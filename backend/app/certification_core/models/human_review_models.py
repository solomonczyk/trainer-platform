"""Human review models — review cases, reviewer assignments, human review decisions.

Extends the certification-grade core with the human review vertical layer.
All tables use the 'cert_' prefix and are append-only for decisions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON,
    UniqueConstraint, Index, CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Review case statuses
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

# Roles eligible for human review (must also exist in authorization.py)
ELIGIBLE_REVIEWER_ROLES = [
    "expert_reviewer",
    "psychometric_reviewer",
    "domain_owner",
    "qa_reviewer",
    "platform_admin",
]

# Roles that are PROHIBITED from performing human review
PROHIBITED_REVIEWER_ROLES = [
    "generation_operator",
    "content_author",
    "read_only_auditor",
    "learner",
    "guest",
    "llm",
    "service_account",
]

# Roles that are blocked from self-reviewing their own work
SELF_REVIEW_BLOCKED_ROLES = [
    "generation_operator",
    "content_author",
    "domain_owner",
]


# ---------------------------------------------------------------------------
# Human review case
# ---------------------------------------------------------------------------

class HumanReviewCase(Base, TimestampMixin):
    """A persistent human review case for a generated candidate.

    Created from a valid review handoff. Tracks the review lifecycle from
    pending assignment through decision.
    """

    __tablename__ = "cert_human_review_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generated_candidates.id"),
        nullable=False, index=True
    )
    review_handoff_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_candidate_review_handoffs.id"),
        nullable=False, index=True
    )
    validation_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_candidate_validation_runs.id"),
        nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="PENDING_ASSIGNMENT", index=True, nullable=False
    )
    review_type: Mapped[str] = mapped_column(
        String(30), default="expert_review", nullable=False
    )
    required_reviewer_role: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    candidate = relationship(
        "GeneratedCandidate", lazy="selectin"
    )
    review_handoff = relationship(
        "CandidateReviewHandoff", lazy="selectin"
    )
    validation_run = relationship(
        "CandidateValidationRun", lazy="selectin"
    )
    assignments = relationship(
        "ReviewerAssignment", back_populates="review_case",
        cascade="all, delete-orphan", lazy="selectin"
    )
    decisions = relationship(
        "HumanReviewDecision", back_populates="review_case",
        cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_hrc_status", "status"),
        Index("idx_hrc_candidate", "candidate_id"),
        Index("idx_hrc_reviewer_role", "required_reviewer_role"),
        Index("idx_hrc_created", "created_at"),
        Index("idx_hrc_status_created", "status", "created_at"),
    )


# ---------------------------------------------------------------------------
# Reviewer assignment
# ---------------------------------------------------------------------------

class ReviewerAssignment(Base, TimestampMixin):
    """An assignment of a human reviewer to a review case.

    Only one active assignment per case is allowed (enforced by a partial
    unique index on (review_case_id) WHERE status IN ('ASSIGNED', 'CLAIMED')).
    """

    __tablename__ = "cert_reviewer_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    assignment_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    review_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_human_review_cases.id"),
        nullable=False, index=True
    )
    reviewer_user_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    reviewer_role: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_by: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    claimed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    released_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="ASSIGNED", index=True, nullable=False
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    review_case = relationship("HumanReviewCase", back_populates="assignments")

    __table_args__ = (
        Index("idx_ra_case", "review_case_id"),
        Index("idx_ra_reviewer", "reviewer_user_id"),
        Index("idx_ra_status", "status"),
        Index("idx_ra_case_status", "review_case_id", "status"),
    )


# ---------------------------------------------------------------------------
# Human review decision (append-only)
# ---------------------------------------------------------------------------

class HumanReviewDecision(Base):
    """An immutable human review decision record.

    Decisions are append-only: once created, they must not be updated or
    deleted. Each decision represents a single review action.
    """

    __tablename__ = "cert_human_review_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    decision_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    review_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_human_review_cases.id"),
        nullable=False, index=True
    )
    assignment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_reviewer_assignments.id"),
        nullable=False, index=True
    )
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generated_candidates.id"),
        nullable=False, index=True
    )
    reviewer_user_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    reviewer_role: Mapped[str] = mapped_column(String(50), nullable=False)
    decision: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    findings_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evidence_snapshot_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    candidate_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    validation_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_candidate_validation_runs.id"),
        nullable=False, index=True
    )
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    review_case = relationship("HumanReviewCase", back_populates="decisions")

    __table_args__ = (
        Index("idx_hrd_case", "review_case_id"),
        Index("idx_hrd_reviewer", "reviewer_user_id"),
        Index("idx_hrd_decision", "decision"),
        Index("idx_hrd_created", "created_at"),
        Index("idx_hrd_candidate", "candidate_id"),
    )
