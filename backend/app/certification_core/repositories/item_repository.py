"""Repository for Item and Item Family entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.certification_core.models.item_models import ItemFamily, Item, ItemVersion
from app.certification_core.repositories.base import CertBaseRepository


class ItemFamilyRepository(CertBaseRepository[ItemFamily]):
    """Repository for ItemFamily entities."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemFamily)

    async def get_by_family_id(self, family_id: str) -> Optional[ItemFamily]:
        """Get item family by business ID."""
        return await self.get_by_business_id(family_id, id_field="family_id")

    async def list_families(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        domain_pack_id: Optional[str] = None,
    ) -> tuple[list[ItemFamily], int]:
        """List item families with filters."""
        filters = {}
        if status:
            filters["status"] = status
        if domain_pack_id:
            filters["domain_pack_id"] = domain_pack_id
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)


class ItemRepository(CertBaseRepository[Item]):
    """Repository for Item entities with versioning support."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Item)

    async def get_by_item_id(self, item_id: str) -> Optional[Item]:
        """Get item by business ID with versions eagerly loaded."""
        result = await self.db.execute(
            select(Item)
            .where(Item.item_id == item_id)
            .options(selectinload(Item.versions))
        )
        return result.scalar_one_or_none()

    async def list_items(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        domain_pack_id: Optional[str] = None, item_type: Optional[str] = None,
        item_family_id: Optional[str] = None,
    ) -> tuple[list[Item], int]:
        """List items with filters."""
        filters = {}
        if status:
            filters["status"] = status
        if domain_pack_id:
            filters["domain_pack_id"] = domain_pack_id
        if item_type:
            filters["item_type"] = item_type
        if item_family_id:
            filters["item_family_id"] = item_family_id
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)

    async def create_snapshot(self, item_id: str, change_reason: str, created_by: str) -> Optional[ItemVersion]:
        """Create an immutable version snapshot of an item."""
        item = await self.get_by_id(item_id)
        if item is None:
            return None

        # Build snapshot from current state
        snapshot = {
            "item_id": item.item_id,
            "item_type": item.item_type,
            "prompt": item.prompt,
            "response_contract": item.response_contract,
            "answer_key": item.answer_key,
            "competency_ids": item.competency_ids,
            "knowledge_source_refs": item.knowledge_source_refs,
            "difficulty_target": item.difficulty_target,
            "status": item.status,
        }

        # Determine next version number
        next_version = (item.version or 0) + 1

        version_record = ItemVersion(
            item_id=item.id,
            version=next_version,
            snapshot=snapshot,
            change_reason=change_reason,
            created_by=created_by,
        )
        self.db.add(version_record)

        # Update item version counter
        item.version = next_version
        await self.db.flush()
        return version_record

    async def update_status(self, item_id: str, new_status: str) -> Optional[Item]:
        """Update item status (for lifecycle transitions)."""
        item = await self.get_by_id(item_id)
        if item is None:
            return None
        item.status = new_status
        await self.db.flush()
        return item
