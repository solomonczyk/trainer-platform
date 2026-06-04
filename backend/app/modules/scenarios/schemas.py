"""Pydantic schemas for scenario endpoints."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ScenarioSummaryResponse(BaseModel):
    """Lightweight scenario summary returned in list endpoints."""

    id: str
    scenario_id: str
    title_key: str
    goal_key: str
    difficulty: str
    estimated_duration_minutes: int
    track: Optional[str] = None
    module: Optional[str] = None

    model_config = {"from_attributes": True}


class ScenarioDetailResponse(BaseModel):
    """Full scenario detail returned for a single scenario."""

    id: str
    scenario_id: str
    title_key: str
    goal_key: str
    trainer_product_id: str
    difficulty: str
    estimated_duration_minutes: int
    target_skills: Optional[list[Any]] = None
    user_role: str
    ai_role: str
    steps: Optional[list[Any]] = None
    hints: Optional[list[Any]] = None
    status: str

    model_config = {"from_attributes": True}
