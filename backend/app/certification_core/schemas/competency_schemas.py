"""Pydantic schemas for Competency Framework and Competency entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Competency (node within a framework)
# ---------------------------------------------------------------------------

class CompetencyCreate(BaseModel):
    competency_id: str = Field(..., max_length=100, description="Unique ID within framework")
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    cognitive_levels: Optional[list[str]] = None
    critical: bool = False
    weight: float = 0.0
    sort_order: int = 0


class CompetencyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    cognitive_levels: Optional[list[str]] = None
    critical: Optional[bool] = None
    weight: Optional[float] = None
    sort_order: Optional[int] = None


class CompetencyResponse(BaseModel):
    id: str
    competency_id: str
    framework_id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    cognitive_levels: Optional[list] = None
    critical: bool
    weight: float
    sort_order: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Competency Framework
# ---------------------------------------------------------------------------

class CompetencyFrameworkCreate(BaseModel):
    framework_id: str = Field(..., max_length=100)
    domain_pack_id: Optional[str] = None
    version: str = Field(..., max_length=20)
    locale: str = "en-US"
    market: str = "global"
    description: Optional[str] = None
    competencies: list[CompetencyCreate] = []
    created_by: str = Field(..., max_length=100)


class CompetencyFrameworkUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    valid_until: Optional[datetime] = None


class CompetencyFrameworkResponse(BaseModel):
    id: str
    framework_id: str
    domain_pack_id: Optional[str] = None
    version: str
    status: str
    locale: str
    market: str
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_by: str
    competencies: list[CompetencyResponse] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CompetencyFrameworkListResponse(BaseModel):
    items: list[CompetencyFrameworkResponse]
    total: int
    skip: int = 0
    limit: int = 100
