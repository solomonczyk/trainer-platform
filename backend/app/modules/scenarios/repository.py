"""Database access layer for Scenario models."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Scenario


async def list_by_trainer_id(db: AsyncSession, trainer_id: str) -> list[Scenario]:
    """Return all scenarios belonging to a trainer product (by DB primary key)."""
    result = await db.execute(
        select(Scenario)
        .where(Scenario.trainer_product_id == trainer_id)
        .order_by(Scenario.created_at)
    )
    return list(result.scalars().all())


async def get_by_scenario_id(db: AsyncSession, scenario_id: str) -> Scenario | None:
    """Return a single scenario by its business identifier (scenario_id column)."""
    result = await db.execute(
        select(Scenario).where(Scenario.scenario_id == scenario_id)
    )
    return result.scalar_one_or_none()
