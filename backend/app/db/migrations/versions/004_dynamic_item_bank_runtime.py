"""Add dynamic item bank runtime tables.

Revision ID: 004
Revises: 003
Create Date: 2026-06-07

This migration creates the operational runtime tables for the Dynamic Item Bank:
- cert_item_source_bindings — traceability snapshots
- cert_item_reviews — review records
- cert_item_review_decisions — immutable review decision trail
- cert_item_pool_memberships — pilot and exam-eligible pool tracking
- cert_item_exposure_events — idempotent exposure event log
- cert_item_exposure_counters — aggregated exposure counters
- cert_item_rotation_policies — rotation policy config
- cert_item_governance_incidents — governance flags
- cert_item_supersession_links — replacement/supersession tracking
- cert_item_exception_approvals — controlled exception approvals

No destructive changes to existing certification or BA/QA tables.
"""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # Item Source Bindings — traceability snapshots
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_source_bindings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("binding_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("source_registry_id", sa.String(100), nullable=False),
        sa.Column("source_version_id", sa.String(50), nullable=False),
        sa.Column("source_hash", sa.String(128), nullable=True),
        sa.Column("source_title", sa.String(500), nullable=False),
        sa.Column("source_uri", sa.String(1000), nullable=True),
        sa.Column("source_section_reference", sa.String(500), nullable=True),
        sa.Column("retrieved_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("domain_pack_id", sa.String(100), nullable=False),
        sa.Column("source_status_at_binding", sa.String(20),
                  nullable=False, server_default="active"),
        sa.Column("binding_actor", sa.String(100), nullable=False),
        sa.Column("binding_timestamp", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_isb_item", "cert_item_source_bindings", ["item_id"])
    op.create_index("idx_isb_source", "cert_item_source_bindings",
                    ["source_registry_id", "source_version_id"])

    # ------------------------------------------------------------------ #
    # Item Reviews
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("review_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("item_version", sa.Integer, nullable=False),
        sa.Column("review_stage", sa.String(30), nullable=False, index=True),
        sa.Column("reviewer_id", sa.String(100), nullable=False),
        sa.Column("reviewer_role", sa.String(50), nullable=False),
        sa.Column("decision", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("reviewer_comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_irev_item", "cert_item_reviews", ["item_id"])
    op.create_index("idx_irev_stage", "cert_item_reviews", ["review_stage"])
    op.create_index("idx_irev_reviewer", "cert_item_reviews", ["reviewer_id"])

    # ------------------------------------------------------------------ #
    # Item Review Decisions — immutable trail
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_review_decisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("decision_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("review_id", sa.String(36),
                  sa.ForeignKey("cert_item_reviews.id"), nullable=False, index=True),
        sa.Column("reviewer_id", sa.String(100), nullable=False),
        sa.Column("reviewer_role", sa.String(50), nullable=False),
        sa.Column("decision", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("before_status", sa.String(30), nullable=True),
        sa.Column("after_status", sa.String(30), nullable=True),
        sa.Column("item_version", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_ird_review", "cert_item_review_decisions", ["review_id"])
    op.create_index("idx_ird_decision", "cert_item_review_decisions", ["decision"])

    # ------------------------------------------------------------------ #
    # Item Pool Memberships — pilot and exam-eligible
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_pool_memberships",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("membership_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("pool_type", sa.String(20), nullable=False, index=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="active", index=True),
        sa.Column("entry_date", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("exit_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exit_reason", sa.String(200), nullable=True),
        sa.Column("exposure_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("response_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("difficulty_estimate", sa.Float, nullable=True),
        sa.Column("discrimination_estimate", sa.Float, nullable=True),
        sa.Column("incident_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("flags", sa.JSON, nullable=True),
        sa.Column("next_review_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("controlled_exception", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("exception_reason", sa.Text, nullable=True),
        sa.Column("exception_granted_by", sa.String(100), nullable=True),
        sa.Column("exception_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entered_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("item_id", "pool_type", "status",
                            name="uq_item_pool_active"),
    )
    op.create_index("idx_ipm_pool_type_status",
                    "cert_item_pool_memberships", ["pool_type", "status"])
    op.create_index("idx_ipm_item_pool",
                    "cert_item_pool_memberships", ["item_id", "pool_type"])

    # ------------------------------------------------------------------ #
    # Item Exposure Events — idempotent per session
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_exposure_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("session_id", sa.String(100), nullable=False, index=True),
        sa.Column("exam_type", sa.String(50), nullable=True),
        sa.Column("domain_pack_id", sa.String(100), nullable=True),
        sa.Column("locale", sa.String(10), nullable=True),
        sa.Column("cohort_id", sa.String(100), nullable=True),
        sa.Column("exposure_timestamp", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("item_id", "session_id",
                            name="uq_exposure_event_item_session"),
    )
    op.create_index("idx_iee_session", "cert_item_exposure_events", ["session_id"])
    op.create_index("idx_iee_timestamp", "cert_item_exposure_events", ["exposure_timestamp"])

    # ------------------------------------------------------------------ #
    # Item Exposure Counters — aggregated
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_exposure_counters",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), unique=True, nullable=False, index=True),
        sa.Column("total_exposures", sa.Integer, nullable=False, server_default="0"),
        sa.Column("rolling_window_exposures", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_exposure_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exposure_threshold", sa.Integer, nullable=False, server_default="50"),
        sa.Column("cooldown_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("overexposed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ------------------------------------------------------------------ #
    # Item Rotation Policies
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_rotation_policies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("policy_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("domain_pack_id", sa.String(100), nullable=True, index=True),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=True, index=True),
        sa.Column("max_total_exposures", sa.Integer, nullable=False, server_default="100"),
        sa.Column("rolling_window_days", sa.Integer, nullable=False, server_default="30"),
        sa.Column("min_cool_down_days", sa.Integer, nullable=False, server_default="7"),
        sa.Column("min_pool_size", sa.Integer, nullable=False, server_default="5"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_irp_domain_pack",
                    "cert_item_rotation_policies", ["domain_pack_id"])

    # ------------------------------------------------------------------ #
    # Item Governance Incidents
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_governance_incidents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("incident_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("incident_type", sa.String(50), nullable=False, index=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open", index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reported_by", sa.String(100), nullable=False),
        sa.Column("assigned_to", sa.String(100), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_igi_item", "cert_item_governance_incidents", ["item_id"])
    op.create_index("idx_igi_type", "cert_item_governance_incidents",
                    ["incident_type", "status"])

    # ------------------------------------------------------------------ #
    # Item Supersession Links
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_supersession_links",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("supersession_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("predecessor_item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("successor_item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("supersession_date", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("predecessor_item_id", "successor_item_id",
                            name="uq_supersession_link"),
    )
    op.create_index("idx_isl_predecessor",
                    "cert_item_supersession_links", ["predecessor_item_id"])
    op.create_index("idx_isl_successor",
                    "cert_item_supersession_links", ["successor_item_id"])

    # ------------------------------------------------------------------ #
    # Item Exception Approvals
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_exception_approvals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("exception_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("exception_type", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("granted_by", sa.String(100), nullable=False),
        sa.Column("granted_by_role", sa.String(50), nullable=False),
        sa.Column("second_reviewer", sa.String(100), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_iea_item", "cert_item_exception_approvals", ["item_id"])
    op.create_index("idx_iea_active", "cert_item_exception_approvals",
                    ["is_active", "expires_at"])


def downgrade() -> None:
    """Rollback dynamic item bank runtime tables.

    Existing certification and BA/QA tables are NOT affected.
    """
    op.drop_table("cert_item_exception_approvals")
    op.drop_table("cert_item_supersession_links")
    op.drop_table("cert_item_governance_incidents")
    op.drop_table("cert_item_rotation_policies")
    op.drop_table("cert_item_exposure_counters")
    op.drop_table("cert_item_exposure_events")
    op.drop_table("cert_item_pool_memberships")
    op.drop_table("cert_item_review_decisions")
    op.drop_table("cert_item_reviews")
    op.drop_table("cert_item_source_bindings")
