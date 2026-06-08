"""REST API for the human review vertical layer.

Endpoints:
POST   /api/v1/certification/review-cases
GET    /api/v1/certification/review-cases
GET    /api/v1/certification/review-cases/{case_id}
POST   /api/v1/certification/review-cases/{case_id}/assign
POST   /api/v1/certification/review-cases/{case_id}/claim
POST   /api/v1/certification/review-cases/{case_id}/release
POST   /api/v1/certification/review-cases/{case_id}/decision
GET    /api/v1/certification/review-cases/{case_id}/history
GET    /api/v1/certification/review-cases/{case_id}/evidence
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
)

from app.certification_core.models.human_review_models import (
    HumanReviewCase,
    ReviewerAssignment,
    HumanReviewDecision,
)
from app.certification_core.schemas.human_review_schemas import (
    ReviewCaseCreate,
    ReviewCaseResponse,
    ReviewCaseListResponse,
    ReviewCaseDetailResponse,
    ReviewAssignRequest,
    ReviewClaimRequest,
    ReviewReleaseRequest,
    ReviewAssignmentResponse,
    ReviewDecisionSubmit,
    ReviewDecisionResponse,
    ReviewHistoryResponse,
    ReviewHistoryEntry,
)
from app.certification_core.services.authorization import (
    require_permission,
    get_current_certification_role,
    AuthorizationService,
    bearer_scheme,
)
from app.certification_core.services.human_review_service import HumanReviewService
from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/certification",
    tags=["Certification-Human-Review"],
)


# ---------------------------------------------------------------------------
# Review Cases
# ---------------------------------------------------------------------------


@router.post(
    "/review-cases",
    response_model=ReviewCaseResponse,
    status_code=201,
)
async def create_review_case(
    body: ReviewCaseCreate,
    role: str = Depends(require_permission("certification:human_review:assign")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Create a human review case from a review handoff.

    Validates handoff, candidate, provenance, validation, and source bindings.
    Idempotent: returns existing case if already created for this handoff.
    """
    actor_id = AuthorizationService.get_user_id_from_token(credentials)

    service = HumanReviewService(db)
    try:
        case = await service.create_review_case(
            handoff_id=body.handoff_id,
            review_type=body.review_type,
            actor_id=actor_id,
            actor_role=role,
        )
    except ValueError as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, str(e))

    return _case_to_response(case)


@router.get(
    "/review-cases",
    response_model=ReviewCaseListResponse,
)
async def list_review_cases(
    status: Optional[str] = Query(None),
    reviewer_user_id: Optional[str] = Query(None),
    required_reviewer_role: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: str = Depends(require_permission("certification:human_review:list")),
    db: AsyncSession = Depends(get_db),
):
    """List review cases with optional filters."""
    service = HumanReviewService(db)
    cases, total = await service.list_cases(
        status=status,
        reviewer_user_id=reviewer_user_id,
        required_reviewer_role=required_reviewer_role,
        assigned_to=assigned_to,
        skip=skip,
        limit=limit,
        actor_role=role,
    )

    return ReviewCaseListResponse(
        items=[_case_to_response(c) for c in cases],
        total=total,
    )


@router.get(
    "/review-cases/{case_id}",
    response_model=ReviewCaseDetailResponse,
)
async def get_review_case_detail(
    case_id: str,
    role: str = Depends(require_permission("certification:human_review:read")),
    db: AsyncSession = Depends(get_db),
):
    """Get full review case detail including candidate, assignments, decisions."""
    service = HumanReviewService(db)
    try:
        detail = await service.get_case_detail(case_id)
    except ValueError as e:
        raise HTTPException(HTTP_404_NOT_FOUND, str(e))

    return ReviewCaseDetailResponse(**detail)


# ---------------------------------------------------------------------------
# Assignment
# ---------------------------------------------------------------------------


@router.post(
    "/review-cases/{case_id}/assign",
    response_model=ReviewAssignmentResponse,
)
async def assign_reviewer(
    case_id: str,
    body: ReviewAssignRequest,
    role: str = Depends(require_permission("certification:human_review:assign")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Assign a human reviewer to a review case."""
    actor_id = AuthorizationService.get_user_id_from_token(credentials)

    service = HumanReviewService(db)
    try:
        assignment = await service.assign_reviewer(
            case_id=case_id,
            reviewer_user_id=body.reviewer_user_id,
            reviewer_role=body.reviewer_role,
            assigned_by=actor_id,
            assigned_by_role=role,
            reason=body.reason,
        )
    except ValueError as e:
        error_msg = str(e)
        if "active assignment already exists" in error_msg:
            raise HTTPException(HTTP_409_CONFLICT, error_msg)
        if "Self-review blocked" in error_msg:
            raise HTTPException(HTTP_403_FORBIDDEN, error_msg)
        raise HTTPException(HTTP_400_BAD_REQUEST, error_msg)

    return ReviewAssignmentResponse(
        assignment_id=assignment.assignment_id,
        review_case_id=case_id,
        reviewer_user_id=assignment.reviewer_user_id,
        reviewer_role=assignment.reviewer_role,
        status=assignment.status,
        message=f"Reviewer {assignment.reviewer_user_id} assigned to case {case_id}",
    )


@router.post(
    "/review-cases/{case_id}/claim",
    response_model=ReviewAssignmentResponse,
)
async def claim_assignment(
    case_id: str,
    body: ReviewClaimRequest,
    role: str = Depends(require_permission("certification:human_review:claim")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Claim an assignment for a review case."""
    actor_id = AuthorizationService.get_user_id_from_token(credentials)

    service = HumanReviewService(db)
    try:
        assignment = await service.claim_assignment(
            case_id=case_id,
            actor_id=actor_id,
            actor_role=role,
            reason=body.reason,
        )
    except ValueError as e:
        error_msg = str(e)
        if "No active assignment found" in error_msg:
            raise HTTPException(HTTP_404_NOT_FOUND, error_msg)
        if "blocked" in error_msg.lower():
            raise HTTPException(HTTP_403_FORBIDDEN, error_msg)
        raise HTTPException(HTTP_400_BAD_REQUEST, error_msg)

    return ReviewAssignmentResponse(
        assignment_id=assignment.assignment_id,
        review_case_id=case_id,
        reviewer_user_id=assignment.reviewer_user_id,
        reviewer_role=assignment.reviewer_role,
        status=assignment.status,
        message=f"Assignment claimed for case {case_id}",
    )


@router.post(
    "/review-cases/{case_id}/release",
    response_model=ReviewAssignmentResponse,
)
async def release_assignment(
    case_id: str,
    body: ReviewReleaseRequest,
    role: str = Depends(require_permission("certification:human_review:assign")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Release/remove a reviewer assignment from a case."""
    actor_id = AuthorizationService.get_user_id_from_token(credentials)

    if not body.reason:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            "Reason is required for releasing an assignment",
        )

    service = HumanReviewService(db)
    try:
        assignment = await service.release_assignment(
            case_id=case_id,
            actor_id=actor_id,
            actor_role=role,
            reason=body.reason,
        )
    except ValueError as e:
        error_msg = str(e)
        if "No active assignment" in error_msg:
            raise HTTPException(HTTP_404_NOT_FOUND, error_msg)
        raise HTTPException(HTTP_400_BAD_REQUEST, error_msg)

    return ReviewAssignmentResponse(
        assignment_id=assignment.assignment_id,
        review_case_id=case_id,
        reviewer_user_id=assignment.reviewer_user_id,
        reviewer_role=assignment.reviewer_role,
        status=assignment.status,
        message=f"Assignment released for case {case_id}",
    )


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------


@router.post(
    "/review-cases/{case_id}/decision",
    response_model=ReviewDecisionResponse,
)
async def submit_review_decision(
    case_id: str,
    body: ReviewDecisionSubmit,
    role: str = Depends(require_permission("certification:human_review:decide")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Submit a human review decision for a case.

    Validates that the reviewer has a claimed assignment and that
    evidence was inspected. Creates an immutable decision record.
    """
    actor_id = AuthorizationService.get_user_id_from_token(credentials)

    service = HumanReviewService(db)
    try:
        decision = await service.submit_decision(
            case_id=case_id,
            decision=body.decision,
            reason=body.reason,
            actor_id=actor_id,
            actor_role=role,
            findings_json=body.findings_json,
            evidence_confirmed=body.evidence_confirmed,
        )
    except ValueError as e:
        error_msg = str(e)
        if "already been submitted" in error_msg:
            raise HTTPException(HTTP_409_CONFLICT, error_msg)
        if ("No active claimed assignment" in error_msg
                or "Assignment must be CLAIMED" in error_msg):
            raise HTTPException(HTTP_400_BAD_REQUEST, error_msg)
        if "blocked" in error_msg.lower():
            raise HTTPException(HTTP_403_FORBIDDEN, error_msg)
        if "candidate hash mismatch" in error_msg.lower():
            raise HTTPException(HTTP_409_CONFLICT, error_msg)
        raise HTTPException(HTTP_400_BAD_REQUEST, error_msg)

    return ReviewDecisionResponse(
        decision_id=decision.decision_id,
        review_case_id=case_id,
        candidate_id=decision.candidate_id,
        decision=decision.decision,
        status="completed",
        message=f"Decision '{decision.decision}' recorded for case {case_id}",
    )


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


@router.get(
    "/review-cases/{case_id}/history",
    response_model=ReviewHistoryResponse,
)
async def get_review_history(
    case_id: str,
    role: str = Depends(require_permission("certification:human_review:audit")),
    db: AsyncSession = Depends(get_db),
):
    """Get the full audit history for a review case."""
    service = HumanReviewService(db)
    try:
        events = await service.get_review_history(case_id)
    except ValueError as e:
        raise HTTPException(HTTP_404_NOT_FOUND, str(e))

    return ReviewHistoryResponse(
        case_id=case_id,
        events=[
            ReviewHistoryEntry(**e) for e in events
        ],
    )


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


@router.get(
    "/review-cases/{case_id}/evidence",
)
async def get_review_evidence(
    case_id: str,
    role: str = Depends(require_permission("certification:human_review:read")),
    db: AsyncSession = Depends(get_db),
):
    """Get the evidence snapshot for a review case."""
    service = HumanReviewService(db)
    try:
        evidence = await service.get_evidence_snapshot(case_id)
    except ValueError as e:
        raise HTTPException(HTTP_404_NOT_FOUND, str(e))

    if not evidence:
        raise HTTPException(HTTP_404_NOT_FOUND, "Evidence not available")

    return evidence.model_dump()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _case_to_response(case: HumanReviewCase) -> ReviewCaseResponse:
    return ReviewCaseResponse(
        case_id=case.case_id,
        candidate_id=case.candidate_id,
        review_handoff_id=case.review_handoff_id,
        validation_run_id=case.validation_run_id,
        status=case.status,
        review_type=case.review_type,
        required_reviewer_role=case.required_reviewer_role,
        created_by=case.created_by,
        created_at=case.created_at,
        opened_at=case.opened_at,
        completed_at=case.completed_at,
        version=case.version,
    )
