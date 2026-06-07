"""Pydantic schemas for Item Family, Item, and Item Version entities."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Item Family
# ---------------------------------------------------------------------------

class ItemFamilyCreate(BaseModel):
    family_id: str = Field(..., max_length=100)
    domain_pack_id: Optional[str] = None
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    template_schema: Optional[dict] = None
    allowed_item_types: Optional[list[str]] = None
    competency_ids: Optional[list[str]] = None
    variant_policy: Optional[dict] = None
    locale: str = "en-US"
    market: str = "global"
    created_by: str = Field(..., max_length=100)


class ItemFamilyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_schema: Optional[dict] = None
    allowed_item_types: Optional[list[str]] = None
    competency_ids: Optional[list[str]] = None
    variant_policy: Optional[dict] = None
    status: Optional[str] = None


class ItemFamilyResponse(BaseModel):
    id: str
    family_id: str
    domain_pack_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    template_schema: Optional[Any] = None
    allowed_item_types: Optional[list] = None
    competency_ids: Optional[list] = None
    variant_policy: Optional[Any] = None
    status: str
    locale: str
    market: str
    created_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ItemFamilyListResponse(BaseModel):
    items: list[ItemFamilyResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ---------------------------------------------------------------------------
# Item
# ---------------------------------------------------------------------------

class ItemCreate(BaseModel):
    item_id: str = Field(..., max_length=100)
    item_family_id: Optional[str] = None
    domain_pack_id: Optional[str] = None
    item_type: str = Field(..., max_length=50)
    prompt: Optional[dict] = None
    response_contract: Optional[dict] = None
    answer_key: Optional[dict] = None
    rubric_id: Optional[str] = None
    competency_ids: Optional[list[str]] = None
    knowledge_source_refs: Optional[list[str]] = None
    difficulty_target: str = "medium"
    locale: str = "en-US"
    market: str = "global"
    created_by: str = Field(..., max_length=100)


class ItemUpdate(BaseModel):
    prompt: Optional[dict] = None
    response_contract: Optional[dict] = None
    answer_key: Optional[dict] = None
    rubric_id: Optional[str] = None
    competency_ids: Optional[list[str]] = None
    knowledge_source_refs: Optional[list[str]] = None
    difficulty_target: Optional[str] = None
    difficulty_measured: Optional[float] = None
    discrimination_measured: Optional[float] = None
    status: Optional[str] = None
    valid_until: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None


class ItemResponse(BaseModel):
    id: str
    item_id: str
    item_family_id: Optional[str] = None
    domain_pack_id: Optional[str] = None
    version: int
    item_type: str
    prompt: Optional[Any] = None
    response_contract: Optional[Any] = None
    answer_key: Optional[Any] = None
    rubric_id: Optional[str] = None
    competency_ids: Optional[list] = None
    knowledge_source_refs: Optional[list] = None
    difficulty_target: str
    difficulty_measured: Optional[float] = None
    discrimination_measured: Optional[float] = None
    status: str
    locale: str
    market: str
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_by: str
    reviewed_by: Optional[str] = None
    exposure_count: int
    compromise_risk: str
    created_at: Optional[datetime] = None
    versions: list[ItemVersionResponse] = []

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ---------------------------------------------------------------------------
# Item Version
# ---------------------------------------------------------------------------

class ItemVersionResponse(BaseModel):
    id: str
    item_id: str
    version: int
    snapshot: Any
    change_reason: Optional[str] = None
    created_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
