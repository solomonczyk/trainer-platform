"""Pydantic schemas for the Activities module."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional


class ActivityResponse(BaseModel):
    """Public activity response (no correct answers exposed)."""
    model_config = ConfigDict(from_attributes=True)

    activity_id: str
    module_id: str
    activity_type: str
    evaluation_mode: str
    difficulty: str
    title_key: str
    description_key: Optional[str] = None
    payload: dict = Field(default_factory=dict)  # Public payload WITHOUT correct answers
    order: int
    version: str


class ActivityStartResponse(BaseModel):
    """Response when starting an activity (no correct answers)."""
    activity_id: str
    activity_type: str
    title_key: str
    description_key: Optional[str] = None
    difficulty: str
    module_id: str
    prompt: dict  # Type-specific prompt data WITHOUT correct answers


class ActivitySubmitRequest(BaseModel):
    """Request body for submitting an activity answer."""
    activity_id: str
    answer: Any
    idempotency_key: Optional[str] = None


class ActivitySubmitResponse(BaseModel):
    """Response after submitting and validating an activity answer."""
    attempt_id: str
    activity_id: str
    status: str  # correct, partial, incorrect
    score: int
    passed: bool
    feedback: Optional[dict] = None
    explanation_key: str
    evaluation_mode: str
    is_retry: bool = False


class ModuleActivitiesResponse(BaseModel):
    """List of activities in a module (public, no correct answers)."""
    module_id: str
    activities: list[ActivityResponse]
    total_count: int
