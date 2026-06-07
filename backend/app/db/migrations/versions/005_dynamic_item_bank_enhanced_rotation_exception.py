"""Add enhanced rotation policy and controlled exception approval columns.

Revision ID: 005
Revises: 004
Create Date: 2026-06-07

Adds columns to:
- cert_item_rotation_policies: allowed_locales, domain_balance_quotas,
  competency_balance_quotas, difficulty_balance_ratios, max_items_per_family,
  recent_use_window_days, exposure_threshold
- cert_item_exception_approvals: item_version_id, scope, requested_by,
  requester_role, first_approver, first_approval_timestamp,
  second_approval_timestamp, status, audit_correlation_id

No destructive changes to existing certification or BA/QA tables.
"""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # Enhanced rotation policy columns
    # ------------------------------------------------------------------ #
    op.add_column(
        "cert_item_rotation_policies",
        sa.Column("allowed_locales", sa.JSON, nullable=True),
    )
    op.add_column(
        "cert_item_rotation_policies",
        sa.Column("domain_balance_quotas", sa.JSON, nullable=True),
    )
    op.add_column(
        "cert_item_rotation_policies",
        sa.Column("competency_balance_quotas", sa.JSON, nullable=True),
    )
    op.add_column(
        "cert_item_rotation_policies",
        sa.Column("difficulty_balance_ratios", sa.JSON, nullable=True),
    )
    op.add_column(
        "cert_item_rotation_policies",
        sa.Column("max_items_per_family", sa.Integer,
                  nullable=False, server_default="3"),
    )
    op.add_column(
        "cert_item_rotation_policies",
        sa.Column("recent_use_window_days", sa.Integer,
                  nullable=False, server_default="90"),
    )
    op.add_column(
        "cert_item_rotation_policies",
        sa.Column("exposure_threshold", sa.Integer,
                  nullable=False, server_default="50"),
    )

    # ------------------------------------------------------------------ #
    # Enhanced exception approval columns
    # ------------------------------------------------------------------ #
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("item_version_id", sa.String(100), nullable=True, index=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("scope", sa.String(100), nullable=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("requested_by", sa.String(100), nullable=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("requester_role", sa.String(50), nullable=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("first_approver", sa.String(100), nullable=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("first_approval_timestamp", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("second_approval_timestamp", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("status", sa.String(20),
                  nullable=False, server_default="pending", index=True),
    )
    op.add_column(
        "cert_item_exception_approvals",
        sa.Column("audit_correlation_id", sa.String(100), nullable=True),
    )

    # Create index on exception status
    op.create_index(
        "idx_iea_status",
        "cert_item_exception_approvals",
        ["status"],
    )


def downgrade() -> None:
    """Rollback enhanced columns — drop all added columns."""
    # Exception approval columns
    op.drop_column("cert_item_exception_approvals", "audit_correlation_id")
    op.drop_column("cert_item_exception_approvals", "status")
    op.drop_column("cert_item_exception_approvals", "second_approval_timestamp")
    op.drop_column("cert_item_exception_approvals", "first_approval_timestamp")
    op.drop_column("cert_item_exception_approvals", "first_approver")
    op.drop_column("cert_item_exception_approvals", "requester_role")
    op.drop_column("cert_item_exception_approvals", "requested_by")
    op.drop_column("cert_item_exception_approvals", "scope")
    op.drop_column("cert_item_exception_approvals", "item_version_id")

    # Rotation policy columns
    op.drop_column("cert_item_rotation_policies", "exposure_threshold")
    op.drop_column("cert_item_rotation_policies", "recent_use_window_days")
    op.drop_column("cert_item_rotation_policies", "max_items_per_family")
    op.drop_column("cert_item_rotation_policies", "difficulty_balance_ratios")
    op.drop_column("cert_item_rotation_policies", "competency_balance_quotas")
    op.drop_column("cert_item_rotation_policies", "domain_balance_quotas")
    op.drop_column("cert_item_rotation_policies", "allowed_locales")
