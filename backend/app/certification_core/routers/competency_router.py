"""API routes for Competency Framework management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.certification_core.schemas.competency_schemas import (
    CompetencyFrameworkCreate, CompetencyFrameworkUpdate, CompetencyFrameworkResponse,
    CompetencyFrameworkListResponse, CompetencyCreate, CompetencyUpdate, CompetencyResponse,
)
from app.certification_core.repositories.competency_repository import CompetencyRepository
from app.certification_core.validators.competency_validator import CompetencyValidator
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    get_current_certification_role, require_permission,
)
from app.db.session import get_db

router = APIRouter(prefix="/certification-core/competency-frameworks", tags=["Certification-Core"])


@router.get("", response_model=CompetencyFrameworkListResponse)
async def list_frameworks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str = Query(None),
    domain_pack_id: str = Query(None),
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    """List competency frameworks with optional filters."""
    repo = CompetencyRepository(db)
    items, total = await repo.list_frameworks(skip=skip, limit=limit, status=status, domain_pack_id=domain_pack_id)
    return CompetencyFrameworkListResponse(
        items=[CompetencyFrameworkResponse.model_validate(fw) for fw in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{framework_id}", response_model=CompetencyFrameworkResponse)
async def get_framework(
    framework_id: str,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    """Get a competency framework by its business ID."""
    repo = CompetencyRepository(db)
    fw = await repo.get_by_framework_id(framework_id)
    if not fw:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Competency framework not found")
    return CompetencyFrameworkResponse.model_validate(fw)


@router.post("", response_model=CompetencyFrameworkResponse, status_code=HTTP_201_CREATED)
async def create_framework(
    body: CompetencyFrameworkCreate,
    role: str = Depends(require_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new competency framework with competencies."""
    # Validate
    errors = CompetencyValidator.validate_framework(body.model_dump())
    if errors:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail={"validation_errors": errors})

    repo = CompetencyRepository(db)
    audit = AuditService(db)

    # Create framework
    fw_data = body.model_dump(exclude={"competencies"})
    fw = await repo.create(**fw_data)

    # Create competencies
    for comp_data in body.competencies:
        await repo.add_competency(framework_id=fw.id, **comp_data.model_dump())

    await db.refresh(fw)

    # Audit
    await audit.record_create(
        entity_type="competency_framework",
        entity_id=fw.framework_id,
        actor_id=body.created_by,
        actor_role=role,
        after_state={"framework_id": fw.framework_id, "version": fw.version},
    )

    return CompetencyFrameworkResponse.model_validate(fw)


@router.patch("/{framework_id}", response_model=CompetencyFrameworkResponse)
async def update_framework(
    framework_id: str,
    body: CompetencyFrameworkUpdate,
    role: str = Depends(require_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    """Update a competency framework."""
    repo = CompetencyRepository(db)
    audit = AuditService(db)

    fw = await repo.get_by_framework_id(framework_id)
    if not fw:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Competency framework not found")

    # Prevent update if active (immutable published versions)
    if fw.status == "active":
        if body.status and body.status == "deprecated":
            pass  # Allow deprecation
        else:
            raise HTTPException(HTTP_400_BAD_REQUEST, detail="Active frameworks cannot be modified; create a new version")

    before = {"status": fw.status}
    fw = await repo.update_entity(fw.id, **body.model_dump(exclude_none=True))
    after = {"status": fw.status}

    await audit.record_update(
        entity_type="competency_framework", entity_id=fw.framework_id,
        actor_id=role, actor_role=role,
        before_state=before, after_state=after,
        reason=body.model_dump(exclude_none=True).get("status", "updated"),
    )

    return CompetencyFrameworkResponse.model_validate(fw)


@router.post("/{framework_id}/competencies", response_model=CompetencyResponse, status_code=HTTP_201_CREATED)
async def add_competency(
    framework_id: str,
    body: CompetencyCreate,
    role: str = Depends(require_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    """Add a competency to a framework."""
    repo = CompetencyRepository(db)
    fw = await repo.get_by_framework_id(framework_id)
    if not fw:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Competency framework not found")

    if fw.status == "active":
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="Cannot modify an active framework")

    comp = await repo.add_competency(framework_id=fw.id, **body.model_dump())
    return CompetencyResponse.model_validate(comp)
