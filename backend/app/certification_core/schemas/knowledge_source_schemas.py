"""Pydantic schemas for Knowledge Source entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KnowledgeSourceCreate(BaseModel):
    source_id: str = Field(..., max_length=100)
    source_type: str = Field(default="standard", max_length=50)
    title: str = Field(..., max_length=500)
    publisher: Optional[str] = None
    source_url: Optional[str] = None
    jurisdiction: Optional[str] = None
    locale: str = "en-US"
    market: str = "global"
    version: str = Field(..., max_length=50)
    content_hash: Optional[str] = None
    reviewed_by: Optional[str] = None
    superseded_by: Optional[str] = None
    change_category: Optional[str] = None
    notes: Optional[str] = None
    created_by: str = Field(..., max_length=100)


class KnowledgeSourceUpdate(BaseModel):
    title: Optional[str] = None
    publisher: Optional[str] = None
    source_url: Optional[str] = None
    content_hash: Optional[str] = None
    status: Optional[str] = None
    valid_until: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    superseded_by: Optional[str] = None
    change_category: Optional[str] = None
    notes: Optional[str] = None


class KnowledgeSourceResponse(BaseModel):
    id: str
    source_id: str
    source_type: str
    title: str
    publisher: Optional[str] = None
    source_url: Optional[str] = None
    jurisdiction: Optional[str] = None
    locale: str
    market: str
    version: str
    content_hash: Optional[str] = None
    status: str
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    superseded_by: Optional[str] = None
    change_category: Optional[str] = None
    notes: Optional[str] = None
    created_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class KnowledgeSourceListResponse(BaseModel):
    items: list[KnowledgeSourceResponse]
    total: int
    skip: int = 0
    limit: int = 100
