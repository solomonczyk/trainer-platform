"""Pydantic schemas for the analytics module."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class AnalyticsEventRequest(BaseModel):
    """Payload for recording a single analytics event."""

    event_type: str
    session_id: Optional[str] = None
    trainer_slug: Optional[str] = None
    scenario_id: Optional[str] = None
    properties: Optional[dict] = None


class AnalyticsEventResponse(BaseModel):
    """Confirmation response after recording an event."""

    event_id: str
    status: str = "recorded"
