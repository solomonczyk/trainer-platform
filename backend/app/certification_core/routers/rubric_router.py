"""API routes for Rubric management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.certification_core.schemas.rubric_schemas import (
    RubricCreate, RubricUpdate, RubricResponse, RubricListResponse,
)
from app.certification_core.repositories.rubric_repository import RubricRepository
from app.certification_core.validators.rubric_validator import RubricValidator
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    get_current_certification_role, require_permission,
)
from app.db.session import get_db

router = APIRouter(prefix="/certification-core/rubrics", tags=["Certification-Core"])


@router.get("", response_model=RubricListResponse)
async def list_rubrics(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    status: str = Query(None), domain_pack_id: str = Query(None),
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = RubricRepository(db)
    items, total = await repo.list_rubrics(skip=skip, limit=limit, status=status, domain_pack_id=domain_pack_id)
    return RubricListResponse(
        items=[RubricResponse.model_validate(r) for r in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{rubric_id}", response_model=RubricResponse)
async def get_rubric(
    rubric_id: str,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = RubricRepository(db)
    rubric = await repo.get_by_rubric_id(rubric_id)
    if not rubric:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Rubric not found")
    return RubricResponse.model_validate(rubric)


@router.post("", response_model=RubricResponse, status_code=HTTP_201_CREATED)
async def create_rubric(
    body: RubricCreate,
    role: str = Depends(require_permission("certification:manage_rubrics")),
    db: AsyncSession = Depends(get_db),
):
    errors = RubricValidator.validate_rubric(body.model_dump())
    if errors:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail={"validation_errors": errors})

    repo = RubricRepository(db)
    audit = AuditService(db)

    rubric_data = body.model_dump(exclude={"criteria"})
    rubric = await repo.create(**rubric_data)

    total_w = 0.0
    for crit_data in body.criteria:
        c = await repo.add_criterion(rubric_id=rubric.id, **crit_data.model_dump())
        total_w += c.weight
    rubric.total_weight = total_w
    await db.flush()
    await db.refresh(rubric)

    await audit.record_create(
        entity_type="rubric", entity_id=rubric.rubric_id,
        actor_id=body.created_by, actor_role=role,
    )
    return RubricResponse.model_validate(rubric)


@router.patch("/{rubric_id}", response_model=RubricResponse)
async def update_rubric(
    rubric_id: str, body: RubricUpdate,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = RubricRepository(db)
    rubric = await repo.get_by_rubric_id(rubric_id)
    if not rubric:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Rubric not found")
    rubric = await repo.update_entity(rubric.id, **body.model_dump(exclude_none=True))
    return RubricResponse.model_validate(rubric)
