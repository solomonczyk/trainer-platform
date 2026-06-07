"""API routes for Dynamic Item Bank Runtime — authoring, review, pools, exposure, rotation, governance."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_409_CONFLICT,
)

from app.certification_core.schemas.runtime_schemas import (
    ControlledItemCreate,
    ItemDraftUpdate,
    SourceBindingCreate,
    ReviewCreate,
    ReviewQueueResponse,
    PoolMembershipCreate,
    PoolMembershipResponse,
    PoolQueryResponse,
    ExposureEventCreate,
    ExposureEventResponse,
    ExposureCounterResponse,
    RotationPolicyCreate,
    RotationEligibilityResponse,
    GovernanceActionCreate,
    SupersessionCreate,
    GovernanceSummaryResponse,
    GovernanceIncidentResponse,
    GovernanceIncidentListResponse,
    TraceabilityResponse,
    SourceBindingResponse,
)
from app.certification_core.schemas.item_schemas import ItemResponse
from app.certification_core.repositories.item_repository import ItemRepository
from app.certification_core.services.runtime_service import (
    AuthoringService,
    ReviewService,
    PilotPoolService,
    ExamEligiblePoolService,
    ExposureService,
    RotationPolicyService,
    GovernanceService,
    SourceTraceabilityService,
)
from app.certification_core.services.authorization import (
    get_current_certification_role,
    require_permission,
    AuthorizationService,
)
from app.certification_core.audit.service import AuditService
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)
router = APIRouter(
    prefix="/certification-core/item-bank",
    tags=["Certification-Core-Item-Bank"],
)


def _get_role_and_user(credentials):
    """Extract role and user ID from credentials."""
    role = AuthorizationService.get_role_from_token(credentials)
    user_id = AuthorizationService.get_user_id_from_token(credentials)
    return role, user_id


def _filter_item_response(item, role: str) -> dict:
    """Filter out answer keys for non-admin roles."""
    from app.certification_core.schemas.item_schemas import ItemResponse
    resp = ItemResponse.model_validate(item)
    data = resp.model_dump(mode="json")
    if not AuthorizationService.can_read_answer_keys(role):
        data.pop("answer_key", None)
    return data


# ----------------------------------------------------------------
# Authoring
# ----------------------------------------------------------------

@router.post("/items", status_code=HTTP_201_CREATED)
async def create_item_draft(
    body: ControlledItemCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Create a new item draft with controlled authoring workflow."""
    role, user_id = _get_role_and_user(credentials)
    role = await require_permission("certification:write")(credentials)
    service = AuthoringService(db)
    result = await service.create_draft(body, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    item = result["item"]
    return _filter_item_response(item, role)


@router.patch("/items/{item_id}")
async def update_item_draft(
    item_id: str,
    body: ItemDraftUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Update a draft item."""
    role, user_id = _get_role_and_user(credentials)
    role = await require_permission("certification:write")(credentials)
    service = AuthoringService(db)
    update_data = body.model_dump(exclude_none=True)
    result = await service.update_draft(item_id, update_data, user_id, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return _filter_item_response(result["item"], role)


@router.post("/items/{item_id}/submit")
async def submit_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Submit an item for review after validation."""
    role, user_id = _get_role_and_user(credentials)
    role = await require_permission("certification:write")(credentials)
    service = AuthoringService(db)
    result = await service.submit_for_review(item_id, user_id, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": "Item submitted for review", "item_id": item_id}


# ----------------------------------------------------------------
# Source Binding
# ----------------------------------------------------------------

@router.post("/items/{item_id}/bind-source", status_code=HTTP_201_CREATED)
async def bind_source(
    item_id: str,
    body: SourceBindingCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Bind a knowledge source to an item with traceability snapshot."""
    role, user_id = _get_role_and_user(credentials)
    role = await require_permission("certification:write")(credentials)
    service = SourceTraceabilityService(db)
    result = await service.create_binding(item_id, body, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": "Source bound", "binding_id": result["binding"].binding_id}


@router.get("/items/{item_id}/traceability")
async def get_traceability(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get source traceability data for an item."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = SourceTraceabilityService(db)
    result = await service.get_traceability(item_id)
    # Convert to response schemas
    bindings = [SourceBindingResponse.model_validate(b) for b in result["bindings"]]
    return TraceabilityResponse(bindings=bindings, total=result["total"])


# ----------------------------------------------------------------
# Review
# ----------------------------------------------------------------

@router.get("/reviews/queue")
async def get_review_queue(
    review_stage: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get items awaiting review."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = ReviewService(db)
    result = await service.get_review_queue(review_stage=review_stage, skip=skip, limit=limit)
    return result


@router.post("/items/{item_id}/review")
async def review_item(
    item_id: str,
    body: ReviewCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Perform a review decision on an item."""
    role, user_id = _get_role_and_user(credentials)
    body.item_id = item_id
    service = ReviewService(db)
    result = await service.perform_review(body, user_id, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {
        "message": "Review recorded",
        "decision": body.decision,
        "before_status": result["before_status"],
        "after_status": result["after_status"],
    }


# ----------------------------------------------------------------
# Pilot Pool
# ----------------------------------------------------------------

@router.post("/items/{item_id}/pilot")
async def enter_pilot(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Enter an item into the pilot pool."""
    role, user_id = _get_role_and_user(credentials)
    service = PilotPoolService(db)
    result = await service.enter_pilot(item_id, user_id, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": "Item entered pilot pool", "item_id": item_id}


@router.post("/items/{item_id}/pilot/complete")
async def complete_pilot(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Complete pilot phase for an item."""
    role, user_id = _get_role_and_user(credentials)
    service = PilotPoolService(db)
    result = await service.complete_pilot(item_id, user_id, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": result["message"]}


@router.get("/pools/pilot")
async def get_pilot_pool(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Query the pilot pool."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = PilotPoolService(db)
    result = await service.get_pilot_pool(status=status, skip=skip, limit=limit)
    items = [PoolMembershipResponse.model_validate(i) for i in result["items"]]
    return PoolQueryResponse(items=items, total=result["total"], skip=skip, limit=limit)


# ----------------------------------------------------------------
# Exam-Eligible Pool
# ----------------------------------------------------------------

@router.post("/items/{item_id}/exam-eligibility")
async def grant_exam_eligibility(
    item_id: str,
    body: PoolMembershipCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Grant exam-eligible status to an item."""
    role, user_id = _get_role_and_user(credentials)
    body.item_id = item_id
    service = ExamEligiblePoolService(db)

    exception_data = None
    if body.controlled_exception:
        exception_data = {
            "reason": body.exception_reason,
            "expires_at": None,  # would come from a full ExceptionApprovalCreate schema
            "second_reviewer": user_id,
        }

    result = await service.enter_exam_eligible(
        item_id=item_id,
        entered_by=user_id,
        actor_role=role,
        controlled_exception=body.controlled_exception,
        exception_data=exception_data,
    )
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": "Item granted exam-eligible status", "item_id": item_id}


@router.get("/pools/exam-eligible")
async def get_exam_eligible_pool(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Query the exam-eligible pool."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = ExamEligiblePoolService(db)
    result = await service.get_exam_eligible_pool(status=status, skip=skip, limit=limit)
    items = [PoolMembershipResponse.model_validate(i) for i in result["items"]]
    return PoolQueryResponse(items=items, total=result["total"], skip=skip, limit=limit)


# ----------------------------------------------------------------
# Exposure
# ----------------------------------------------------------------

@router.post("/items/{item_id}/exposure", status_code=HTTP_201_CREATED)
async def record_exposure(
    item_id: str,
    body: ExposureEventCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Record an item exposure event (idempotent)."""
    role, user_id = _get_role_and_user(credentials)
    body.item_id = item_id
    service = ExposureService(db)
    result = await service.record_exposure(body, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": "Exposure recorded", "duplicate": result.get("duplicate", False)}


@router.get("/items/{item_id}/exposure")
async def get_exposure(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get exposure data for an item."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = ExposureService(db)
    result = await service.get_exposure(item_id)
    if not result["success"]:
        raise HTTPException(HTTP_404_NOT_FOUND, detail=result["message"])
    counter = ExposureCounterResponse.model_validate(result["counter"]) if result["counter"] else None
    return {"counter": counter, "total_events": result["total_events"]}


# ----------------------------------------------------------------
# Rotation
# ----------------------------------------------------------------

@router.post("/rotation/policies", status_code=HTTP_201_CREATED)
async def create_rotation_policy(
    body: RotationPolicyCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Create a rotation policy."""
    role, user_id = _get_role_and_user(credentials)
    service = RotationPolicyService(db)
    result = await service.create_policy(body, role)
    if not result["success"]:
        raise HTTPException(HTTP_403_FORBIDDEN, detail=result["message"])
    return result["policy"]


@router.get("/items/{item_id}/rotation-eligibility")
async def check_rotation_eligibility(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Check item rotation eligibility."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = RotationPolicyService(db)
    result = await service.check_eligibility(item_id)
    return result


# ----------------------------------------------------------------
# Suspension / Retirement
# ----------------------------------------------------------------

@router.post("/items/{item_id}/suspend")
async def suspend_item(
    item_id: str,
    body: GovernanceActionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Suspend an item."""
    role, user_id = _get_role_and_user(credentials)
    body.item_id = item_id
    service = GovernanceService(db)
    result = await service.suspend(body, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": result["message"]}


@router.post("/items/{item_id}/unsuspend")
async def unsuspend_item(
    item_id: str,
    body: GovernanceActionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Unsuspend an item."""
    role, user_id = _get_role_and_user(credentials)
    body.item_id = item_id
    service = GovernanceService(db)
    result = await service.unsuspend(body, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": result["message"]}


@router.post("/items/{item_id}/retire")
async def retire_item(
    item_id: str,
    body: GovernanceActionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Retire an item."""
    role, user_id = _get_role_and_user(credentials)
    body.item_id = item_id
    service = GovernanceService(db)
    result = await service.retire(body, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": result["message"]}


@router.post("/items/{item_id}/supersede")
async def supersede_item(
    item_id: str,
    body: SupersessionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Supersede an item with a successor."""
    role, user_id = _get_role_and_user(credentials)
    body.predecessor_item_id = item_id
    service = GovernanceService(db)
    result = await service.supersede(body, role)
    if not result["success"]:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=result["message"])
    return {"message": "Item superseded", "link_id": result["link"].supersession_id}


# ----------------------------------------------------------------
# Governance
# ----------------------------------------------------------------

@router.get("/governance/summary")
async def get_governance_summary(
    domain_pack_id: Optional[str] = Query(None),
    locale: Optional[str] = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get governance summary statistics."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = GovernanceService(db)
    return await service.get_governance_summary(domain_pack_id=domain_pack_id, locale=locale)


@router.get("/governance/incidents")
async def list_governance_incidents(
    incident_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """List governance incidents."""
    role = AuthorizationService.get_role_from_token(credentials)
    service = GovernanceService(db)
    result = await service.list_incidents(
        incident_type=incident_type, status=status, skip=skip, limit=limit,
    )
    items = [GovernanceIncidentResponse.model_validate(i) for i in result["items"]]
    return GovernanceIncidentListResponse(
        items=items, total=result["total"], skip=skip, limit=limit,
    )
