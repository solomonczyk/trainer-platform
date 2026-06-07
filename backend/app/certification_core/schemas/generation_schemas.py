"""Pydantic schemas for the controlled item generation pipeline.

Defines request/response schemas for generation requests, candidates,
validation results, provenance, and review handoff.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums / Literals
# ---------------------------------------------------------------------------

GENERATION_REQUEST_STATUSES = [
    "draft",
    "authorized",
    "generating",
    "generated",
    "validation_in_progress",
    "validation_failed",
    "review_handoff_ready",
    "rejected",
    "cancelled",
]

CANDIDATE_STATUSES = [
    "generated",
    "validation_failed",
    "review_handoff_ready",
    "rejected",
]

VALIDATION_DECISIONS = [
    "REJECTED",
    "VALIDATION_FAILED",
    "READY_FOR_HUMAN_REVIEW",
]

VALIDATOR_SEVERITIES = ["info", "minor", "major", "critical"]

VALIDATOR_STATUSES = ["passed", "failed", "warning", "not_run"]


# ---------------------------------------------------------------------------
# Generation Request
# ---------------------------------------------------------------------------

class GenerationRequestCreate(BaseModel):
    """Request to create a new generation request."""
    domain_id: str
    competency_id: str
    difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard|junior_basic|junior|middle|senior)$")
    locale: str = Field(default="en-US", max_length=10)
    item_family_id: str
    requested_candidate_count: int = Field(default=1, ge=1, le=3)
    trusted_source_version_ids: list[str] = []
    generation_policy_version: str = "1.0.0"
    prompt_template_version: str = "1.0.0"
    provider: str = "mock"
    model: str = "mock-model"


class GenerationRequestAuthorize(BaseModel):
    """Authorization payload for a generation request."""
    authorized_by: str


class GenerationRequestExecute(BaseModel):
    """Execution parameters for a generation request."""
    execute: bool = False
    max_candidates: int = Field(default=1, ge=1, le=3)


class GenerationRequestResponse(BaseModel):
    """Response schema for a generation request."""
    request_id: str
    requested_by_user_id: str
    requested_by_role: str
    authorized_by: Optional[str] = None
    authorized_at: Optional[datetime] = None
    domain_id: str
    competency_id: str
    difficulty: str
    locale: str
    item_family_id: str
    requested_candidate_count: int
    trusted_source_version_ids: list[str]
    generation_policy_version: str
    prompt_template_version: str
    provider: str
    model: str
    status: str
    correlation_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class GenerationRequestListResponse(BaseModel):
    """List of generation requests."""
    items: list[GenerationRequestResponse]
    total: int


# ---------------------------------------------------------------------------
# Generated Candidate (admin/reviewer view)
# ---------------------------------------------------------------------------

class GeneratedCandidateResponse(BaseModel):
    """Admin/reviewer view of a generated candidate."""
    candidate_id: str
    generation_request_id: str
    item_family_id: str
    domain_id: str
    competency_id: str
    difficulty: str
    locale: str
    item_type: str
    stem: str
    options: Optional[list] = None
    rationale: str
    source_citations: Optional[list] = None
    provider: str
    model: str
    status: str
    validation_status: str
    created_at: datetime


class GeneratedCandidateDetailResponse(GeneratedCandidateResponse):
    """Detailed view including answer_key and rubric for authorized reviewers."""
    answer_key: Optional[dict] = None
    rubric: Optional[dict] = None
    normalized_payload: Optional[dict] = None


# ---------------------------------------------------------------------------
# Learner-facing candidate schema (no answer key, no rationale, no rubric)
# ---------------------------------------------------------------------------

class LearnerFacingCandidate(BaseModel):
    """Candidate as exposed to learners — no answer key, rationale, or rubric."""
    candidate_id: str
    item_type: str
    stem: str
    options: Optional[list] = None
    locale: str
    difficulty: str


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ValidationResultEntry(BaseModel):
    """Single validator result."""
    validator_code: str
    validator_version: str
    status: str
    severity: str
    reason_code: Optional[str] = None
    details: Optional[dict] = None
    executed_at: datetime


class ValidationRunSummary(BaseModel):
    """Summary of a validation run."""
    validation_run_id: str
    candidate_id: str
    validation_policy_version: str
    total_validators: int
    passed_count: int
    failed_count: int
    warning_count: int
    not_run_count: int
    critical_failures: int
    major_failures: int
    decision: str
    results: list[ValidationResultEntry]
    started_at: datetime
    completed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

class ProvenanceResponse(BaseModel):
    """Complete provenance record."""
    provenance_id: str
    candidate_id: str
    provider: str
    model: str
    source_version_ids: list[str]
    source_checksums: list[str] = []
    prompt_template_version: str
    prompt_hash: Optional[str] = None
    generation_policy_version: str
    schema_version: str
    raw_response_hash: Optional[str] = None
    candidate_hash: str
    validator_versions: Optional[dict] = None
    correlation_id: Optional[str] = None
    request_timestamp: Optional[datetime] = None
    response_timestamp: Optional[datetime] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Review Handoff
# ---------------------------------------------------------------------------

class ReviewHandoffResponse(BaseModel):
    """Human review handoff record."""
    handoff_id: str
    candidate_id: str
    status: str
    validation_summary: Optional[dict] = None
    warnings: Optional[list] = None
    reviewer_roles_allowed: Optional[list] = None
    forbidden_actions: Optional[list] = None
    human_review_completed: bool = False
    human_accepted: bool = False
    pilot_allowed: bool = False
    exam_eligible_allowed: bool = False
    publication_allowed: bool = False
    created_at: datetime


# ---------------------------------------------------------------------------
# Forbidden action flags (for API responses)
# ---------------------------------------------------------------------------

class ForbiddenActions(BaseModel):
    exam_form_assembly: bool = False
    pilot_pool_mutation: bool = False
    exam_eligible_pool_mutation: bool = False
    generated_item_auto_publication: bool = False
    automatic_human_acceptance: bool = False
