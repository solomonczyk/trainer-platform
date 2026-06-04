"""Business logic for the Domains module."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Domain, TrainerProduct
from app.modules.domains.repository import (
    list_active_domains,
    get_by_slug,
    count_trainers,
)


async def get_all_domains(db: AsyncSession) -> list[dict]:
    """Return all active domains with their trainer counts."""
    domains = await list_active_domains(db)
    result: list[dict] = []
    for d in domains:
        trainer_count = await count_trainers(db, d.id)
        result.append(
            {
                "id": d.id,
                "slug": d.slug,
                "name": d.name,
                "description": d.description,
                "icon": d.icon,
                "sort_order": d.sort_order,
                "trainer_count": trainer_count,
            }
        )
    return result


async def get_domain_by_slug(db: AsyncSession, slug: str) -> Domain | None:
    """Return a domain by slug, or None."""
    return await get_by_slug(db, slug)


async def get_domain_with_trainers(db: AsyncSession, slug: str) -> dict | None:
    """Return a domain with its published trainers as a dict, or None."""
    domain = await get_by_slug(db, slug)
    if not domain:
        return None

    result = await db.execute(
        select(TrainerProduct)
        .where(TrainerProduct.domain_id == domain.id)
        .where(TrainerProduct.is_published.is_(True))
        .order_by(TrainerProduct.name)
    )
    trainers = result.scalars().all()

    return {
        "id": domain.id,
        "slug": domain.slug,
        "name": domain.name,
        "description": domain.description,
        "icon": domain.icon,
        "trainers": [
            {
                "id": t.id,
                "trainer_product_id": t.trainer_product_id,
                "slug": t.slug,
                "name": t.name,
                "description": t.description,
                "product_type": t.product_type,
            }
            for t in trainers
        ],
    }
