"""Pydantic schemas for Domain Pack entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DomainPackCreate(BaseModel):
    domain_pack_id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    version: str = Field(..., max_length=20)
    locale: str = "en-US"
    market: str = "global"
    description: Optional[str] = None
    competency_framework_id: Optional[str] = None
    blueprint_ids: Optional[list[str]] = None
    knowledge_source_ids: Optional[list[str]] = None
    item_bank_policy_id: Optional[str] = None
    scoring_policy_id: Optional[str] = None
    pass_policy_id: Optional[str] = None
    rubric_ids: Optional[list[str]] = None
    supported_modes: Optional[list[str]] = None
    created_by: str = Field(..., max_length=100)


class DomainPackUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    competency_framework_id: Optional[str] = None
    blueprint_ids: Optional[list[str]] = None
    knowledge_source_ids: Optional[list[str]] = None
    rubric_ids: Optional[list[str]] = None
    supported_modes: Optional[list[str]] = None
    status: Optional[str] = None


class DomainPackResponse(BaseModel):
    id: str
    domain_pack_id: str
    name: str
    version: str
    locale: str
    market: str
    status: str
    description: Optional[str] = None
    competency_framework_id: Optional[str] = None
    blueprint_ids: Optional[list] = None
    knowledge_source_ids: Optional[list] = None
    item_bank_policy_id: Optional[str] = None
    scoring_policy_id: Optional[str] = None
    pass_policy_id: Optional[str] = None
    rubric_ids: Optional[list] = None
    supported_modes: Optional[list] = None
    created_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DomainPackListResponse(BaseModel):
    items: list[DomainPackResponse]
    total: int
    skip: int = 0
    limit: int = 100
