"""API routes for Domain Pack management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.certification_core.schemas.domain_pack_schemas import (
    DomainPackCreate, DomainPackUpdate, DomainPackResponse, DomainPackListResponse,
)
from app.certification_core.repositories.domain_pack_repository import DomainPackRepository
from app.certification_core.validators.domain_pack_validator import DomainPackValidator
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    get_current_certification_role, require_permission,
)
from app.db.session import get_db

router = APIRouter(prefix="/certification-core/domain-packs", tags=["Certification-Core"])


@router.get("", response_model=DomainPackListResponse)
async def list_domain_packs(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    status: str = Query(None), locale: str = Query(None), market: str = Query(None),
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = DomainPackRepository(db)
    items, total = await repo.list_domain_packs(skip=skip, limit=limit, status=status, locale=locale, market=market)
    return DomainPackListResponse(
        items=[DomainPackResponse.model_validate(dp) for dp in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{domain_pack_id}", response_model=DomainPackResponse)
async def get_domain_pack(
    domain_pack_id: str,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = DomainPackRepository(db)
    dp = await repo.get_by_domain_pack_id(domain_pack_id)
    if not dp:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Domain pack not found")
    return DomainPackResponse.model_validate(dp)


@router.post("", response_model=DomainPackResponse, status_code=HTTP_201_CREATED)
async def create_domain_pack(
    body: DomainPackCreate,
    role: str = Depends(require_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    errors = DomainPackValidator.validate_domain_pack(body.model_dump())
    if errors:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail={"validation_errors": errors})

    repo = DomainPackRepository(db)
    audit = AuditService(db)

    dp = await repo.create(**body.model_dump())
    await audit.record_create(
        entity_type="domain_pack", entity_id=dp.domain_pack_id,
        actor_id=body.created_by, actor_role=role,
    )
    return DomainPackResponse.model_validate(dp)


@router.patch("/{domain_pack_id}", response_model=DomainPackResponse)
async def update_domain_pack(
    domain_pack_id: str, body: DomainPackUpdate,
    role: str = Depends(require_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    repo = DomainPackRepository(db)
    dp = await repo.get_by_domain_pack_id(domain_pack_id)
    if not dp:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Domain pack not found")
    dp = await repo.update_entity(dp.id, **body.model_dump(exclude_none=True))
    return DomainPackResponse.model_validate(dp)
