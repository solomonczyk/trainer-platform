"""Repository for Domain Pack entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.domain_pack_models import DomainPack
from app.certification_core.repositories.base import CertBaseRepository


class DomainPackRepository(CertBaseRepository[DomainPack]):
    """Repository for DomainPack entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, DomainPack)

    async def get_by_domain_pack_id(self, domain_pack_id: str) -> Optional[DomainPack]:
        """Get domain pack by business ID."""
        return await self.get_by_business_id(domain_pack_id, id_field="domain_pack_id")

    async def list_domain_packs(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        locale: Optional[str] = None, market: Optional[str] = None,
    ) -> tuple[list[DomainPack], int]:
        """List domain packs with filters."""
        filters = {}
        if status:
            filters["status"] = status
        if locale:
            filters["locale"] = locale
        if market:
            filters["market"] = market
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)
