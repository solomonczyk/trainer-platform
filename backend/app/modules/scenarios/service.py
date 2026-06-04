"""Business logic for scenario operations."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Scenario
from app.modules.scenarios import repository as scenarios_repo


async def get_scenarios_for_trainer(
    db: AsyncSession, trainer_id: str
) -> list[Scenario]:
    """Return all scenarios for a given trainer product (by DB primary key)."""
    return await scenarios_repo.list_by_trainer_id(db, trainer_id=trainer_id)


async def get_scenario_by_scenario_id(
    db: AsyncSession, scenario_id: str
) -> Scenario | None:
    """Return a single scenario by its business scenario_id string."""
    return await scenarios_repo.get_by_scenario_id(db, scenario_id=scenario_id)
