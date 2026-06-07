"""Repository for Exam Blueprint and Blueprint Section entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.certification_core.models.blueprint_models import ExamBlueprint, BlueprintSection
from app.certification_core.repositories.base import CertBaseRepository


class BlueprintRepository(CertBaseRepository[ExamBlueprint]):
    """Repository for ExamBlueprint with section management."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ExamBlueprint)

    async def get_by_blueprint_id(self, blueprint_id: str) -> Optional[ExamBlueprint]:
        """Get blueprint by business ID with sections eagerly loaded."""
        result = await self.db.execute(
            select(ExamBlueprint)
            .where(ExamBlueprint.blueprint_id == blueprint_id)
            .options(selectinload(ExamBlueprint.sections))
        )
        return result.scalar_one_or_none()

    async def list_blueprints(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        domain_pack_id: Optional[str] = None,
    ) -> tuple[list[ExamBlueprint], int]:
        """List blueprints with filters."""
        filters = {}
        if status:
            filters["status"] = status
        if domain_pack_id:
            filters["domain_pack_id"] = domain_pack_id
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)

    async def add_section(self, blueprint_id: str, **kwargs) -> BlueprintSection:
        """Add a section to a blueprint."""
        section = BlueprintSection(blueprint_id=blueprint_id, **kwargs)
        self.db.add(section)
        await self.db.flush()
        return section

    async def get_section(self, section_id: str) -> Optional[BlueprintSection]:
        """Get a specific section by its primary key."""
        result = await self.db.execute(
            select(BlueprintSection).where(BlueprintSection.id == section_id)
        )
        return result.scalar_one_or_none()

    async def update_section(self, section_id: str, **kwargs) -> Optional[BlueprintSection]:
        """Update a section."""
        section = await self.get_section(section_id)
        if section is None:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(section, key):
                setattr(section, key, value)
        await self.db.flush()
        return section

    async def list_sections(
        self, blueprint_id: str,
    ) -> tuple[list[BlueprintSection], int]:
        """List sections within a blueprint."""
        query = select(BlueprintSection).where(BlueprintSection.blueprint_id == blueprint_id)
        count_query = select(func.count(BlueprintSection.id)).where(
            BlueprintSection.blueprint_id == blueprint_id
        )
        query = query.order_by(BlueprintSection.sort_order)

        result = await self.db.execute(query)
        count_result = await self.db.execute(count_query)
        return list(result.scalars().all()), count_result.scalar() or 0
