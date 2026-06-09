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
from app.modules.scenarios.scenario_quest_mapping import (
    SCENARIO_QUEST_MAPPING,
    get_scenario_mapping,
    is_scenario_hidden,
)

router = APIRouter()


@router.get(
    "/trainers/{trainer_slug}/scenarios",
    response_model=List[ScenarioSummaryResponse],
    summary="List scenarios for a trainer product",
)
async def list_scenarios_for_trainer(
    trainer_slug: str,
    db: AsyncSession = Depends(get_db),
    include_hidden: bool = False,
) -> list[ScenarioSummaryResponse]:
    """Return scenarios published under a trainer product.

    By default, scenarios that have been hidden (HIDE_TEMPORARILY) are excluded
    from the listing. Pass `include_hidden=true` to include them.
    """
    result = await db.execute(
        select(TrainerProduct).where(TrainerProduct.slug == trainer_slug)
    )
    trainer = result.scalar_one_or_none()
    if not trainer:
        raise NotFoundError(entity="TrainerProduct", entity_id=trainer_slug)

    scenarios = await scenarios_service.get_scenarios_for_trainer(db, trainer_id=trainer.id)
    result_list = []
    for s in scenarios:
        scenario_id = s.scenario_id or s.id
        if not include_hidden and is_scenario_hidden(scenario_id):
            continue
        result_list.append(ScenarioSummaryResponse.model_validate(s))
    return result_list


@router.get(
    "/scenarios/mappings",
    summary="List all scenario-to-quest mappings",
)
async def list_scenario_mappings() -> dict:
    """Return all scenario-to-quest mappings for the platform."""
    result = {}
    for scenario_id, mapping in SCENARIO_QUEST_MAPPING.items():
        result[scenario_id] = {
            "quest_id": mapping.get("quest_id"),
            "mode": mapping.get("mode", "UNMAPPED"),
            "trainer_slug": mapping.get("trainer_slug"),
            "reason": mapping.get("reason", ""),
        }
    return {"mappings": result}


@router.get(
    "/scenarios/{scenario_id}/mapping",
    summary="Get scenario-to-quest mapping for a legacy scenario",
)
async def get_scenario_mapping_endpoint(
    scenario_id: str,
) -> dict:
    """Return the quest mapping for a legacy scenario ID.

    Used by the frontend to redirect legacy scenario routes to quest routes
    or render the quest engine on the old route.
    """
    mapping = get_scenario_mapping(scenario_id)
    if mapping is None:
        return {
            "scenario_id": scenario_id,
            "mode": "UNMAPPED",
            "quest_id": None,
            "trainer_slug": None,
        }
    return {
        "scenario_id": scenario_id,
        "quest_id": mapping.get("quest_id"),
        "mode": mapping.get("mode", "UNMAPPED"),
        "trainer_slug": mapping.get("trainer_slug"),
        "reason": mapping.get("reason", ""),
    }


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
