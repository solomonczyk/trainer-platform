"""Database queries for the Activities module."""
from __future__ import annotations

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Activity, Attempt, DeterministicEvaluation, TrainerProgress


async def get_activity_by_id(db: AsyncSession, activity_id: str) -> Activity | None:
    """Return an activity by its business activity_id, or None."""
    result = await db.execute(
        select(Activity).where(Activity.activity_id == activity_id)
    )
    return result.scalar_one_or_none()


async def get_activity_by_db_id(db: AsyncSession, db_id: str) -> Activity | None:
    """Return an activity by its primary key, or None."""
    return await db.get(Activity, db_id)


async def get_module_activities(
    db: AsyncSession,
    trainer_product_id: str,
    module_id: str,
) -> list[Activity]:
    """Return activities for a module, ordered."""
    result = await db.execute(
        select(Activity)
        .where(
            Activity.trainer_product_id == trainer_product_id,
            Activity.module_id == module_id,
        )
        .order_by(Activity.order)
    )
    return list(result.scalars().all())


async def count_module_activities(
    db: AsyncSession,
    trainer_product_id: str,
    module_id: str,
) -> int:
    """Count activities for a module."""
    result = await db.execute(
        select(func.count(Activity.id))
        .where(
            Activity.trainer_product_id == trainer_product_id,
            Activity.module_id == module_id,
        )
    )
    return result.scalar() or 0


async def count_total_activities(
    db: AsyncSession,
    trainer_product_id: str,
) -> int:
    """Count total activities for a trainer product."""
    result = await db.execute(
        select(func.count(Activity.id))
        .where(Activity.trainer_product_id == trainer_product_id)
    )
    return result.scalar() or 0


async def find_existing_attempt(
    db: AsyncSession,
    user_id: str,
    activity_id: str,
) -> Attempt | None:
    """Find an existing attempt for a user + activity combination."""
    from app.db.models import Activity as ActivityModel

    result = await db.execute(
        select(Attempt)
        .join(ActivityModel, Attempt.activity_id == ActivityModel.id)
        .where(
            Attempt.user_id == user_id,
            ActivityModel.activity_id == activity_id,
        )
        .order_by(Attempt.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def find_attempt_by_idempotency(
    db: AsyncSession,
    user_id: str,
    idempotency_key: str,
) -> Attempt | None:
    """Find an attempt by idempotency key."""
    result = await db.execute(
        select(Attempt)
        .where(
            Attempt.user_id == user_id,
            Attempt.idempotency_key == idempotency_key,
        )
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_attempt(
    db: AsyncSession,
    user_id: str,
    trainer_product_id: str,
    activity: Activity,
    submitted_answer: dict,
    idempotency_key: str | None = None,
    is_retry: bool = False,
    retry_of_attempt_id: str | None = None,
) -> Attempt:
    """Create a new attempt record for an activity submission."""
    attempt = Attempt(
        user_id=user_id,
        trainer_product_id=trainer_product_id,
        scenario_id=None,  # Activity-based attempts don't use scenarios
        activity_id=activity.id,
        activity_type=activity.activity_type,
        evaluation_mode=activity.evaluation_mode,
        submitted_answer=submitted_answer,
        idempotency_key=idempotency_key,
        answer_text=str(submitted_answer) if submitted_answer else None,
        status="completed",
        is_retry=is_retry,
        retry_of_attempt_id=retry_of_attempt_id,
        completed_at=func.now(),
    )
    db.add(attempt)
    await db.flush()
    return attempt


async def create_deterministic_evaluation(
    db: AsyncSession,
    attempt_id: str,
    result: dict,
) -> DeterministicEvaluation:
    """Create a deterministic evaluation record."""
    evaluation = DeterministicEvaluation(
        attempt_id=attempt_id,
        status=result["status"],
        score=result["score"],
        passed=result["passed"],
        feedback=result.get("feedback"),
        evaluation_mode=result.get("evaluation_mode", "deterministic"),
        validation_status=result.get("validation_status", "validated"),
    )
    db.add(evaluation)
    await db.flush()
    return evaluation


async def update_progress_after_activity(
    db: AsyncSession,
    user_id: str,
    trainer_id: str,
    activity_result: dict,
) -> TrainerProgress:
    """Update trainer progress after a deterministic activity attempt."""
    progress = await _get_or_create_progress(db, user_id, trainer_id)

    progress.total_attempts += 1
    if activity_result.get("passed", False):
        progress.completed_scenarios += 1

    # Rolling average score
    old_total = progress.average_score * (progress.total_attempts - 1)
    progress.average_score = round(
        (old_total + activity_result.get("score", 0)) / progress.total_attempts, 2
    )

    progress.readiness_status = _calculate_readiness(
        progress.average_score,
        progress.completed_scenarios,
        progress.total_attempts,
    )

    await db.flush()
    return progress


async def _get_or_create_progress(
    db: AsyncSession,
    user_id: str,
    trainer_id: str,
) -> TrainerProgress:
    """Get existing progress or create a new one."""
    from app.modules.progress.repository import ProgressRepository

    progress = await ProgressRepository.get_by_user_and_trainer(db, user_id, trainer_id)
    if progress is None:
        progress = await ProgressRepository.create_progress(db, user_id, trainer_id)
    return progress


def _calculate_readiness(average_score: float, completed: int, total: int) -> str:
    """Derive a readiness label from aggregated metrics."""
    if total == 0:
        return "started"
    if average_score >= 85 and completed >= 5:
        return "strong"
    if average_score >= 70 and completed >= 3:
        return "ready"
    if average_score >= 50 and completed >= 1:
        return "developing"
    return "started"


async def get_trainer_by_db_id(
    db: AsyncSession,
    trainer_db_id: str,
):
    """Get a trainer product by its primary key (UUID)."""
    from app.db.models import TrainerProduct

    return await db.get(TrainerProduct, trainer_db_id)


async def get_activity_count_by_type(
    db: AsyncSession,
    trainer_product_id: str,
) -> dict[str, int]:
    """Count activities by type for a trainer product."""
    result = await db.execute(
        select(
            Activity.activity_type,
            func.count(Activity.id).label("count"),
        )
        .where(Activity.trainer_product_id == trainer_product_id)
        .group_by(Activity.activity_type)
    )
    return {row.activity_type: row.count for row in result.all()}
