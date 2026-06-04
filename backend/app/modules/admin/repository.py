"""Data-access layer for admin operations."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AnalyticsEvent,
    Attempt,
    Domain,
    Evaluation,
    Rubric,
    Scenario,
    Skill,
    TrainerLocalization,
    TrainerProduct,
    UserTrainerEnrollment,
)


class AdminRepository:
    """Stateless repository for admin-level aggregate queries."""

    # Mapping of human-readable table names to their SQLAlchemy models.
    TABLE_COUNTS: dict[str, type] = {
        "domains": Domain,
        "trainers": TrainerProduct,
        "scenarios": Scenario,
        "rubrics": Rubric,
        "locales": TrainerLocalization,
        "skills": Skill,
        "enrollments": UserTrainerEnrollment,
    }

    # ------------------------------------------------------------------
    # Counts
    # ------------------------------------------------------------------

    @staticmethod
    async def count_table(db: AsyncSession, model: type) -> int:
        """Return the total number of rows in *model*'s table."""
        result = await db.execute(select(func.count()).select_from(model))
        return result.scalar() or 0

    # ------------------------------------------------------------------
    # Failed evaluations
    # ------------------------------------------------------------------

    @staticmethod
    async def get_failed_evals(
        db: AsyncSession, limit: int = 50
    ) -> list[dict]:
        """Return failed evaluations (without raw_ai_output)."""
        rows = await db.execute(
            select(Evaluation, Attempt)
            .join(Attempt, Evaluation.attempt_id == Attempt.id)
            .where(Evaluation.validation_status == "failed")
            .order_by(Evaluation.created_at.desc().nulls_last())
            .limit(limit)
        )
        evaluations: list[dict] = []
        for ev, att in rows.all():
            evaluations.append(
                {
                    "evaluation_id": ev.id,
                    "attempt_id": ev.attempt_id,
                    "overall_score": ev.overall_score,
                    "confidence": ev.confidence,
                    "validation_status": ev.validation_status,
                    "ai_model_used": ev.ai_model_used,
                    "ai_cost_usd": ev.ai_cost_usd,
                    "ai_latency_ms": ev.ai_latency_ms,
                    "created_at": ev.created_at.isoformat()
                    if ev.created_at
                    else None,
                }
            )
        return evaluations

    # ------------------------------------------------------------------
    # Analytics event breakdown
    # ------------------------------------------------------------------

    @staticmethod
    async def get_event_counts(db: AsyncSession) -> list[dict]:
        """Return event counts grouped by event_type, sorted by count desc."""
        rows = await db.execute(
            select(
                AnalyticsEvent.event_type,
                func.count().label("count"),
            )
            .group_by(AnalyticsEvent.event_type)
            .order_by(func.count().desc())
        )
        return [
            {"event_type": row[0], "count": row[1]} for row in rows.all()
        ]
