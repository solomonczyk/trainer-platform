"""Business-logic layer for trainer progress."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Evaluation, Skill, TrainerProduct
from app.modules.progress.repository import ProgressRepository


class ProgressService:
    """Orchestrates progress queries and updates."""

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_readiness(average_score: float, completed: int, total: int) -> str:
        """Derive a readiness label from aggregated metrics."""
        if total == 0:
            return "started"
        if average_score >= 85 and completed >= 5:
            return "strong"
        if average_score >= 70 and completed >= 3:
            return "ready"
        if average_score >= 50 and completed >= 1:
            return "developing"
        return "started"

    @staticmethod
    async def _resolve_skill_name(db: AsyncSession, skill_id: str) -> str:
        """Look up a human-readable skill name by its external identifier."""
        result = await db.execute(select(Skill).where(Skill.skill_id == skill_id))
        skill = result.scalar_one_or_none()
        return skill.name if skill is not None else skill_id

    @staticmethod
    async def _build_progress_item(
        db: AsyncSession,
        user_id: str,
        progress,
    ) -> dict | None:
        """Assemble a single ProgressSummaryResponse-compatible dict."""
        trainer = await db.get(TrainerProduct, progress.trainer_product_id)
        if trainer is None:
            return None

        skill_scores = await ProgressRepository.get_skill_scores(
            db, user_id, progress.trainer_product_id
        )
        skill_list = []
        for ss in skill_scores:
            skill_list.append(
                {
                    "skill_id": ss.skill_id,
                    "skill_name": await ProgressService._resolve_skill_name(
                        db, ss.skill_id
                    ),
                    "score": ss.score,
                    "level": ss.level,
                    "attempts_count": ss.attempts_count,
                }
            )

        return {
            "trainer_slug": trainer.slug,
            "trainer_name": trainer.name,
            "average_score": progress.average_score,
            "completed_scenarios": progress.completed_scenarios,
            "total_attempts": progress.total_attempts,
            "readiness_status": progress.readiness_status,
            "skill_scores": skill_list,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    async def get_all_progress(cls, db: AsyncSession, user_id: str) -> list[dict]:
        """Return progress summaries for every trainer the user has attempted."""
        records = await ProgressRepository.list_by_user(db, user_id)
        results: list[dict] = []
        for p in records:
            item = await cls._build_progress_item(db, user_id, p)
            if item is not None:
                results.append(item)
        return results

    @classmethod
    async def get_trainer_progress(
        cls,
        db: AsyncSession,
        user_id: str,
        trainer_slug: str,
    ) -> dict | None:
        """Return progress summary for a specific trainer, or default if no progress yet."""
        result = await db.execute(
            select(TrainerProduct).where(TrainerProduct.slug == trainer_slug)
        )
        trainer = result.scalar_one_or_none()
        if trainer is None:
            return None

        progress = await ProgressRepository.get_by_user_and_trainer(
            db, user_id, trainer.id
        )
        if progress is None:
            # Return a default progress summary when no progress record exists yet
            return {
                "trainer_slug": trainer.slug,
                "trainer_name": trainer.name,
                "average_score": 0.0,
                "completed_scenarios": 0,
                "total_attempts": 0,
                "readiness_status": "started",
                "skill_scores": [],
            }

        return await cls._build_progress_item(db, user_id, progress)

    @classmethod
    async def update_progress_after_evaluation(
        cls,
        db: AsyncSession,
        user_id: str,
        trainer_id: str,
        evaluation: Evaluation,
    ) -> TrainerProgress:
        """Recompute progress metrics after a completed evaluation."""
        from app.db.models import TrainerProgress

        progress = await ProgressRepository.get_by_user_and_trainer(
            db, user_id, trainer_id
        )
        if progress is None:
            progress = await ProgressRepository.create_progress(
                db, user_id, trainer_id
            )

        # Accumulate attempt count and completed scenario count
        progress.total_attempts += 1
        if evaluation.passed:
            progress.completed_scenarios += 1

        # Rolling average score
        old_total = progress.average_score * (progress.total_attempts - 1)
        progress.average_score = round(
            (old_total + evaluation.overall_score) / progress.total_attempts, 2
        )

        # Refresh readiness label
        progress.readiness_status = cls._calculate_readiness(
            progress.average_score,
            progress.completed_scenarios,
            progress.total_attempts,
        )

        await db.flush()
        return progress
