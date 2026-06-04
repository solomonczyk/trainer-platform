"""Router for the Domains module."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.errors import NotFoundError
from app.modules.domains.schemas import DomainResponse, DomainDetailResponse
from app.modules.domains.service import get_all_domains, get_domain_with_trainers

router = APIRouter()


@router.get("/domains", response_model=list[DomainResponse])
async def list_domains(
    db: AsyncSession = Depends(get_db),
) -> list[DomainResponse]:
    """Return all active domains with their trainer counts."""
    domains_data = await get_all_domains(db)
    return [DomainResponse(**d) for d in domains_data]


@router.get(
    "/domains/{domain_slug}",
    response_model=DomainDetailResponse,
)
async def get_domain(
    domain_slug: str,
    db: AsyncSession = Depends(get_db),
) -> DomainDetailResponse:
    """Return a domain detail including its published trainers."""
    domain_data = await get_domain_with_trainers(db, domain_slug)
    if not domain_data:
        raise NotFoundError("Domain", domain_slug)
    return DomainDetailResponse(**domain_data)
