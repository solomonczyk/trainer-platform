"""Business logic for the evaluations module.

Coordinates between the HTTP layer, the database repository, and the
AI Gateway service to evaluate user attempts and persist results.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_gateway.schemas import (
    EvaluationGatewayRequest,
)
from app.ai_gateway.service import AIGatewayService
from app.core.errors import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.modules.evaluations import repository as repo
from app.modules.evaluations.schemas import EvaluationResponse

logger = get_logger(__name__)


class EvaluationService:
    """Service layer for the evaluations module.

    Wraps the core business logic so the router stays thin.
    """

    def __init__(self) -> None:
        self._ai_gateway = AIGatewayService()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def evaluate_attempt(
        self,
        db: AsyncSession,
        attempt_id: str,
        locale: str = "ru-RU",
    ) -> EvaluationResponse:
        """Evaluate a user attempt using the AI Gateway.

        Workflow:
        1. Load the attempt and associated scenario from the database.
        2. Load the rubric attached to the scenario.
        3. Build an :class:`EvaluationGatewayRequest` and call the AI Gateway.
        4. Persist the evaluation and criterion results.
        5. Update the attempt status to ``"evaluated"``.
        6. Return the evaluation response.

        Args:
            db: Database session.
            attempt_id: UUID of the attempt to evaluate.
            locale: Evaluation locale (``"ru-RU"`` or ``"en-US"``).

        Returns:
            Fully populated :class:`EvaluationResponse`.

        Raises:
            NotFoundError: If the attempt or scenario is not found.
            ValidationError: If the attempt has no answer or is already evaluated.
        """
        # 1. Load the attempt
        attempt = await repo.get_attempt_by_id(db, attempt_id)
        if attempt is None:
            raise NotFoundError(entity="Attempt", entity_id=attempt_id)

        # Validate attempt state
        if attempt.status == "evaluated":
            raise ValidationError(
                message="Attempt has already been evaluated",
                details={"attempt_id": attempt_id, "status": attempt.status},
            )
        if attempt.status == "evaluating":
            raise ValidationError(
                message="Attempt is currently being evaluated",
                details={"attempt_id": attempt_id, "status": attempt.status},
            )

        answer = attempt.answer_text
        if not answer or not answer.strip():
            raise ValidationError(
                message="Attempt has no answer text to evaluate",
                details={"attempt_id": attempt_id},
            )

        scenario = attempt.scenario
        if scenario is None:
            raise NotFoundError(entity="Scenario", entity_id=attempt.scenario_id)

        # 2. Load the rubric
        rubric_dict: dict = {"pass_score": 70, "critical_fail_enabled": True, "criteria": []}
        rubric = await repo.get_rubric_by_scenario(db, scenario.id)
        if rubric is not None:
            rubric_dict = repo._build_rubric_dict(rubric)
        else:
            logger.warning(
                "No rubric found for scenario, using default",
                scenario_id=scenario.id,
            )

        # Update attempt status to evaluating
        await repo.update_attempt_status(db, attempt_id, "evaluating")

        # 3. Call the AI Gateway
        gateway_request = EvaluationGatewayRequest(
            attempt_id=attempt_id,
            scenario_id=scenario.id,
            user_answer=answer,
            rubric=rubric_dict,
            locale=locale,
            user_role=scenario.user_role or "candidate",
            ai_role=scenario.ai_role or "interviewer",
        )

        logger.info(
            "Calling AI Gateway for evaluation",
            attempt_id=attempt_id,
            scenario_id=scenario.id,
            locale=locale,
        )

        gateway_result = await self._ai_gateway.evaluate_attempt(gateway_request)

        # 4. Persist the evaluation
        validated = gateway_result.validated_output

        if validated is None:
            # Gateway call failed entirely
            await repo.update_attempt_status(db, attempt_id, "failed")
            raise ValidationError(
                message=f"AI evaluation failed: {gateway_result.error_message}",
                details={
                    "attempt_id": attempt_id,
                    "provider": gateway_result.provider,
                    "validation_status": gateway_result.validation_status,
                },
            )

        evaluation = await repo.save_evaluation(
            db=db,
            attempt_id=attempt_id,
            overall_score=validated.overall_score,
            passed=validated.passed,
            strengths=validated.strengths,
            weak_points=validated.weak_points,
            critical_errors=validated.critical_errors,
            next_recommendation=validated.next_recommendation,
            confidence=validated.confidence,
            ai_model_used=gateway_result.model or "",
            ai_cost_usd=gateway_result.cost_usd,
            ai_latency_ms=gateway_result.latency_ms,
            raw_ai_output=gateway_result.raw_output,
            validation_status=gateway_result.validation_status,
        )

        # Save per-criterion results
        for cr in validated.criteria:
            await repo.save_criterion_result(
                db=db,
                evaluation_id=evaluation.id,
                criterion_id=cr.criterion_id,
                score=cr.score,
                evidence=cr.evidence,
                comment=cr.comment,
                improvement=cr.improvement,
            )

        # 5. Update attempt status
        final_status = "evaluated" if gateway_result.success else "failed"
        await repo.update_attempt_status(db, attempt_id, final_status)

        # 6. Build and return response
        return self._evaluation_to_response(evaluation)

    async def get_evaluation(
        self,
        db: AsyncSession,
        attempt_id: str,
    ) -> EvaluationResponse:
        """Retrieve the evaluation result for an attempt.

        Args:
            db: Database session.
            attempt_id: UUID of the attempt.

        Returns:
            Fully populated :class:`EvaluationResponse`.

        Raises:
            NotFoundError: If the attempt or its evaluation is not found.
        """
        attempt = await repo.get_attempt_by_id(db, attempt_id)
        if attempt is None:
            raise NotFoundError(entity="Attempt", entity_id=attempt_id)

        evaluation = await repo.get_evaluation_by_attempt(db, attempt_id)
        if evaluation is None:
            raise NotFoundError(
                entity="Evaluation",
                entity_id=f"for attempt {attempt_id}",
            )

        return self._evaluation_to_response(evaluation)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evaluation_to_response(self, evaluation) -> EvaluationResponse:
        """Convert an :class:`Evaluation` ORM instance to an :class:`EvaluationResponse`."""
        criteria = []
        for cr in evaluation.criteria_results or []:
            criteria.append({
                "criterion_id": cr.criterion_id,
                "score": cr.score,
                "evidence": cr.evidence or "",
                "comment": cr.comment or "",
                "improvement": cr.improvement or "",
            })

        return EvaluationResponse(
            id=evaluation.id,
            attempt_id=evaluation.attempt_id,
            overall_score=evaluation.overall_score,
            passed=evaluation.passed,
            criteria=criteria,
            strengths=evaluation.strengths or [],
            weak_points=evaluation.weak_points or [],
            critical_errors=evaluation.critical_errors or [],
            next_recommendation=evaluation.next_recommendation,
            confidence=evaluation.confidence or 0.0,
            ai_model_used=evaluation.ai_model_used,
            ai_cost_usd=evaluation.ai_cost_usd,
            ai_latency_ms=evaluation.ai_latency_ms,
            validation_status=evaluation.validation_status or "validated",
            created_at=evaluation.created_at,
            updated_at=evaluation.updated_at,
        )
