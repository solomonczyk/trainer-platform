"""Repository for Knowledge Source entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.knowledge_source_models import KnowledgeSource
from app.certification_core.repositories.base import CertBaseRepository


class KnowledgeSourceRepository(CertBaseRepository[KnowledgeSource]):
    """Repository for KnowledgeSource entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, KnowledgeSource)

    async def get_by_source_id(self, source_id: str) -> Optional[KnowledgeSource]:
        """Get knowledge source by its business ID."""
        return await self.get_by_business_id(source_id, id_field="source_id")

    async def list_sources(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        source_type: Optional[str] = None, locale: Optional[str] = None,
    ) -> tuple[list[KnowledgeSource], int]:
        """List knowledge sources with filters."""
        filters = {}
        if status:
            filters["status"] = status
        if source_type:
            filters["source_type"] = source_type
        if locale:
            filters["locale"] = locale
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)
