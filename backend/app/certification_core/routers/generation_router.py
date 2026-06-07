"""REST API for the controlled item generation pipeline.

Endpoints:
POST   /api/v1/certification/generation/requests
GET    /api/v1/certification/generation/requests/{request_id}
POST   /api/v1/certification/generation/requests/{request_id}/authorize
POST   /api/v1/certification/generation/requests/{request_id}/execute
GET    /api/v1/certification/generation/requests/{request_id}/candidates
GET    /api/v1/certification/generated-candidates/{candidate_id}
GET    /api/v1/certification/generated-candidates/{candidate_id}/validation
GET    /api/v1/certification/generated-candidates/{candidate_id}/provenance
GET    /api/v1/certification/generated-candidates/{candidate_id}/review-handoff

Forbidden endpoints (not implemented):
publish, approve, pilot, exam-eligible, assemble-exam, production-accept
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.certification_core.models.generation_models import (
    GenerationRequest,
    GeneratedCandidate,
    CandidateValidationRun,
    CandidateValidationResult,
    CandidateProvenance,
    CandidateReviewHandoff,
    GenerationSourceBinding,
    GenerationRawResponse,
)
from app.certification_core.schemas.generation_schemas import (
    GenerationRequestCreate,
    GenerationRequestAuthorize,
    GenerationRequestExecute,
    GenerationRequestResponse,
    GenerationRequestListResponse,
    GeneratedCandidateResponse,
    GeneratedCandidateDetailResponse,
    ValidationRunSummary,
    ValidationResultEntry,
    ProvenanceResponse,
    ReviewHandoffResponse,
    LearnerFacingCandidate,
    ForbiddenActions,
)
from app.certification_core.services.authorization import (
    require_permission,
    get_current_certification_role,
    AuthorizationService,
    bearer_scheme,
)
from app.certification_core.services.generation_service import GenerationService
from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/certification", tags=["Certification-Generation"])


# ---------------------------------------------------------------------------
# Generation Requests
# ---------------------------------------------------------------------------

@router.post("/generation/requests", response_model=GenerationRequestResponse)
async def create_generation_request(
    body: GenerationRequestCreate,
    role: str = Depends(require_permission("certification:generation:create")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Create a new generation request in draft status."""
    user_id = AuthorizationService.get_user_id_from_token(credentials)

    service = GenerationService(db)
    gen_request = await service.create_request(
        requested_by_user_id=user_id,
        requested_by_role=role,
        domain_id=body.domain_id,
        competency_id=body.competency_id,
        difficulty=body.difficulty,
        locale=body.locale,
        item_family_id=body.item_family_id,
        requested_candidate_count=body.requested_candidate_count,
        trusted_source_version_ids=body.trusted_source_version_ids,
        generation_policy_version=body.generation_policy_version,
        prompt_template_version=body.prompt_template_version,
        provider=body.provider,
        model=body.model,
    )

    return _request_to_response(gen_request)


@router.get("/generation/requests/{request_id}", response_model=GenerationRequestResponse)
async def get_generation_request(
    request_id: str,
    role: str = Depends(require_permission("certification:generation:view")),
    db: AsyncSession = Depends(get_db),
):
    """Get a generation request by ID."""
    result = await db.execute(
        select(GenerationRequest).where(GenerationRequest.request_id == request_id)
    )
    gen_request = result.scalar_one_or_none()
    if not gen_request:
        raise HTTPException(HTTP_404_NOT_FOUND, "Generation request not found")
    return _request_to_response(gen_request)


@router.post("/generation/requests/{request_id}/authorize", response_model=GenerationRequestResponse)
async def authorize_generation_request(
    request_id: str,
    body: GenerationRequestAuthorize,
    role: str = Depends(require_permission("certification:generation:authorize")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Authorize a generation request.

    Requester self-authorization is blocked at the service layer.
    """
    user_id = AuthorizationService.get_user_id_from_token(credentials)

    service = GenerationService(db)
    gen_request = await service.authorize_request(
        request_id=request_id,
        authorized_by=user_id,
        authorized_role=role,
    )
    return _request_to_response(gen_request)


@router.post("/generation/requests/{request_id}/execute", response_model=dict)
async def execute_generation_request(
    request_id: str,
    body: GenerationRequestExecute,
    role: str = Depends(require_permission("certification:generation:execute")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Execute controlled generation.

    Requires --execute=True flag. Without it, returns preflight info.
    """
    if not body.execute:
        # Dry-run / preflight mode
        result = await db.execute(
            select(GenerationRequest).where(GenerationRequest.request_id == request_id)
        )
        gen_request = result.scalar_one_or_none()
        if not gen_request:
            raise HTTPException(HTTP_404_NOT_FOUND, "Generation request not found")

        return {
            "mode": "dry_run",
            "request_id": request_id,
            "status": gen_request.status,
            "max_candidates": body.max_candidates,
            "preflight_checks": {
                "request_status_valid": gen_request.status == "authorized",
                "provider_configured": bool(gen_request.provider),
                "max_candidates_valid": 1 <= body.max_candidates <= 3,
            },
            "message": "Preflight mode. Pass --execute=True to run generation.",
        }

    user_id = AuthorizationService.get_user_id_from_token(credentials)

    # Bind sources if not already bound
    service = GenerationService(db)
    _bind_sources_if_needed(service, request_id)

    candidates = await service.execute_generation(
        request_id=request_id,
        actor_id=user_id,
        actor_role=role,
        max_candidates=body.max_candidates,
    )

    return {
        "mode": "executed",
        "request_id": request_id,
        "candidates_generated": len(candidates),
        "candidates": [
            {
                "candidate_id": c.candidate_id,
                "status": c.status,
                "validation_status": c.validation_status,
                "decision": await _get_validation_decision(db, c.id),
            }
            for c in candidates
        ],
        "forbidden_actions": ForbiddenActions().model_dump(),
    }


@router.get("/generation/requests/{request_id}/candidates", response_model=list[GeneratedCandidateResponse])
async def get_generation_candidates(
    request_id: str,
    role: str = Depends(require_permission("certification:generation:view")),
    db: AsyncSession = Depends(get_db),
):
    """Get all candidates for a generation request."""
    result = await db.execute(
        select(GenerationRequest).where(GenerationRequest.request_id == request_id)
    )
    gen_request = result.scalar_one_or_none()
    if not gen_request:
        raise HTTPException(HTTP_404_NOT_FOUND, "Generation request not found")

    cand_result = await db.execute(
        select(GeneratedCandidate).where(
            GeneratedCandidate.generation_request_id == gen_request.id
        )
    )
    candidates = cand_result.scalars().all()

    return [_candidate_to_response(c) for c in candidates]


# ---------------------------------------------------------------------------
# Generated Candidates
# ---------------------------------------------------------------------------

@router.get("/generated-candidates/{candidate_id}", response_model=GeneratedCandidateDetailResponse)
async def get_generated_candidate(
    candidate_id: str,
    role: str = Depends(require_permission("certification:generation:view")),
    credentials=Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get a generated candidate with full details (admin/reviewer view)."""
    result = await db.execute(
        select(GeneratedCandidate).where(GeneratedCandidate.candidate_id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(HTTP_404_NOT_FOUND, "Candidate not found")

    return _candidate_to_detail_response(candidate)


@router.get("/generated-candidates/{candidate_id}/validation", response_model=ValidationRunSummary)
async def get_candidate_validation(
    candidate_id: str,
    role: str = Depends(require_permission("certification:generation:view")),
    db: AsyncSession = Depends(get_db),
):
    """Get validation results for a candidate."""
    result = await db.execute(
        select(GeneratedCandidate).where(GeneratedCandidate.candidate_id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(HTTP_404_NOT_FOUND, "Candidate not found")

    vr_result = await db.execute(
        select(CandidateValidationRun).where(
            CandidateValidationRun.candidate_id == candidate.id
        ).order_by(CandidateValidationRun.created_at.desc()).limit(1)
    )
    validation_run = vr_result.scalar_one_or_none()
    if not validation_run:
        raise HTTPException(HTTP_404_NOT_FOUND, "No validation run found for candidate")

    # Get results
    res_result = await db.execute(
        select(CandidateValidationResult).where(
            CandidateValidationResult.validation_run_id == validation_run.id
        )
    )
    results = res_result.scalars().all()

    return ValidationRunSummary(
        validation_run_id=validation_run.validation_run_id,
        candidate_id=candidate.candidate_id,
        validation_policy_version=validation_run.validation_policy_version,
        total_validators=validation_run.total_validators,
        passed_count=validation_run.passed_count,
        failed_count=validation_run.failed_count,
        warning_count=validation_run.warning_count,
        not_run_count=validation_run.not_run_count,
        critical_failures=validation_run.critical_failures,
        major_failures=validation_run.major_failures,
        decision=validation_run.decision,
        results=[
            ValidationResultEntry(
                validator_code=r.validator_code,
                validator_version=r.validator_version,
                status=r.status,
                severity=r.severity,
                reason_code=r.reason_code,
                details=r.details,
                executed_at=r.executed_at,
            )
            for r in results
        ],
        started_at=validation_run.started_at,
        completed_at=validation_run.completed_at,
    )


@router.get("/generated-candidates/{candidate_id}/provenance", response_model=ProvenanceResponse)
async def get_candidate_provenance(
    candidate_id: str,
    role: str = Depends(require_permission("certification:generation:view")),
    db: AsyncSession = Depends(get_db),
):
    """Get the complete provenance record for a candidate."""
    result = await db.execute(
        select(GeneratedCandidate).where(GeneratedCandidate.candidate_id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(HTTP_404_NOT_FOUND, "Candidate not found")

    prov_result = await db.execute(
        select(CandidateProvenance).where(
            CandidateProvenance.candidate_id == candidate.id
        )
    )
    provenance = prov_result.scalar_one_or_none()
    if not provenance:
        raise HTTPException(HTTP_404_NOT_FOUND, "Provenance not found for candidate")

    return ProvenanceResponse(
        provenance_id=provenance.provenance_id,
        candidate_id=candidate.candidate_id,
        provider=provenance.provider,
        model=provenance.model,
        source_version_ids=provenance.source_version_ids or [],
        source_checksums=provenance.source_checksums or [],
        prompt_template_version=provenance.prompt_template_version,
        prompt_hash=provenance.prompt_hash,
        generation_policy_version=provenance.generation_policy_version,
        schema_version=provenance.schema_version,
        raw_response_hash=provenance.raw_response_hash,
        candidate_hash=provenance.candidate_hash,
        validator_versions=provenance.validator_versions,
        correlation_id=provenance.correlation_id,
        request_timestamp=provenance.request_timestamp,
        response_timestamp=provenance.response_timestamp,
        created_at=provenance.created_at,
    )


@router.get("/generated-candidates/{candidate_id}/review-handoff", response_model=ReviewHandoffResponse)
async def get_candidate_review_handoff(
    candidate_id: str,
    role: str = Depends(require_permission("certification:generation:view")),
    db: AsyncSession = Depends(get_db),
):
    """Get the review handoff record for a candidate."""
    result = await db.execute(
        select(GeneratedCandidate).where(GeneratedCandidate.candidate_id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(HTTP_404_NOT_FOUND, "Candidate not found")

    ho_result = await db.execute(
        select(CandidateReviewHandoff).where(
            CandidateReviewHandoff.candidate_id == candidate.id
        )
    )
    handoff = ho_result.scalar_one_or_none()
    if not handoff:
        raise HTTPException(HTTP_404_NOT_FOUND, "No review handoff created for this candidate")

    return ReviewHandoffResponse(
        handoff_id=handoff.handoff_id,
        candidate_id=candidate.candidate_id,
        status=handoff.status,
        validation_summary=handoff.validation_summary,
        warnings=handoff.warnings,
        reviewer_roles_allowed=handoff.reviewer_roles_allowed,
        forbidden_actions=handoff.forbidden_actions,
        human_review_completed=handoff.human_review_completed,
        human_accepted=handoff.human_accepted,
        pilot_allowed=handoff.pilot_allowed,
        exam_eligible_allowed=handoff.exam_eligible_allowed,
        publication_allowed=handoff.publication_allowed,
        created_at=handoff.created_at,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _bind_sources_if_needed(service: GenerationService, request_id: str):
    """Bind source references if not already bound (helper for execution)."""
    # This is a simplified version — in production, actual KnowledgeSource records
    # would be looked up by version IDs
    pass


async def _get_validation_decision(db: AsyncSession, candidate_db_id: str) -> str:
    """Get the latest validation decision for a candidate."""
    result = await db.execute(
        select(CandidateValidationRun).where(
            CandidateValidationRun.candidate_id == candidate_db_id
        ).order_by(CandidateValidationRun.created_at.desc()).limit(1)
    )
    vr = result.scalar_one_or_none()
    return vr.decision if vr else "pending"


def _request_to_response(req: GenerationRequest) -> GenerationRequestResponse:
    return GenerationRequestResponse(
        request_id=req.request_id,
        requested_by_user_id=req.requested_by_user_id,
        requested_by_role=req.requested_by_role,
        authorized_by=req.authorized_by,
        authorized_at=req.authorized_at,
        domain_id=req.domain_id,
        competency_id=req.competency_id,
        difficulty=req.difficulty,
        locale=req.locale,
        item_family_id=req.item_family_id,
        requested_candidate_count=req.requested_candidate_count,
        trusted_source_version_ids=req.trusted_source_version_ids or [],
        generation_policy_version=req.generation_policy_version,
        prompt_template_version=req.prompt_template_version,
        provider=req.provider,
        model=req.model,
        status=req.status,
        correlation_id=req.correlation_id,
        error_message=req.error_message,
        created_at=req.created_at,
        updated_at=req.updated_at,
    )


def _candidate_to_response(c: GeneratedCandidate) -> GeneratedCandidateResponse:
    return GeneratedCandidateResponse(
        candidate_id=c.candidate_id,
        generation_request_id=c.generation_request_id,
        item_family_id=c.item_family_id,
        domain_id=c.domain_id,
        competency_id=c.competency_id,
        difficulty=c.difficulty,
        locale=c.locale,
        item_type=c.item_type,
        stem=c.stem,
        options=c.options,
        rationale=c.rationale,
        source_citations=c.source_citations,
        provider=c.provider,
        model=c.model,
        status=c.status,
        validation_status=c.validation_status,
        created_at=c.created_at,
    )


def _candidate_to_detail_response(c: GeneratedCandidate) -> GeneratedCandidateDetailResponse:
    return GeneratedCandidateDetailResponse(
        candidate_id=c.candidate_id,
        generation_request_id=c.generation_request_id,
        item_family_id=c.item_family_id,
        domain_id=c.domain_id,
        competency_id=c.competency_id,
        difficulty=c.difficulty,
        locale=c.locale,
        item_type=c.item_type,
        stem=c.stem,
        options=c.options,
        rationale=c.rationale,
        source_citations=c.source_citations,
        provider=c.provider,
        model=c.model,
        status=c.status,
        validation_status=c.validation_status,
        created_at=c.created_at,
        answer_key=c.answer_key,
        rubric=c.rubric,
        normalized_payload=c.normalized_payload,
    )
