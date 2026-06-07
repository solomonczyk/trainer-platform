"""Repository for Competency Framework and Competency entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.certification_core.models.competency_models import CompetencyFramework, Competency
from app.certification_core.repositories.base import CertBaseRepository


class CompetencyRepository(CertBaseRepository[CompetencyFramework]):
    """Repository for CompetencyFramework with competency management."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, CompetencyFramework)

    async def get_by_framework_id(self, framework_id: str) -> Optional[CompetencyFramework]:
        """Get framework by business ID with competencies eagerly loaded."""
        result = await self.db.execute(
            select(CompetencyFramework)
            .where(CompetencyFramework.framework_id == framework_id)
            .options(selectinload(CompetencyFramework.competencies))
        )
        return result.scalar_one_or_none()

    async def list_frameworks(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        domain_pack_id: Optional[str] = None,
    ) -> tuple[list[CompetencyFramework], int]:
        """List frameworks with filters."""
        filters = {}
        if status:
            filters["status"] = status
        if domain_pack_id:
            filters["domain_pack_id"] = domain_pack_id
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)

    async def add_competency(self, framework_id: str, **kwargs) -> Competency:
        """Add a competency to a framework."""
        comp = Competency(framework_id=framework_id, **kwargs)
        self.db.add(comp)
        await self.db.flush()
        return comp

    async def get_competency(self, competency_id: str) -> Optional[Competency]:
        """Get a specific competency by its primary key."""
        result = await self.db.execute(
            select(Competency).where(Competency.id == competency_id)
        )
        return result.scalar_one_or_none()

    async def update_competency(self, competency_id: str, **kwargs) -> Optional[Competency]:
        """Update a competency."""
        comp = await self.get_competency(competency_id)
        if comp is None:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(comp, key):
                setattr(comp, key, value)
        await self.db.flush()
        return comp

    async def list_competencies(
        self, framework_id: str, skip: int = 0, limit: int = 100,
    ) -> tuple[list[Competency], int]:
        """List competencies within a framework."""
        query = select(Competency).where(Competency.framework_id == framework_id)
        count_query = select(func.count(Competency.id)).where(Competency.framework_id == framework_id)
        query = query.order_by(Competency.sort_order).offset(skip).limit(limit)

        result = await self.db.execute(query)
        count_result = await self.db.execute(count_query)
        return list(result.scalars().all()), count_result.scalar() or 0
