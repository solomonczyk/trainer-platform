"""Business logic for the Trainers module."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserTrainerEnrollment
from app.modules.trainers.repository import (
    get_by_slug,
    count_scenarios,
    find_enrollment,
    create_enrollment,
)


async def get_trainer_by_slug(
    db: AsyncSession,
    slug: str,
    user_id: str | None = None,
) -> dict | None:
    """Return trainer data with scenario count and enrollment status, or None."""
    trainer = await get_by_slug(db, slug)
    if not trainer:
        return None

    scenario_count = await count_scenarios(db, trainer.id)

    is_enrolled = False
    if user_id and user_id != "guest":
        enrollment = await find_enrollment(db, user_id, trainer.id)
        is_enrolled = enrollment is not None

    return {
        "id": trainer.id,
        "trainer_product_id": trainer.trainer_product_id,
        "slug": trainer.slug,
        "name": trainer.name,
        "description": trainer.description,
        "product_type": trainer.product_type,
        "target_audience": trainer.target_audience,
        "supported_locales": trainer.supported_locales,
        "default_locale": trainer.default_locale,
        "status": trainer.status,
        "scenario_count": scenario_count,
        "is_enrolled": is_enrolled,
    }


async def enroll_user(
    db: AsyncSession,
    user_id: str,
    trainer_id: str,
) -> tuple[UserTrainerEnrollment, bool]:
    """Create enrollment if it does not exist, or return the existing one.

    Returns (enrollment, was_created).
    """
    existing = await find_enrollment(db, user_id, trainer_id)
    if existing:
        return existing, False

    enrollment = await create_enrollment(db, user_id, trainer_id)
    return enrollment, True
