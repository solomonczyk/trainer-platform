"""Dynamic Item Bank Runtime models — source bindings, reviews, pools, exposure, rotation, governance.

Extends the certification-grade core contracts with operational runtime entities.
All tables use the 'cert_' prefix to namespace against BA/QA tables.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
    UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class ItemSourceBinding(Base, TimestampMixin):
    """Persistent traceability snapshot linking an item version to its knowledge sources.

    Saved at submission time so future source changes do not erase the evidence
    used when the item was reviewed.
    """

    __tablename__ = "cert_item_source_bindings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    binding_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    # Source registry snapshot
    source_registry_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_version_id: Mapped[str] = mapped_column(String(50), nullable=False)
    source_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    source_title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_uri: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source_section_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    retrieved_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    domain_pack_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_status_at_binding: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="active"
    )
    binding_actor: Mapped[str] = mapped_column(String(100), nullable=False)
    binding_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_isb_item", "item_id"),
        Index("idx_isb_source", "source_registry_id", "source_version_id"),
    )


class ItemReview(Base, TimestampMixin):
    """An item review record — each reviewer interaction creates one review entry."""

    __tablename__ = "cert_item_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    review_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    item_version: Mapped[int] = mapped_column(Integer, nullable=False)
    review_stage: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # expert_review, qa_review, psychometric_review
    reviewer_id: Mapped[str] = mapped_column(String(100), nullable=False)
    reviewer_role: Mapped[str] = mapped_column(String(50), nullable=False)
    decision: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # approve, reject, request_changes, suspend
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_irev_item", "item_id"),
        Index("idx_irev_stage", "review_stage"),
        Index("idx_irev_reviewer", "reviewer_id"),
    )


class ItemReviewDecision(Base, TimestampMixin):
    """Immutable trail of every review decision state change."""

    __tablename__ = "cert_item_review_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    decision_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    review_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_item_reviews.id"), nullable=False, index=True
    )
    reviewer_id: Mapped[str] = mapped_column(String(100), nullable=False)
    reviewer_role: Mapped[str] = mapped_column(String(50), nullable=False)
    decision: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    before_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    after_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    item_version: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("idx_ird_review", "review_id"),
        Index("idx_ird_decision", "decision"),
    )


class ItemPoolMembership(Base, TimestampMixin):
    """Tracks an item's membership in pilot or exam-eligible pools.

    An item may have zero or one active membership per pool type.
    Historical records are preserved.
    """

    __tablename__ = "cert_item_pool_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    membership_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    pool_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # pilot, exam_eligible
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="active", index=True
    )
    entry_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    exit_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    exit_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # Pilot-specific fields
    exposure_count: Mapped[int] = mapped_column(Integer, default=0)
    response_count: Mapped[int] = mapped_column(Integer, default=0)
    difficulty_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    discrimination_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    incident_count: Mapped[int] = mapped_column(Integer, default=0)
    flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    next_review_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Controlled exception tracking
    controlled_exception: Mapped[bool] = mapped_column(Boolean, default=False)
    exception_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exception_granted_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    exception_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Entered by
    entered_by: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("item_id", "pool_type", "status",
                         name="uq_item_pool_active"),
        Index("idx_ipm_pool_type_status", "pool_type", "status"),
        Index("idx_ipm_item_pool", "item_id", "pool_type"),
    )


class ItemExposureEvent(Base, TimestampMixin):
    """An individual exposure event — recorded when an item is served to a learner.

    Idempotent: duplicate events within the same session are not double-counted.
    """

    __tablename__ = "cert_item_exposure_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    exam_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    domain_pack_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    locale: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    cohort_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    exposure_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "item_id", "session_id",
            name="uq_exposure_event_item_session"
        ),
        Index("idx_iee_session", "session_id"),
        Index("idx_iee_timestamp", "exposure_timestamp"),
    )


class ItemExposureCounter(Base, TimestampMixin):
    """Aggregated exposure counters per item.

    Updated atomically from exposure events.
    """

    __tablename__ = "cert_item_exposure_counters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), unique=True, nullable=False, index=True
    )
    total_exposures: Mapped[int] = mapped_column(Integer, default=0)
    rolling_window_exposures: Mapped[int] = mapped_column(Integer, default=0)
    last_exposure_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    exposure_threshold: Mapped[int] = mapped_column(Integer, default=50)
    cooldown_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    overexposed: Mapped[bool] = mapped_column(Boolean, default=False)


class ItemRotationPolicy(Base, TimestampMixin):
    """Rotation policy configuration per item or domain pack."""

    __tablename__ = "cert_item_rotation_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    policy_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    domain_pack_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    item_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=True, index=True
    )
    max_total_exposures: Mapped[int] = mapped_column(Integer, default=100)
    rolling_window_days: Mapped[int] = mapped_column(Integer, default=30)
    min_cool_down_days: Mapped[int] = mapped_column(Integer, default=7)
    min_pool_size: Mapped[int] = mapped_column(Integer, default=5)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("idx_irp_domain_pack", "domain_pack_id"),
    )


class ItemGovernanceIncident(Base, TimestampMixin):
    """Governance incidents — flags requiring operator or admin attention."""

    __tablename__ = "cert_item_governance_incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    incident_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    incident_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(String(20), default="info")
    status: Mapped[str] = mapped_column(
        String(20), default="open", index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reported_by: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_igi_item", "item_id"),
        Index("idx_igi_type", "incident_type", "status"),
    )


class ItemSupersessionLink(Base, TimestampMixin):
    """Tracks supersession relationships between item versions.

    When an item is retired and replaced, the link preserves history.
    """

    __tablename__ = "cert_item_supersession_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    supersession_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    predecessor_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    successor_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supersession_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("predecessor_item_id", "successor_item_id",
                         name="uq_supersession_link"),
        Index("idx_isl_predecessor", "predecessor_item_id"),
        Index("idx_isl_successor", "successor_item_id"),
    )


class ItemExceptionApproval(Base, TimestampMixin):
    """Controlled exceptions — documented overrides for exam-eligible pool entry
    without full psychometric gate or pilot completion.
    """

    __tablename__ = "cert_item_exception_approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    exception_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    exception_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    granted_by: Mapped[str] = mapped_column(String(100), nullable=False)
    granted_by_role: Mapped[str] = mapped_column(String(50), nullable=False)
    second_reviewer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("idx_iea_item", "item_id"),
        Index("idx_iea_active", "is_active", "expires_at"),
    )
