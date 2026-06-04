"""Business-logic layer for admin operations."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AnalyticsEvent, Domain
from app.modules.admin.repository import AdminRepository


class AdminService:
    """Orchestrates admin-level queries and health checks."""

    @staticmethod
    async def get_seed_status(db: AsyncSession) -> dict:
        """Return row counts from all major entity tables."""
        counts: dict[str, int] = {}
        for name, model in AdminRepository.TABLE_COUNTS.items():
            counts[name] = await AdminRepository.count_table(db, model)
        return counts

    @staticmethod
    async def get_system_health(db: AsyncSession) -> dict:
        """Return a health summary including database connectivity."""
        db_status = "ok"
        try:
            await db.execute(select(func.count()).select_from(Domain))
        except Exception:
            db_status = "error"

        modules_status = {
            "auth": "configured",
            "users": "configured",
            "domains": "configured",
            "trainers": "configured",
            "scenarios": "configured",
            "runtime": "configured",
            "evaluations": "configured",
            "progress": "configured",
            "analytics": "configured",
            "admin": "configured",
        }

        return {
            "status": "healthy" if db_status == "ok" else "degraded",
            "database": db_status,
            "modules": modules_status,
        }

    @staticmethod
    async def get_evaluation_failures(
        db: AsyncSession, limit: int = 50
    ) -> list[dict]:
        """Return failed evaluations without raw answer data."""
        return await AdminRepository.get_failed_evals(db, limit)

    @staticmethod
    async def get_analytics_sanity(db: AsyncSession) -> dict:
        """Return total event count and breakdown by event type."""
        total = await AdminRepository.count_table(db, AnalyticsEvent)
        by_type = await AdminRepository.get_event_counts(db)
        return {"total_events": total, "events_by_type": by_type}
