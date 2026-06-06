"""BA Trainer deterministic activity system — activities and deterministic_evaluations tables.

Revision ID: 002
Revises: 001
Create Date: 2026-06-06

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> sa.sql.expression.FunctionElement:
    """Return a server-default expression for current_timestamp (utc)."""
    return sa.func.now()


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    # =========================================================================
    # 1. Activities table
    # =========================================================================

    op.create_table(
        "activities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("activity_id", sa.String(100), nullable=False),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("module_id", sa.String(100), nullable=False),
        sa.Column("activity_type", sa.String(50), nullable=False),
        sa.Column("evaluation_mode", sa.String(50), server_default="deterministic", nullable=False),
        sa.Column("difficulty", sa.String(50), server_default="junior", nullable=False),
        sa.Column("title_key", sa.String(255), nullable=False),
        sa.Column("description_key", sa.String(255), nullable=True),
        sa.Column("payload", JSON(), nullable=False),
        sa.Column("explanation_key", sa.String(255), nullable=False),
        sa.Column("order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("version", sa.String(20), server_default="0.1.0", nullable=False),
        sa.Column("migration_metadata", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_activities_trainer_product_id"
        ),
        sa.UniqueConstraint("activity_id", name="uq_activities_activity_id"),
    )
    op.create_index("ix_activities_activity_id", "activities", ["activity_id"])

    # =========================================================================
    # 2. Deterministic Evaluations table
    # =========================================================================

    op.create_table(
        "deterministic_evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("attempt_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("feedback", JSON(), nullable=True),
        sa.Column("evaluation_mode", sa.String(50), server_default="deterministic", nullable=False),
        sa.Column("validation_status", sa.String(50), server_default="validated", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["attempt_id"], ["attempts.id"], name="fk_deterministic_evaluations_attempt_id"
        ),
        sa.UniqueConstraint("attempt_id", name="uq_deterministic_evaluations_attempt_id"),
    )

    # =========================================================================
    # 3. Add columns to attempts
    # =========================================================================

    op.add_column("attempts", sa.Column("activity_id", sa.String(36), nullable=True))
    op.add_column("attempts", sa.Column("activity_type", sa.String(50), nullable=True))
    op.add_column("attempts", sa.Column("evaluation_mode", sa.String(50), nullable=True))
    op.add_column("attempts", sa.Column("submitted_answer", JSON(), nullable=True))
    op.add_column("attempts", sa.Column("idempotency_key", sa.String(100), nullable=True))
    op.create_index("ix_attempts_idempotency_key", "attempts", ["idempotency_key"])
    op.create_foreign_key(
        "fk_attempts_activity_id", "attempts", "activities",
        ["activity_id"], ["id"]
    )

    # Make scenario_id nullable for activity-based attempts (BA trainer)
    op.execute("ALTER TABLE attempts ALTER COLUMN scenario_id DROP NOT NULL;")


# ---------------------------------------------------------------------------
# Downgrade  (reverse order to respect FK constraints)
# ---------------------------------------------------------------------------

def downgrade() -> None:
    # =========================================================================
    # 3. Revert attempts columns
    # =========================================================================

    op.drop_constraint("fk_attempts_activity_id", "attempts", type_="foreignkey")
    op.drop_index("ix_attempts_idempotency_key", table_name="attempts")
    op.drop_column("attempts", "idempotency_key")
    op.drop_column("attempts", "submitted_answer")
    op.drop_column("attempts", "evaluation_mode")
    op.drop_column("attempts", "activity_type")
    op.drop_column("attempts", "activity_id")

    # =========================================================================
    # 2. Drop deterministic_evaluations
    # =========================================================================

    op.drop_table("deterministic_evaluations")

    # =========================================================================
    # 1. Drop activities
    # =========================================================================

    op.drop_index("ix_activities_activity_id", table_name="activities")
    op.drop_table("activities")
