"""API routes for Exam Blueprint management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.certification_core.schemas.blueprint_schemas import (
    ExamBlueprintCreate, ExamBlueprintUpdate, ExamBlueprintResponse,
    ExamBlueprintListResponse, BlueprintSectionCreate, BlueprintSectionResponse,
)
from app.certification_core.repositories.blueprint_repository import BlueprintRepository
from app.certification_core.validators.blueprint_validator import BlueprintValidator
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    get_current_certification_role, require_certification_permission,
)
from app.db.session import get_db

router = APIRouter(prefix="/certification-core/blueprints", tags=["Certification-Core"])


@router.get("", response_model=ExamBlueprintListResponse)
async def list_blueprints(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str = Query(None),
    domain_pack_id: str = Query(None),
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    """List exam blueprints with optional filters."""
    repo = BlueprintRepository(db)
    items, total = await repo.list_blueprints(skip=skip, limit=limit, status=status, domain_pack_id=domain_pack_id)
    return ExamBlueprintListResponse(
        items=[ExamBlueprintResponse.model_validate(bp) for bp in items],
        total=total, skip=skip, limit=limit,
    )


@router.get("/{blueprint_id}", response_model=ExamBlueprintResponse)
async def get_blueprint(
    blueprint_id: str,
    role: str = Depends(get_current_certification_role),
    db: AsyncSession = Depends(get_db),
):
    """Get an exam blueprint by its business ID."""
    repo = BlueprintRepository(db)
    bp = await repo.get_by_blueprint_id(blueprint_id)
    if not bp:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Exam blueprint not found")
    return ExamBlueprintResponse.model_validate(bp)


@router.post("", response_model=ExamBlueprintResponse, status_code=HTTP_201_CREATED)
async def create_blueprint(
    body: ExamBlueprintCreate,
    role: str = Depends(lambda: require_certification_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new exam blueprint with sections."""
    # Validate
    errors = BlueprintValidator.validate_blueprint(body.model_dump())
    if errors:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail={"validation_errors": errors})

    repo = BlueprintRepository(db)
    audit = AuditService(db)

    bp_data = body.model_dump(exclude={"sections"})
    bp = await repo.create(**bp_data)

    for sec_data in body.sections:
        await repo.add_section(blueprint_id=bp.id, **sec_data.model_dump())

    await db.refresh(bp)

    await audit.record_create(
        entity_type="exam_blueprint",
        entity_id=bp.blueprint_id,
        actor_id=body.created_by,
        actor_role=role,
        after_state={"blueprint_id": bp.blueprint_id, "version": bp.version},
    )

    return ExamBlueprintResponse.model_validate(bp)


@router.patch("/{blueprint_id}", response_model=ExamBlueprintResponse)
async def update_blueprint(
    blueprint_id: str,
    body: ExamBlueprintUpdate,
    role: str = Depends(lambda: require_certification_permission("certification:write")),
    db: AsyncSession = Depends(get_db),
):
    """Update an exam blueprint."""
    repo = BlueprintRepository(db)
    audit = AuditService(db)

    bp = await repo.get_by_blueprint_id(blueprint_id)
    if not bp:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Exam blueprint not found")

    if bp.status == "active" and body.status and body.status != "deprecated":
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="Active blueprints cannot be modified")

    before = {"status": bp.status}
    bp = await repo.update_entity(bp.id, **body.model_dump(exclude_none=True))

    await audit.record_update(
        entity_type="exam_blueprint", entity_id=bp.blueprint_id,
        actor_id=role, actor_role=role,
        before_state=before, after_state={"status": bp.status},
    )

    return ExamBlueprintResponse.model_validate(bp)
