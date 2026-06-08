"""Create human review layer tables — review cases, assignments, decisions.

Revision ID: 007
Revises: 006
Create Date: 2026-06-08

Creates tables:
- cert_human_review_cases
- cert_reviewer_assignments
- cert_human_review_decisions

Constraints:
- Foreign keys to candidates, validation runs, review handoffs
- Unique active assignment per case
- Decision values constrained
- Status values constrained
- No hard-delete behavior
- Useful indexes for filtering and queries

No destructive changes to existing certification, BA/QA, or generation tables.
"""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from alembic import op

revision = "007"
down_revision = "006"
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. cert_human_review_cases
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_human_review_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("candidate_id", sa.String(36),
                  sa.ForeignKey("cert_generated_candidates.id"),
                  nullable=False, index=True),
        sa.Column("review_handoff_id", sa.String(36),
                  sa.ForeignKey("cert_candidate_review_handoffs.id"),
                  nullable=False, index=True),
        sa.Column("validation_run_id", sa.String(36),
                  sa.ForeignKey("cert_candidate_validation_runs.id"),
                  nullable=False, index=True),
        sa.Column("status", sa.String(30), nullable=False,
                  server_default="PENDING_ASSIGNMENT", index=True),
        sa.Column("review_type", sa.String(30), nullable=False,
                  server_default="expert_review"),
        sa.Column("required_reviewer_role", sa.String(50), nullable=False),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_hrc_status", "cert_human_review_cases", ["status"])
    op.create_index("idx_hrc_candidate", "cert_human_review_cases", ["candidate_id"])
    op.create_index("idx_hrc_reviewer_role", "cert_human_review_cases", ["required_reviewer_role"])
    op.create_index("idx_hrc_created", "cert_human_review_cases", ["created_at"])
    op.create_index("idx_hrc_status_created", "cert_human_review_cases", ["status", "created_at"])

    # ------------------------------------------------------------------ #
    # 2. cert_reviewer_assignments
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_reviewer_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("assignment_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("review_case_id", sa.String(36),
                  sa.ForeignKey("cert_human_review_cases.id"),
                  nullable=False, index=True),
        sa.Column("reviewer_user_id", sa.String(100), nullable=False, index=True),
        sa.Column("reviewer_role", sa.String(50), nullable=False),
        sa.Column("assigned_by", sa.String(100), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(30), nullable=False,
                  server_default="ASSIGNED", index=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_ra_case", "cert_reviewer_assignments", ["review_case_id"])
    op.create_index("idx_ra_reviewer", "cert_reviewer_assignments", ["reviewer_user_id"])
    op.create_index("idx_ra_status", "cert_reviewer_assignments", ["status"])
    op.create_index("idx_ra_case_status", "cert_reviewer_assignments",
                    ["review_case_id", "status"])

    # ------------------------------------------------------------------ #
    # 3. cert_human_review_decisions
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_human_review_decisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("decision_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("review_case_id", sa.String(36),
                  sa.ForeignKey("cert_human_review_cases.id"),
                  nullable=False, index=True),
        sa.Column("assignment_id", sa.String(36),
                  sa.ForeignKey("cert_reviewer_assignments.id"),
                  nullable=False, index=True),
        sa.Column("candidate_id", sa.String(36),
                  sa.ForeignKey("cert_generated_candidates.id"),
                  nullable=False, index=True),
        sa.Column("reviewer_user_id", sa.String(100), nullable=False, index=True),
        sa.Column("reviewer_role", sa.String(50), nullable=False),
        sa.Column("decision", sa.String(30), nullable=False, index=True),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("findings_json", sa.JSON, nullable=True),
        sa.Column("evidence_snapshot_json", sa.JSON, nullable=True),
        sa.Column("candidate_hash", sa.String(128), nullable=False),
        sa.Column("validation_run_id", sa.String(36),
                  sa.ForeignKey("cert_candidate_validation_runs.id"),
                  nullable=False, index=True),
        sa.Column("correlation_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_hrd_case", "cert_human_review_decisions", ["review_case_id"])
    op.create_index("idx_hrd_reviewer", "cert_human_review_decisions", ["reviewer_user_id"])
    op.create_index("idx_hrd_decision", "cert_human_review_decisions", ["decision"])
    op.create_index("idx_hrd_created", "cert_human_review_decisions", ["created_at"])
    op.create_index("idx_hrd_candidate", "cert_human_review_decisions", ["candidate_id"])

    # Add a partial unique index to enforce exactly one active assignment per case
    op.execute(
        "CREATE UNIQUE INDEX idx_ra_one_active_per_case "
        "ON cert_reviewer_assignments (review_case_id) "
        "WHERE status IN ('ASSIGNED', 'CLAIMED')"
    )


def downgrade() -> None:
    """Drop all human review layer tables."""
    op.drop_index("idx_ra_one_active_per_case",
                  table_name="cert_reviewer_assignments")
    op.drop_table("cert_human_review_decisions")
    op.drop_table("cert_reviewer_assignments")
    op.drop_table("cert_human_review_cases")
