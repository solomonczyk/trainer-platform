"""Controlled Item Generation models — generation requests, candidates, validation, provenance, review handoff.

Extends the certification-grade core with controlled generation pipeline entities.
All tables use the 'cert_' prefix to namespace against BA/QA tables.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
    UniqueConstraint, Index, CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class GenerationRequest(Base, TimestampMixin):
    """Authoritative generation request contract.

    Tracks the full lifecycle of a controlled generation request from draft
    through generation, validation, and handoff for human review.
    """

    __tablename__ = "cert_generation_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    request_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    requested_by_user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    requested_by_role: Mapped[str] = mapped_column(String(50), nullable=False)
    authorized_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    authorized_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    domain_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    competency_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False)
    item_family_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    requested_candidate_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    trusted_source_version_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    generation_policy_version: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt_template_version: Mapped[str] = mapped_column(String(20), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="draft", index=True, nullable=False,
    )
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    candidates = relationship(
        "GeneratedCandidate", back_populates="generation_request",
        cascade="all, delete-orphan", lazy="selectin"
    )
    source_bindings = relationship(
        "GenerationSourceBinding", back_populates="generation_request",
        cascade="all, delete-orphan", lazy="selectin"
    )
    provider_runs = relationship(
        "GenerationProviderRun", back_populates="generation_request",
        cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_gr_status", "status"),
        Index("idx_gr_requested_by", "requested_by_user_id"),
        Index("idx_gr_domain_competency", "domain_id", "competency_id"),
    )


class GenerationSourceBinding(Base, TimestampMixin):
    """Immutable source version snapshot bound to a generation request."""

    __tablename__ = "cert_generation_source_bindings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    binding_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    generation_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generation_requests.id"), nullable=False, index=True
    )
    source_version_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    source_title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_locale: Mapped[str] = mapped_column(String(10), nullable=False)
    source_status: Mapped[str] = mapped_column(String(20), default="active")
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    retrieval_method: Mapped[str] = mapped_column(String(50), default="registry")
    context_fragment_hashes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    generation_request = relationship("GenerationRequest", back_populates="source_bindings")

    __table_args__ = (
        Index("idx_gsb_request", "generation_request_id"),
        Index("idx_gsb_source", "source_version_id"),
    )


class GenerationProviderRun(Base, TimestampMixin):
    """Records a single provider invocation during a generation request."""

    __tablename__ = "cert_generation_provider_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    generation_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generation_requests.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_request_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_response_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    prompt_package_system_prompt_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    prompt_package_context_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    prompt_package_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    generation_request = relationship("GenerationRequest", back_populates="provider_runs")
    raw_response = relationship(
        "GenerationRawResponse", back_populates="provider_run",
        uselist=False, cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_gpr_request", "generation_request_id"),
    )


class GenerationRawResponse(Base, TimestampMixin):
    """Restricted-access raw provider response storage.

    The raw response is stored separately and access is restricted to authorized
    roles (platform_admin, qa_reviewer). It is never exposed to learners.
    """

    __tablename__ = "cert_generation_raw_responses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    provider_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generation_provider_runs.id"),
        unique=True, nullable=False, index=True
    )
    raw_response: Mapped[dict] = mapped_column(JSON, nullable=False)
    reasoning_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_response_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    response_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    secret_material_absent: Mapped[bool] = mapped_column(Boolean, default=True)

    provider_run = relationship("GenerationProviderRun", back_populates="raw_response")


class GeneratedCandidate(Base, TimestampMixin):
    """A normalized generated candidate item.

    This is the core artifact of the generation pipeline. The candidate is
    validated, has provenance recorded, and may proceed to human review handoff.
    It cannot enter pilot or exam-eligible pools in this layer.
    """

    __tablename__ = "cert_generated_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    candidate_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    generation_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generation_requests.id"), nullable=False, index=True
    )
    provider_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("cert_generation_provider_runs.id"), nullable=True, index=True
    )
    item_family_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    domain_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    competency_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    answer_key: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    rationale: Mapped[str] = mapped_column(Text, default="")
    rubric: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    source_citations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_request_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    raw_response_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    normalized_payload_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    normalized_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default="generated", index=True, nullable=False,
    )
    validation_status: Mapped[str] = mapped_column(String(30), default="pending")

    generation_request = relationship("GenerationRequest", back_populates="candidates")
    validation_runs = relationship(
        "CandidateValidationRun", back_populates="candidate",
        cascade="all, delete-orphan", lazy="selectin"
    )
    provenance = relationship(
        "CandidateProvenance", back_populates="candidate",
        uselist=False, cascade="all, delete-orphan",
    )
    review_handoff = relationship(
        "CandidateReviewHandoff", back_populates="candidate",
        uselist=False, cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_gc_request", "generation_request_id"),
        Index("idx_gc_status", "status"),
        Index("idx_gc_competency", "competency_id"),
        Index("idx_gc_difficulty", "difficulty"),
    )


class CandidateValidationRun(Base, TimestampMixin):
    """A validation run containing all validator results for a candidate."""

    __tablename__ = "cert_candidate_validation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    validation_run_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generated_candidates.id"), nullable=False, index=True
    )
    validation_policy_version: Mapped[str] = mapped_column(String(20), nullable=False)
    total_validators: Mapped[int] = mapped_column(Integer, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    not_run_count: Mapped[int] = mapped_column(Integer, default=0)
    critical_failures: Mapped[int] = mapped_column(Integer, default=0)
    major_failures: Mapped[int] = mapped_column(Integer, default=0)
    decision: Mapped[str] = mapped_column(
        String(30), default="pending"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    candidate = relationship("GeneratedCandidate", back_populates="validation_runs")
    results = relationship(
        "CandidateValidationResult", back_populates="validation_run",
        cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_cvr_candidate", "candidate_id"),
    )


class CandidateValidationResult(Base, TimestampMixin):
    """Individual validator result for a candidate."""

    __tablename__ = "cert_candidate_validation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    validation_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_candidate_validation_runs.id"),
        nullable=False, index=True
    )
    validator_code: Mapped[str] = mapped_column(String(10), nullable=False)
    validator_version: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    reason_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    validation_run = relationship("CandidateValidationRun", back_populates="results")


class CandidateProvenance(Base, TimestampMixin):
    """Complete lineage record for a generated candidate — append-only."""

    __tablename__ = "cert_candidate_provenance"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    provenance_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generated_candidates.id"),
        unique=True, nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    source_version_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    source_checksums: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    prompt_template_version: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    generation_policy_version: Mapped[str] = mapped_column(String(20), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_response_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    candidate_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    validator_versions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    request_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    response_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    candidate = relationship("GeneratedCandidate", back_populates="provenance")


class CandidateReviewHandoff(Base, TimestampMixin):
    """Formal human review handoff record for a validated candidate.

    The handoff is created only after a candidate passes required validation.
    No decision workflow beyond handoff creation is implemented in this layer.
    """

    __tablename__ = "cert_candidate_review_handoffs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    handoff_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_generated_candidates.id"),
        unique=True, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="pending_human_review", nullable=False
    )
    validation_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    warnings: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    reviewer_roles_allowed: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    forbidden_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    human_review_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    human_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pilot_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    exam_eligible_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    publication_allowed: Mapped[bool] = mapped_column(Boolean, default=False)

    candidate = relationship("GeneratedCandidate", back_populates="review_handoff")

    __table_args__ = (
        Index("idx_crh_status", "status"),
        Index("idx_crh_candidate", "candidate_id"),
    )
