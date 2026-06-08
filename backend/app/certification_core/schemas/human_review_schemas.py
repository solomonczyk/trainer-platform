"""Pydantic schemas for the human review vertical layer.

Defines request/response schemas for review cases, assignments,
decisions, evidence snapshots, and review history.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

REVIEW_CASE_STATUSES = [
    "PENDING_ASSIGNMENT",
    "ASSIGNED",
    "IN_REVIEW",
    "CHANGES_REQUESTED",
    "REJECTED",
    "APPROVED_FOR_PILOT_REVIEW",
    "ESCALATED",
    "CLOSED",
]

REVIEW_DECISIONS = [
    "APPROVED_FOR_PILOT_REVIEW",
    "REJECTED",
    "CHANGES_REQUESTED",
    "ESCALATED",
]

ASSIGNMENT_STATUSES = [
    "ASSIGNED",
    "CLAIMED",
    "RELEASED",
    "COMPLETED",
]


# ---------------------------------------------------------------------------
# Review case creation
# ---------------------------------------------------------------------------

class ReviewCaseCreate(BaseModel):
    """Request to create a new review case from a handoff."""
    handoff_id: str
    review_type: str = Field(default="expert_review")


class ReviewCaseResponse(BaseModel):
    """Response schema for a review case."""
    case_id: str
    candidate_id: str
    review_handoff_id: str
    validation_run_id: str
    status: str
    review_type: str
    required_reviewer_role: str
    created_by: str
    created_at: datetime
    opened_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    version: int


class ReviewCaseListResponse(BaseModel):
    """List of review cases with pagination."""
    items: list[ReviewCaseResponse]
    total: int


# ---------------------------------------------------------------------------
# Review case detail (includes candidate info and assignments)
# ---------------------------------------------------------------------------

class AssignmentSummary(BaseModel):
    """Summary of a reviewer assignment."""
    assignment_id: str
    reviewer_user_id: str
    reviewer_role: str
    assigned_by: str
    assigned_at: datetime
    claimed_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    status: str
    reason: Optional[str] = None


class DecisionSummary(BaseModel):
    """Summary of a review decision for history display."""
    decision_id: str
    decision: str
    reviewer_user_id: str
    reviewer_role: str
    reason: str
    findings_json: Optional[dict] = None
    candidate_hash: str
    correlation_id: Optional[str] = None
    created_at: datetime


class ReviewCaseDetailResponse(BaseModel):
    """Full review case detail with assignments and decisions."""
    case_id: str
    candidate_id: str
    review_handoff_id: str
    validation_run_id: str
    status: str
    review_type: str
    required_reviewer_role: str
    created_by: str
    created_at: datetime
    opened_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    version: int
    candidate: Optional[dict] = None
    assignments: list[AssignmentSummary] = []
    decisions: list[DecisionSummary] = []


# ---------------------------------------------------------------------------
# Assignment
# ---------------------------------------------------------------------------

class ReviewAssignRequest(BaseModel):
    """Request to assign a reviewer to a case."""
    reviewer_user_id: str
    reviewer_role: str
    reason: Optional[str] = None


class ReviewClaimRequest(BaseModel):
    """Request to claim an assignment (reviewer claims their own)."""
    reason: Optional[str] = None


class ReviewReleaseRequest(BaseModel):
    """Request to release/remove a reviewer from a case."""
    reason: str


class ReviewAssignmentResponse(BaseModel):
    """Response after an assignment action."""
    assignment_id: str
    review_case_id: str
    reviewer_user_id: str
    reviewer_role: str
    status: str
    message: str


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------

class ReviewDecisionSubmit(BaseModel):
    """Submit a review decision."""
    decision: str = Field(
        ..., pattern=r"^(APPROVED_FOR_PILOT_REVIEW|REJECTED|CHANGES_REQUESTED|ESCALATED)$"
    )
    reason: str = Field(..., min_length=1)
    findings_json: Optional[dict] = None
    evidence_confirmed: bool = False


class ReviewDecisionResponse(BaseModel):
    """Response after a decision submission."""
    decision_id: str
    review_case_id: str
    candidate_id: str
    decision: str
    status: str
    message: str


# ---------------------------------------------------------------------------
# Evidence snapshot
# ---------------------------------------------------------------------------

class EvidenceSnapshot(BaseModel):
    """Evidence snapshot for a candidate during review."""
    candidate_id: str
    candidate_hash: str
    generation_request_id: Optional[str] = None
    validation_run_id: Optional[str] = None
    validation_decision: Optional[str] = None
    validator_versions: Optional[dict] = None
    provenance: Optional[dict] = None
    source_bindings: Optional[list] = None
    citations: Optional[list] = None
    duplicate_detection: Optional[dict] = None
    safety_gate: Optional[dict] = None
    review_handoff_id: Optional[str] = None
    review_handoff_status: Optional[str] = None


# ---------------------------------------------------------------------------
# History / Audit
# ---------------------------------------------------------------------------

class ReviewHistoryEntry(BaseModel):
    """A single event in the review case history."""
    event_type: str
    actor_id: str
    actor_role: Optional[str] = None
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    reason: Optional[str] = None
    correlation_id: Optional[str] = None
    decision_id: Optional[str] = None
    event_timestamp: datetime


class ReviewHistoryResponse(BaseModel):
    """Review case history."""
    case_id: str
    events: list[ReviewHistoryEntry]


# ---------------------------------------------------------------------------
# Queue filters
# ---------------------------------------------------------------------------

class ReviewQueueFilter(BaseModel):
    """Filters for the review queue."""
    status: Optional[str] = None
    reviewer_user_id: Optional[str] = None
    required_reviewer_role: Optional[str] = None
    assigned_to: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    skip: int = 0
    limit: int = 20
