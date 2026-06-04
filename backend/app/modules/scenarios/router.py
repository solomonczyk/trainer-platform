"""REST API router for scenario endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.models import Scenario, TrainerProduct
from app.db.session import get_db
from app.modules.scenarios import service as scenarios_service
from app.modules.scenarios.schemas import ScenarioDetailResponse, ScenarioSummaryResponse

router = APIRouter()


@router.get(
    "/trainers/{trainer_slug}/scenarios",
    response_model=List[ScenarioSummaryResponse],
    summary="List scenarios for a trainer product",
)
async def list_scenarios_for_trainer(
    trainer_slug: str,
    db: AsyncSession = Depends(get_db),
) -> list[ScenarioSummaryResponse]:
    """Return all scenarios published under a trainer product identified by its slug."""
    # Resolve trainer slug to DB primary key
    result = await db.execute(
        select(TrainerProduct).where(TrainerProduct.slug == trainer_slug)
    )
    trainer = result.scalar_one_or_none()
    if not trainer:
        raise NotFoundError(entity="TrainerProduct", entity_id=trainer_slug)

    scenarios = await scenarios_service.get_scenarios_for_trainer(db, trainer_id=trainer.id)
    return [ScenarioSummaryResponse.model_validate(s) for s in scenarios]


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetailResponse,
    summary="Get scenario detail by scenario_id",
)
async def get_scenario_detail(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
) -> ScenarioDetailResponse:
    """Return full detail for a single scenario by its business scenario_id string."""
    scenario = await scenarios_service.get_scenario_by_scenario_id(db, scenario_id=scenario_id)
    if not scenario:
        raise NotFoundError(entity="Scenario", entity_id=scenario_id)

    return ScenarioDetailResponse.model_validate(scenario)
