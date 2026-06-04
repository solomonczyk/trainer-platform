"""REST endpoints for analytics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.modules.analytics.schemas import (
    AnalyticsEventRequest,
    AnalyticsEventResponse,
)
from app.modules.analytics.service import AnalyticsService

router = APIRouter(tags=["Analytics"])


@router.post("/events", response_model=AnalyticsEventResponse)
async def record_event(
    body: AnalyticsEventRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsEventResponse:
    """Record an analytics event.

    Events are validated against an allowlist of safe event types.
    Sensitive data (answers, passwords, tokens, API keys) is stripped
    from the ``properties`` payload before persistence.
    """
    event = await AnalyticsService.record_event(
        db,
        user_id=user_id,
        event_type=body.event_type,
        session_id=body.session_id,
        trainer_slug=body.trainer_slug,
        scenario_id=body.scenario_id,
        properties=body.properties,
    )
    if event is None:
        return AnalyticsEventResponse(event_id="", status="skipped")
    return AnalyticsEventResponse(event_id=event.id, status="recorded")
