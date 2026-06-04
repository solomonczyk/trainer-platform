"""Database queries for the Trainers module."""
from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TrainerProduct, Scenario, UserTrainerEnrollment


async def get_by_slug(db: AsyncSession, slug: str) -> TrainerProduct | None:
    """Return a trainer product by slug, or None."""
    result = await db.execute(
        select(TrainerProduct).where(TrainerProduct.slug == slug)
    )
    return result.scalar_one_or_none()


async def count_scenarios(db: AsyncSession, trainer_id: str) -> int:
    """Count scenarios linked to a trainer product."""
    result = await db.execute(
        select(func.count(Scenario.id))
        .where(Scenario.trainer_product_id == trainer_id)
    )
    return result.scalar() or 0


async def find_enrollment(
    db: AsyncSession,
    user_id: str,
    trainer_id: str,
) -> UserTrainerEnrollment | None:
    """Return an existing enrollment for a user + trainer, or None."""
    result = await db.execute(
        select(UserTrainerEnrollment)
        .where(UserTrainerEnrollment.user_id == user_id)
        .where(UserTrainerEnrollment.trainer_product_id == trainer_id)
    )
    return result.scalar_one_or_none()


async def create_enrollment(
    db: AsyncSession,
    user_id: str,
    trainer_id: str,
) -> UserTrainerEnrollment:
    """Create a new user-trainer enrollment."""
    enrollment = UserTrainerEnrollment(
        user_id=user_id,
        trainer_product_id=trainer_id,
    )
    db.add(enrollment)
    await db.flush()
    return enrollment
