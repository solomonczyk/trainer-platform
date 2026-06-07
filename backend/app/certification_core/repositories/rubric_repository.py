"""Repository for Rubric and Rubric Criterion entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.certification_core.models.rubric_models import CertRubric, CertRubricCriterion
from app.certification_core.repositories.base import CertBaseRepository


class RubricRepository(CertBaseRepository[CertRubric]):
    """Repository for Rubric entities with criterion management."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, CertRubric)

    async def get_by_rubric_id(self, rubric_id: str) -> Optional[CertRubric]:
        """Get rubric by business ID with criteria eagerly loaded."""
        result = await self.db.execute(
            select(CertRubric)
            .where(CertRubric.rubric_id == rubric_id)
            .options(selectinload(CertRubric.criteria))
        )
        return result.scalar_one_or_none()

    async def list_rubrics(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        domain_pack_id: Optional[str] = None,
    ) -> tuple[list[CertRubric], int]:
        """List rubrics with filters."""
        filters = {}
        if status:
            filters["status"] = status
        if domain_pack_id:
            filters["domain_pack_id"] = domain_pack_id
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)

    async def add_criterion(self, rubric_id: str, **kwargs) -> CertRubricCriterion:
        """Add a criterion to a rubric."""
        criterion = CertRubricCriterion(rubric_id=rubric_id, **kwargs)
        self.db.add(criterion)
        await self.db.flush()
        return criterion

    async def get_criterion(self, criterion_id: str) -> Optional[CertRubricCriterion]:
        """Get a specific criterion."""
        result = await self.db.execute(
            select(CertRubricCriterion).where(CertRubricCriterion.id == criterion_id)
        )
        return result.scalar_one_or_none()

    async def update_criterion(self, criterion_id: str, **kwargs) -> Optional[CertRubricCriterion]:
        """Update a criterion."""
        criterion = await self.get_criterion(criterion_id)
        if criterion is None:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(criterion, key):
                setattr(criterion, key, value)
        await self.db.flush()
        return criterion

    async def recalculate_total_weight(self, rubric_id: str) -> float:
        """Recalculate and update the total_weight of a rubric from its criteria."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(CertRubricCriterion.weight), 0))
            .where(CertRubricCriterion.rubric_id == rubric_id)
        )
        total = float(result.scalar() or 0)
        rubric = await self.get_by_id(rubric_id)
        if rubric:
            rubric.total_weight = total
            await self.db.flush()
        return total
