"""API routes for Item Family management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.certification_core.schemas.item_schemas import (
    ItemFamilyCreate, ItemFamilyUpdate, ItemFamilyResponse, ItemFamilyListResponse,
)
from app.certification_core.repositories.item_repository import ItemFamilyRepository
from app.certification_core.validators.item_validator import ItemFamilyValidator
from app.certification_core.services.authorization import (
    get_current_certification_role,
)
from app.certification_core.audit.service import AuditService
from app.db.session import get_db

router = APIRouter(prefix="/certification-core/item-families", tags=["Certification-Core"])


@router.get("", response_model=ItemFamilyListResponse)
async def list_families(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    status: str = Query(None), domain_pack_id: str = Query(None),
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = ItemFamilyRepository(db)
    items, total = await repo.list_families(skip=skip, limit=limit, status=status, domain_pack_id=domain_pack_id)
    return ItemFamilyListResponse(
        items=[ItemFamilyResponse.model_validate(f) for f in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{family_id}", response_model=ItemFamilyResponse)
async def get_family(
    family_id: str,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = ItemFamilyRepository(db)
    family = await repo.get_by_family_id(family_id)
    if not family:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Item family not found")
    return ItemFamilyResponse.model_validate(family)


@router.post("", response_model=ItemFamilyResponse, status_code=HTTP_201_CREATED)
async def create_family(
    body: ItemFamilyCreate,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    errors = ItemFamilyValidator.validate_family(body.model_dump())
    if errors:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail={"validation_errors": errors})

    repo = ItemFamilyRepository(db)
    audit = AuditService(db)
    family = await repo.create(**body.model_dump())
    await audit.record_create(
        entity_type="item_family", entity_id=family.family_id,
        actor_id=body.created_by, actor_role=role,
    )
    return ItemFamilyResponse.model_validate(family)


@router.patch("/{family_id}", response_model=ItemFamilyResponse)
async def update_family(
    family_id: str, body: ItemFamilyUpdate,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = ItemFamilyRepository(db)
    family = await repo.get_by_family_id(family_id)
    if not family:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Item family not found")
    family = await repo.update_entity(family.id, **body.model_dump(exclude_none=True))
    return ItemFamilyResponse.model_validate(family)
