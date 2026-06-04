"""Data-access layer for analytics events."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AnalyticsEvent


class AnalyticsRepository:
    """Stateless repository for AnalyticsEvent CRUD."""

    @staticmethod
    async def create_event(
        db: AsyncSession,
        user_id: str,
        event_type: str,
        data: dict,
    ) -> AnalyticsEvent:
        """Persist a new analytics event and return it."""
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            session_id=data.get("session_id"),
            trainer_slug=data.get("trainer_slug"),
            scenario_id=data.get("scenario_id"),
            properties=data.get("properties"),
        )
        db.add(event)
        await db.flush()
        return event
