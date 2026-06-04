"""Data-access layer for trainer progress and skill scores."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SkillScore, TrainerProgress


class ProgressRepository:
    """Stateless repository for TrainerProgress and SkillScore CRUD."""

    @staticmethod
    async def get_by_user_and_trainer(
        db: AsyncSession,
        user_id: str,
        trainer_id: str,
    ) -> TrainerProgress | None:
        """Return a single progress record, or None."""
        result = await db.execute(
            select(TrainerProgress).where(
                TrainerProgress.user_id == user_id,
                TrainerProgress.trainer_product_id == trainer_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_progress(
        db: AsyncSession,
        user_id: str,
        trainer_id: str,
    ) -> TrainerProgress:
        """Create a new progress record for a user+trainer pair."""
        progress = TrainerProgress(
            user_id=user_id,
            trainer_product_id=trainer_id,
        )
        db.add(progress)
        await db.flush()
        return progress

    @staticmethod
    async def update_progress(
        db: AsyncSession,
        progress: TrainerProgress,
        data: dict,
    ) -> TrainerProgress:
        """Apply partial updates to an existing progress record."""
        for key, value in data.items():
            if hasattr(progress, key):
                setattr(progress, key, value)
        await db.flush()
        return progress

    @staticmethod
    async def get_skill_scores(
        db: AsyncSession,
        user_id: str,
        trainer_id: str,
    ) -> list[SkillScore]:
        """Return all skill-score rows for a user+trainer pair."""
        result = await db.execute(
            select(SkillScore).where(
                SkillScore.user_id == user_id,
                SkillScore.trainer_product_id == trainer_id,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def upsert_skill_score(
        db: AsyncSession,
        user_id: str,
        trainer_id: str,
        skill_id: str,
        score: float,
    ) -> SkillScore:
        """Create or update a single skill-score row."""
        result = await db.execute(
            select(SkillScore).where(
                SkillScore.user_id == user_id,
                SkillScore.trainer_product_id == trainer_id,
                SkillScore.skill_id == skill_id,
            )
        )
        skill_score = result.scalar_one_or_none()

        if skill_score is not None:
            skill_score.score = score
            skill_score.attempts_count += 1
        else:
            skill_score = SkillScore(
                user_id=user_id,
                trainer_product_id=trainer_id,
                skill_id=skill_id,
                score=score,
                attempts_count=1,
            )
            db.add(skill_score)

        await db.flush()
        return skill_score

    @staticmethod
    async def list_by_user(
        db: AsyncSession,
        user_id: str,
    ) -> list[TrainerProgress]:
        """Return all progress records for a given user."""
        result = await db.execute(
            select(TrainerProgress)
            .where(TrainerProgress.user_id == user_id)
            .order_by(TrainerProgress.updated_at.desc().nulls_last())
        )
        return list(result.scalars().all())
