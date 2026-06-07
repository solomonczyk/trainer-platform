"""Base repository for certification-grade core entities — common CRUD operations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import select, func, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CertBaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations for certification entities."""

    def __init__(self, db: AsyncSession, model_class: type[ModelType]):
        self.db = db
        self.model_class = model_class

    async def create(self, **kwargs) -> ModelType:
        """Create a new entity."""
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        return instance

    async def get_by_id(self, entity_id: str) -> Optional[ModelType]:
        """Get entity by primary key ID."""
        result = await self.db.execute(
            select(self.model_class).where(self.model_class.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_by_business_id(self, business_id: str, id_field: str = "item_id") -> Optional[ModelType]:
        """Get entity by its business ID (unique identifier)."""
        column = getattr(self.model_class, id_field, None)
        if column is None:
            raise ValueError(f"Field '{id_field}' not found on {self.model_class.__name__}")
        result = await self.db.execute(
            select(self.model_class).where(column == business_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> tuple[list[ModelType], int]:
        """List entities with pagination and optional filters."""
        query = select(self.model_class)
        count_query = select(func.count(self.model_class.id))

        if filters:
            for field, value in filters.items():
                if value is not None:
                    column = getattr(self.model_class, field, None)
                    if column is not None:
                        query = query.where(column == value)
                        count_query = count_query.where(column == value)

        # Ordering
        if order_by and hasattr(self.model_class, order_by):
            order_col = getattr(self.model_class, order_by)
            query = query.order_by(order_col.desc() if order_desc else order_col.asc())
        else:
            query = query.order_by(self.model_class.created_at.desc())

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        count_result = await self.db.execute(count_query)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return list(items), total

    async def update_entity(self, entity_id: str, **kwargs) -> Optional[ModelType]:
        """Update an entity by primary key ID."""
        instance = await self.get_by_id(entity_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.db.flush()
        return instance

    async def soft_delete(self, entity_id: str, valid_until: Optional[datetime] = None) -> Optional[ModelType]:
        """Soft delete by setting valid_until."""
        instance = await self.get_by_id(entity_id)
        if instance is None:
            return None
        if hasattr(instance, "status"):
            setattr(instance, "status", "retired")
        if hasattr(instance, "valid_until"):
            setattr(instance, "valid_until", valid_until or datetime.now(timezone.utc))
        await self.db.flush()
        return instance

    async def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """Count entities, optionally filtered."""
        query = select(func.count(self.model_class.id))
        if filters:
            for field, value in filters.items():
                if value is not None:
                    column = getattr(self.model_class, field, None)
                    if column is not None:
                        query = query.where(column == value)
        result = await self.db.execute(query)
        return result.scalar() or 0
