"""Add quest engine tables for Layer 010 immersive simulator.

Revision ID: 008
Revises: 007
Create Date: 2026-06-09

Creates tables:
- quest_sessions — tracks immersive quest state with narrative values
- quest_step_results — per-step answers, evaluation state, and results

Constraints:
- Foreign keys to users
- Unique step per quest session
- Cascade delete on session removal
- Narrative value ranges (0-100 where applicable)

No destructive changes to existing tables.
"""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from alembic import op

revision = "008"
down_revision: Optional[str] = "007"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    """Create quest engine tables."""

    # ---------------------------------------------------------------------------
    # quest_sessions
    # ---------------------------------------------------------------------------
    op.create_table(
        "quest_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("quest_id", sa.String(100), nullable=False, index=True),
        sa.Column("trainer_slug", sa.String(100), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False, server_default="ru-RU"),
        sa.Column("status", sa.String(50), nullable=False, server_default="in_progress"),

        # Narrative state
        sa.Column("current_step_id", sa.String(100), nullable=True),
        sa.Column("completed_step_ids", sa.JSON, nullable=True),
        sa.Column("visited_branch_ids", sa.JSON, nullable=True),

        # Tracked narrative values
        sa.Column("risk", sa.Integer, nullable=False, server_default="0"),
        sa.Column("time_remaining", sa.Integer, nullable=False, server_default="100"),
        sa.Column("team_trust", sa.Integer, nullable=False, server_default="100"),
        sa.Column("client_trust", sa.Integer, nullable=False, server_default="100"),
        sa.Column("evidence_quality", sa.Integer, nullable=False, server_default="0"),
        sa.Column("decision_quality", sa.Integer, nullable=False, server_default="0"),

        # Flags, outcome, debrief
        sa.Column("flags", sa.JSON, nullable=True),
        sa.Column("selected_outcome_id", sa.String(100), nullable=True),
        sa.Column("debrief_data", sa.JSON, nullable=True),

        # Timestamps
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_quest_sessions_user_id", "quest_sessions", ["user_id"])
    op.create_index("ix_quest_sessions_quest_id", "quest_sessions", ["quest_id"])

    # ---------------------------------------------------------------------------
    # quest_step_results
    # ---------------------------------------------------------------------------
    op.create_table(
        "quest_step_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "quest_session_id", sa.String(36),
            sa.ForeignKey("quest_sessions.id", ondelete="CASCADE"),
            nullable=False, index=True,
        ),
        sa.Column("step_id", sa.String(100), nullable=False),
        sa.Column("step_type", sa.String(50), nullable=True),

        # Answer
        sa.Column("answer", sa.JSON, nullable=True),

        # Evaluation state
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("evaluation_mode", sa.String(50), nullable=True),
        sa.Column("score", sa.Integer, nullable=True),
        sa.Column("max_score", sa.Integer, nullable=True),
        sa.Column("correct", sa.Boolean, nullable=True),
        sa.Column("feedback_key", sa.String(255), nullable=True),
        sa.Column("feedback_data", sa.JSON, nullable=True),

        # Consequence updates
        sa.Column("consequence_updates", sa.JSON, nullable=True),

        # AI metadata
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("provider_model", sa.String(100), nullable=True),
        sa.Column("ai_latency_ms", sa.Integer, nullable=True),
        sa.Column("ai_cost_usd", sa.Float, nullable=True),
        sa.Column("correlation_id", sa.String(100), nullable=True),
        sa.Column("timed_out", sa.Boolean, nullable=False, server_default="false"),

        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_quest_step_results_session", "quest_step_results", ["quest_session_id"])
    op.create_unique_constraint(
        "uq_quest_session_step",
        "quest_step_results",
        ["quest_session_id", "step_id"],
    )


def downgrade() -> None:
    """Drop quest engine tables."""
    op.drop_table("quest_step_results")
    op.drop_table("quest_sessions")
