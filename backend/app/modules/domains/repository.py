"""Database queries for the Domains module."""
from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Domain, TrainerProduct


async def list_active_domains(db: AsyncSession) -> list[Domain]:
    """Return all active domains ordered by sort_order."""
    result = await db.execute(
        select(Domain)
        .where(Domain.is_active.is_(True))
        .order_by(Domain.sort_order)
    )
    return list(result.scalars().all())


async def get_by_slug(db: AsyncSession, slug: str) -> Domain | None:
    """Return a domain by slug, or None if not found."""
    result = await db.execute(
        select(Domain).where(Domain.slug == slug)
    )
    return result.scalar_one_or_none()


async def count_trainers(db: AsyncSession, domain_id: str) -> int:
    """Count published trainers for a given domain."""
    result = await db.execute(
        select(func.count(TrainerProduct.id))
        .where(TrainerProduct.domain_id == domain_id)
        .where(TrainerProduct.is_published.is_(True))
    )
    return result.scalar() or 0
