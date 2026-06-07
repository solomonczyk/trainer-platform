"""Pydantic schemas for Rubric and Rubric Criterion entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Rubric Criterion
# ---------------------------------------------------------------------------

class RubricCriterionCreate(BaseModel):
    criterion_id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    weight: float = Field(..., ge=0)
    levels: Optional[dict] = None
    sort_order: int = 0


class RubricCriterionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    levels: Optional[dict] = None
    sort_order: Optional[int] = None


class RubricCriterionResponse(BaseModel):
    id: str
    rubric_id: str
    criterion_id: str
    name: str
    description: Optional[str] = None
    weight: float
    levels: Optional[dict] = None
    sort_order: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Rubric
# ---------------------------------------------------------------------------

class RubricCreate(BaseModel):
    rubric_id: str = Field(..., max_length=100)
    version: str = Field(..., max_length=20)
    domain_pack_id: Optional[str] = None
    competency_ids: Optional[list[str]] = None
    description: Optional[str] = None
    validation_dataset_ref: Optional[str] = None
    criteria: list[RubricCriterionCreate] = []
    created_by: str = Field(..., max_length=100)


class RubricUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None


class RubricResponse(BaseModel):
    id: str
    rubric_id: str
    version: str
    domain_pack_id: Optional[str] = None
    competency_ids: Optional[list] = None
    status: str
    description: Optional[str] = None
    total_weight: float
    validation_dataset_ref: Optional[str] = None
    created_by: str
    criteria: list[RubricCriterionResponse] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RubricListResponse(BaseModel):
    items: list[RubricResponse]
    total: int
    skip: int = 0
    limit: int = 100
