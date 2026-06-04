"""Database repository for evaluations module.

Provides data access methods for attempts, scenarios, rubrics, evaluations,
and evaluation criterion results using SQLAlchemy async sessions.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.db.models import (
    Attempt,
    Evaluation,
    EvaluationCriterionResult,
    Rubric,
    RubricCriterion,
    Scenario,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Attempts
# ---------------------------------------------------------------------------


async def get_attempt_by_id(
    db: AsyncSession,
    attempt_id: str,
) -> Optional[Attempt]:
    """Fetch an attempt by its primary key, including its scenario.

    Args:
        db: Database session.
        attempt_id: The attempt UUID string.

    Returns:
        The :class:`Attempt` instance, or ``None`` if not found.
    """
    stmt = (
        select(Attempt)
        .where(Attempt.id == attempt_id)
        .options(selectinload(Attempt.scenario))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


async def get_scenario_by_id(
    db: AsyncSession,
    scenario_id: str,
) -> Optional[Scenario]:
    """Fetch a scenario by its primary key.

    Args:
        db: Database session.
        scenario_id: The scenario UUID string.

    Returns:
        The :class:`Scenario` instance, or ``None`` if not found.
    """
    stmt = select(Scenario).where(Scenario.id == scenario_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Rubrics
# ---------------------------------------------------------------------------


async def get_rubric_by_scenario(
    db: AsyncSession,
    scenario_id: str,
) -> Optional[Rubric]:
    """Fetch a rubric associated with a scenario, including its criteria.

    Args:
        db: Database session.
        scenario_id: The scenario UUID string.

    Returns:
        The :class:`Rubric` instance with loaded criteria, or ``None``.
    """
    stmt = (
        select(Rubric)
        .where(Rubric.scenario_id == scenario_id)
        .options(selectinload(Rubric.criteria))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_rubric_by_rubric_id(
    db: AsyncSession,
    rubric_id: str,
) -> Optional[Rubric]:
    """Fetch a rubric by its application-level rubric_id string.

    Args:
        db: Database session.
        rubric_id: The business-logic rubric identifier (e.g. ``"qa_interview_v1"``).

    Returns:
        The :class:`Rubric` instance with loaded criteria, or ``None``.
    """
    stmt = (
        select(Rubric)
        .where(Rubric.rubric_id == rubric_id)
        .options(selectinload(Rubric.criteria))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def _build_rubric_dict(rubric: Rubric) -> dict:
    """Convert a :class:`Rubric` ORM object to the dictionary format expected
    by the AI gateway.

    Returns:
        A dict with ``pass_score``, ``critical_fail_enabled``, and ``criteria``.
    """
    criteria_list = []
    for c in rubric.criteria:
        criteria_list.append({
            "criterion_id": c.criterion_id,
            "id": c.criterion_id,
            "name": c.name,
            "weight": c.weight,
            "evidence_required": c.evidence_required,
        })

    return {
        "pass_score": rubric.pass_score,
        "critical_fail_enabled": rubric.critical_fail_enabled,
        "criteria": criteria_list,
    }


# ---------------------------------------------------------------------------
# Evaluations
# ---------------------------------------------------------------------------


async def save_evaluation(
    db: AsyncSession,
    attempt_id: str,
    overall_score: int,
    passed: bool,
    strengths: Optional[list[str]] = None,
    weak_points: Optional[list[str]] = None,
    critical_errors: Optional[list[str]] = None,
    next_recommendation: Optional[dict] = None,
    confidence: float = 0.0,
    ai_model_used: Optional[str] = None,
    ai_cost_usd: Optional[float] = None,
    ai_latency_ms: Optional[int] = None,
    raw_ai_output: Optional[dict] = None,
    validation_status: str = "validated",
) -> Evaluation:
    """Create and persist a new :class:`Evaluation` record.

    Args:
        db: Database session.
        attempt_id: FK to the attempt being evaluated.
        overall_score: Final score 0-100.
        passed: Whether the attempt passed.
        strengths: List of identified strengths.
        weak_points: List of identified weaknesses.
        critical_errors: List of critical error codes.
        next_recommendation: Dict with action/suggestion/target_score.
        confidence: AI confidence score 0.0-1.0.
        ai_model_used: Model name used for evaluation.
        ai_cost_usd: Estimated cost of the AI call.
        ai_latency_ms: Latency of the AI call in milliseconds.
        raw_ai_output: Raw AI provider response.
        validation_status: Status of validation (validated, partial, fallback, failed).

    Returns:
        The newly created :class:`Evaluation` instance.
    """
    evaluation = Evaluation(
        attempt_id=attempt_id,
        overall_score=overall_score,
        passed=passed,
        strengths=strengths or [],
        weak_points=weak_points or [],
        critical_errors=critical_errors or [],
        next_recommendation=next_recommendation,
        confidence=confidence,
        ai_model_used=ai_model_used,
        ai_cost_usd=ai_cost_usd,
        ai_latency_ms=ai_latency_ms,
        raw_ai_output=raw_ai_output,
        validation_status=validation_status,
    )
    db.add(evaluation)
    await db.flush()
    logger.info(
        "Evaluation saved",
        evaluation_id=evaluation.id,
        attempt_id=attempt_id,
        overall_score=overall_score,
        passed=passed,
    )
    return evaluation


async def save_criterion_result(
    db: AsyncSession,
    evaluation_id: str,
    criterion_id: str,
    score: int,
    evidence: Optional[str] = None,
    comment: Optional[str] = None,
    improvement: Optional[str] = None,
) -> EvaluationCriterionResult:
    """Create and persist a single criterion result record.

    Args:
        db: Database session.
        evaluation_id: FK to the parent evaluation.
        criterion_id: The rubric criterion identifier.
        score: Score 0-100.
        evidence: Evidence text from the AI.
        comment: Optional comment.
        improvement: Improvement suggestion.

    Returns:
        The newly created :class:`EvaluationCriterionResult` instance.
    """
    result = EvaluationCriterionResult(
        evaluation_id=evaluation_id,
        criterion_id=criterion_id,
        score=score,
        evidence=evidence or "",
        comment=comment or "",
        improvement=improvement or "",
    )
    db.add(result)
    await db.flush()
    return result


async def get_evaluation_by_attempt(
    db: AsyncSession,
    attempt_id: str,
) -> Optional[Evaluation]:
    """Fetch the evaluation for a given attempt, including criterion results.

    Args:
        db: Database session.
        attempt_id: The attempt UUID string.

    Returns:
        The :class:`Evaluation` with loaded criteria results, or ``None``.
    """
    stmt = (
        select(Evaluation)
        .where(Evaluation.attempt_id == attempt_id)
        .options(selectinload(Evaluation.criteria_results))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_attempt_status(
    db: AsyncSession,
    attempt_id: str,
    status: str,
) -> Optional[Attempt]:
    """Update the status of an attempt.

    Args:
        db: Database session.
        attempt_id: The attempt UUID string.
        status: New status value (e.g. ``"evaluated"``, ``"failed"``).

    Returns:
        The updated :class:`Attempt` instance, or ``None`` if not found.
    """
    attempt = await get_attempt_by_id(db, attempt_id)
    if attempt is None:
        return None
    attempt.status = status
    await db.flush()
    return attempt
