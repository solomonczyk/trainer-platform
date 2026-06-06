"""Business logic for the Activities module."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ForbiddenError, ValidationError
from app.modules.activities import repository as repo
from app.modules.activities.validators.registry import validate
from app.modules.activities.schemas import (
    ActivityResponse,
    ActivityStartResponse,
    ActivitySubmitResponse,
)
from app.modules.analytics.service import AnalyticsService


class ActivityService:
    """Orchestrates activity operations."""

    @staticmethod
    def _sanitize_payload(payload: dict, activity_type: str) -> dict:
        """Remove correct answers from public payload."""
        sanitized = {k: v for k, v in payload.items() if k != "correct" and k != "pairs"}
        # For matching, keep left/right items but remove pair mappings
        if activity_type == "matching":
            sanitized["left_items"] = payload.get("left_items", [])
            sanitized["right_items"] = payload.get("right_items", [])
        # For fill_blanks, keep template and blanks but remove correct
        if activity_type == "fill_blanks":
            sanitized["template"] = payload.get("template", "")
            sanitized["blanks"] = payload.get("blanks", [])
        return sanitized

    @staticmethod
    def _build_prompt(payload: dict, activity_type: str) -> dict:
        """Build type-specific prompt data without correct answers."""
        if activity_type == "single_choice":
            return {"options": payload.get("options", [])}
        elif activity_type == "multiple_choice":
            return {"options": payload.get("options", [])}
        elif activity_type == "numeric":
            return {"input_type": "number"}
        elif activity_type == "fill_blanks":
            return {
                "template": payload.get("template", ""),
                "blanks": [
                    {"id": b.get("id"), "options": b.get("options")}
                    for b in payload.get("blanks", [])
                ],
            }
        elif activity_type == "matching":
            return {
                "left_items": payload.get("left_items", []),
                "right_items": payload.get("right_items", []),
            }
        return {}

    @classmethod
    async def get_module_activities(
        cls,
        db: AsyncSession,
        trainer_product_id: str,
        module_id: str,
    ) -> list[ActivityResponse]:
        """Get public activity list for a module (no correct answers)."""
        activities = await repo.get_module_activities(db, trainer_product_id, module_id)
        return [
            ActivityResponse(
                activity_id=a.activity_id,
                module_id=a.module_id,
                activity_type=a.activity_type,
                evaluation_mode=a.evaluation_mode,
                difficulty=a.difficulty,
                title_key=a.title_key,
                description_key=a.description_key,
                payload=cls._sanitize_payload(a.payload, a.activity_type),
                order=a.order,
                version=a.version,
            )
            for a in activities
        ]

    @classmethod
    async def start_activity(
        cls,
        db: AsyncSession,
        activity_id: str,
        user_id: str,
    ) -> ActivityStartResponse:
        """Start an activity — return prompt without correct answers."""
        activity = await repo.get_activity_by_id(db, activity_id)
        if not activity:
            raise NotFoundError("Activity", activity_id)

        return ActivityStartResponse(
            activity_id=activity.activity_id,
            activity_type=activity.activity_type,
            title_key=activity.title_key,
            description_key=activity.description_key,
            difficulty=activity.difficulty,
            module_id=activity.module_id,
            prompt=cls._build_prompt(activity.payload, activity.activity_type),
        )

    @classmethod
    async def submit_activity(
        cls,
        db: AsyncSession,
        activity_id: str,
        user_id: str,
        submitted_answer: dict | list | str | int | float,
        idempotency_key: str | None = None,
    ) -> ActivitySubmitResponse:
        """Submit and validate an activity answer."""
        # Resolve activity
        activity = await repo.get_activity_by_id(db, activity_id)
        if not activity:
            raise NotFoundError("Activity", activity_id)

        # Resolve trainer product (activity.trainer_product_id is FK to TrainerProduct.id)
        trainer = await repo.get_trainer_by_db_id(db, activity.trainer_product_id)
        if not trainer:
            raise NotFoundError("TrainerProduct", activity.trainer_product_id)

        # Check enrollment
        from app.db.models import UserTrainerEnrollment
        from sqlalchemy import select

        enrollment_result = await db.execute(
            select(UserTrainerEnrollment).where(
                UserTrainerEnrollment.user_id == user_id,
                UserTrainerEnrollment.trainer_product_id == trainer.id,
                UserTrainerEnrollment.is_active.is_(True),
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if not enrollment:
            raise ForbiddenError("User is not enrolled in this trainer")

        # Idempotency check
        if idempotency_key:
            existing = await repo.find_attempt_by_idempotency(db, user_id, idempotency_key)
            if existing:
                # Get evaluation result via explicit query to avoid greenlet issues
                from app.db.models import DeterministicEvaluation
                from sqlalchemy import select
                eval_result = await db.execute(
                    select(DeterministicEvaluation).where(
                        DeterministicEvaluation.attempt_id == existing.id
                    )
                )
                de = eval_result.scalar_one_or_none()
                if de:
                    return ActivitySubmitResponse(
                        attempt_id=existing.id,
                        activity_id=activity_id,
                        status=de.status,
                        score=de.score,
                        passed=de.passed,
                        feedback=de.feedback,
                        explanation_key=activity.explanation_key,
                        evaluation_mode="deterministic",
                        is_retry=existing.is_retry,
                    )

        # Check if retry
        previous_attempt = await repo.find_existing_attempt(db, user_id, activity_id)
        is_retry = previous_attempt is not None

        # Validate submitted answer
        try:
            result = validate(submitted_answer, activity.payload, activity.activity_type)
        except ValueError as e:
            raise ValidationError(str(e))

        # Create attempt
        attempt = await repo.create_attempt(
            db=db,
            user_id=user_id,
            trainer_product_id=trainer.id,
            activity=activity,
            submitted_answer=submitted_answer,
            idempotency_key=idempotency_key,
            is_retry=is_retry,
            retry_of_attempt_id=previous_attempt.id if previous_attempt else None,
        )

        # Create deterministic evaluation
        await repo.create_deterministic_evaluation(db, attempt.id, result)

        # Update progress
        await repo.update_progress_after_activity(
            db, user_id, trainer.id, result
        )

        # Record analytics event
        await AnalyticsService.record_event(
            db=db,
            user_id=user_id,
            event_type="answer_evaluated",
            session_id=None,
            trainer_slug=trainer.slug,
            scenario_id=activity_id,
            properties={
                "activity_id": activity_id,
                "activity_type": activity.activity_type,
                "status": result["status"],
                "score_bucket": _score_bucket(result["score"]),
                "evaluation_mode": "deterministic",
            },
        )

        return ActivitySubmitResponse(
            attempt_id=attempt.id,
            activity_id=activity_id,
            status=result["status"],
            score=result["score"],
            passed=result["passed"],
            feedback=_safe_feedback(result.get("feedback"), result["status"]),
            explanation_key=activity.explanation_key,
            evaluation_mode="deterministic",
            is_retry=is_retry,
        )


def _score_bucket(score: int) -> str:
    if score >= 100:
        return "100"
    if score >= 80:
        return "80-99"
    if score >= 60:
        return "60-79"
    if score >= 40:
        return "40-59"
    if score >= 1:
        return "1-39"
    return "0"


def _safe_feedback(feedback: dict | None, status: str) -> dict | None:
    """Return safe feedback that doesn't expose correct answers for incorrect results."""
    if feedback is None:
        return None
    # For incorrect results, don't expose the correct answer in feedback
    # The explanation_key will provide the learning content
    if status == "incorrect":
        safe = {k: v for k, v in feedback.items() if k != "correct"}
        if safe and not any(k in safe for k in ("error", "selected", "blank_results", "pair_results")):
            return None
        return safe
    return feedback
