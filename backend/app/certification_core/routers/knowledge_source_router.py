"""API routes for Knowledge Source Registry."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.certification_core.schemas.knowledge_source_schemas import (
    KnowledgeSourceCreate, KnowledgeSourceUpdate, KnowledgeSourceResponse,
    KnowledgeSourceListResponse,
)
from app.certification_core.repositories.knowledge_source_repository import KnowledgeSourceRepository
from app.certification_core.validators.knowledge_source_validator import KnowledgeSourceValidator
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    get_current_certification_role, require_certification_permission,
)
from app.db.session import get_db

router = APIRouter(prefix="/certification-core/knowledge-sources", tags=["Certification-Core"])


@router.get("", response_model=KnowledgeSourceListResponse)
async def list_sources(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    status: str = Query(None), source_type: str = Query(None),
    locale: str = Query(None),
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = KnowledgeSourceRepository(db)
    items, total = await repo.list_sources(skip=skip, limit=limit, status=status, source_type=source_type, locale=locale)
    return KnowledgeSourceListResponse(
        items=[KnowledgeSourceResponse.model_validate(s) for s in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{source_id}", response_model=KnowledgeSourceResponse)
async def get_source(
    source_id: str,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    repo = KnowledgeSourceRepository(db)
    src = await repo.get_by_source_id(source_id)
    if not src:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Knowledge source not found")
    return KnowledgeSourceResponse.model_validate(src)


@router.post("", response_model=KnowledgeSourceResponse, status_code=HTTP_201_CREATED)
async def create_source(
    body: KnowledgeSourceCreate,
    role: str = Depends(lambda: require_certification_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    errors = KnowledgeSourceValidator.validate_source(body.model_dump())
    if errors:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail={"validation_errors": errors})

    repo = KnowledgeSourceRepository(db)
    audit = AuditService(db)

    src = await repo.create(**body.model_dump())
    await audit.record_create(
        entity_type="knowledge_source", entity_id=src.source_id,
        actor_id=body.created_by, actor_role=role,
    )
    return KnowledgeSourceResponse.model_validate(src)


@router.patch("/{source_id}", response_model=KnowledgeSourceResponse)
async def update_source(
    source_id: str,
    body: KnowledgeSourceUpdate,
    role: str = Depends(lambda: require_certification_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    repo = KnowledgeSourceRepository(db)
    audit = AuditService(db)
    src = await repo.get_by_source_id(source_id)
    if not src:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Knowledge source not found")
    src = await repo.update_entity(src.id, **body.model_dump(exclude_none=True))
    await audit.record_update(
        entity_type="knowledge_source", entity_id=source_id,
        actor_id=role, actor_role=role,
    )
    return KnowledgeSourceResponse.model_validate(src)
