"""Pydantic schemas for Exam Blueprint and Blueprint Section entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Blueprint Section
# ---------------------------------------------------------------------------

class BlueprintSectionCreate(BaseModel):
    section_id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    competency_ids: list[str] = []
    weight_percent: float = Field(..., ge=0, le=100)
    minimum_items: int = 0
    maximum_items: int = 0
    difficulty_distribution: Optional[dict] = None
    cognitive_distribution: Optional[dict] = None
    critical_section: bool = False
    sort_order: int = 0


class BlueprintSectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    competency_ids: Optional[list[str]] = None
    weight_percent: Optional[float] = None
    minimum_items: Optional[int] = None
    maximum_items: Optional[int] = None
    difficulty_distribution: Optional[dict] = None
    cognitive_distribution: Optional[dict] = None
    critical_section: Optional[bool] = None
    sort_order: Optional[int] = None


class BlueprintSectionResponse(BaseModel):
    id: str
    blueprint_id: str
    section_id: str
    name: str
    description: Optional[str] = None
    competency_ids: Optional[list] = None
    weight_percent: float
    minimum_items: int
    maximum_items: int
    difficulty_distribution: Optional[dict] = None
    cognitive_distribution: Optional[dict] = None
    critical_section: bool
    sort_order: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Exam Blueprint
# ---------------------------------------------------------------------------

class ExamBlueprintCreate(BaseModel):
    blueprint_id: str = Field(..., max_length=100)
    domain_pack_id: Optional[str] = None
    competency_framework_version: str = Field(..., max_length=100)
    version: str = Field(..., max_length=20)
    exam_duration_minutes: int = 60
    total_items: int = 0
    pass_policy_id: Optional[str] = None
    description: Optional[str] = None
    sections: list[BlueprintSectionCreate] = []
    created_by: str = Field(..., max_length=100)


class ExamBlueprintUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    valid_until: Optional[datetime] = None


class ExamBlueprintResponse(BaseModel):
    id: str
    blueprint_id: str
    domain_pack_id: Optional[str] = None
    competency_framework_version: str
    version: str
    status: str
    exam_duration_minutes: int
    total_items: int
    pass_policy_id: Optional[str] = None
    description: Optional[str] = None
    created_by: str
    sections: list[BlueprintSectionResponse] = []
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExamBlueprintListResponse(BaseModel):
    items: list[ExamBlueprintResponse]
    total: int
    skip: int = 0
    limit: int = 100
