"""Pydantic schemas for item lifecycle transitions."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemTransitionRequest(BaseModel):
    to_status: str = Field(..., max_length=30)
    actor_id: str = Field(..., max_length=100)
    actor_role: str = Field(..., max_length=50)
    reason: str = Field(..., max_length=500)


class ItemTransitionResponse(BaseModel):
    item_id: str
    from_status: str
    to_status: str
    allowed: bool = True
    reason: Optional[str] = None
    timestamp: Optional[datetime] = None
    message: str = "Transition completed"
