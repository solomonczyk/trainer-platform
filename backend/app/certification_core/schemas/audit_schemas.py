"""Pydantic schemas for Audit Event entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AuditEventResponse(BaseModel):
    id: str
    audit_event_id: str
    entity_type: str
    entity_id: str
    entity_version: Optional[str] = None
    action: str
    actor_id: str
    actor_role: Optional[str] = None
    reason: Optional[str] = None
    before_hash: Optional[str] = None
    after_hash: Optional[str] = None
    event_timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuditQueryParams(BaseModel):
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    actor_id: Optional[str] = None
    action: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


class AuditEventListResponse(BaseModel):
    items: list[AuditEventResponse]
    total: int
    skip: int = 0
    limit: int = 100
