"""Initial MVP schema — create all platform tables.

Revision ID: 001
Revises: None
Create Date: 2026-06-04

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
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
    # 1. Auth / Users
    # =========================================================================

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), server_default="registered_user", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("preferred_locale", sa.String(10), server_default="ru-RU", nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("metadata_json", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_profiles_user_id"),
        sa.UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
    )

    # =========================================================================
    # 2. Content / Domains
    # =========================================================================

    op.create_table(
        "domains",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("slug", name="uq_domains_slug"),
    )
    op.create_index("ix_domains_slug", "domains", ["slug"])

    op.create_table(
        "trainer_products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trainer_product_id", sa.String(100), nullable=False),
        sa.Column("domain_id", sa.String(36), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("product_type", sa.String(50), server_default="interview_simulator", nullable=False),
        sa.Column("target_audience", JSON(), nullable=True),
        sa.Column("default_locale", sa.String(10), server_default="ru-RU", nullable=False),
        sa.Column("supported_locales", JSON(), nullable=True),
        sa.Column("status", sa.String(50), server_default="published_seed", nullable=False),
        sa.Column("owner", sa.String(50), server_default="platform", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["domain_id"], ["domains.id"], name="fk_trainer_products_domain_id"),
        sa.UniqueConstraint("trainer_product_id", name="uq_trainer_products_product_id"),
        sa.UniqueConstraint("slug", name="uq_trainer_products_slug"),
    )
    op.create_index("ix_trainer_products_trainer_product_id", "trainer_products", ["trainer_product_id"])
    op.create_index("ix_trainer_products_slug", "trainer_products", ["slug"])

    op.create_table(
        "trainer_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("release_status", sa.String(50), server_default="mvp_seed", nullable=False),
        sa.Column("skill_map_id", sa.String(100), nullable=True),
        sa.Column("rubric_pack_id", sa.String(100), nullable=True),
        sa.Column("scenario_ids", JSON(), nullable=True),
        sa.Column("locale_pack_ids", JSON(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requires_expert_review", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_trainer_versions_trainer_product_id"
        ),
        sa.UniqueConstraint("trainer_product_id", "version", name="uq_trainer_version"),
    )

    op.create_table(
        "trainer_localizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False),
        sa.Column("strings", JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_trainer_localizations_trainer_product_id"
        ),
        sa.UniqueConstraint("trainer_product_id", "locale", name="uq_trainer_locale"),
    )

    # =========================================================================
    # 3. Tracks / Modules
    # =========================================================================

    op.create_table(
        "tracks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_tracks_trainer_product_id"
        ),
    )

    op.create_table(
        "modules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("track_id", sa.String(36), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"], name="fk_modules_track_id"),
    )

    # =========================================================================
    # 4. Scenarios
    # =========================================================================

    op.create_table(
        "scenarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scenario_id", sa.String(100), nullable=False),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("title_key", sa.String(255), nullable=False),
        sa.Column("goal_key", sa.String(255), nullable=False),
        sa.Column("trainer_version", sa.String(20), server_default="1.0.0", nullable=False),
        sa.Column("track", sa.String(100), nullable=True),
        sa.Column("module", sa.String(100), nullable=True),
        sa.Column("difficulty", sa.String(50), server_default="junior_basic", nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), server_default=sa.text("8"), nullable=False),
        sa.Column("target_skills", JSON(), nullable=True),
        sa.Column("user_role", sa.String(50), server_default="candidate", nullable=False),
        sa.Column("ai_role", sa.String(50), server_default="interviewer", nullable=False),
        sa.Column("rubric_id", sa.String(100), nullable=True),
        sa.Column("steps", JSON(), nullable=True),
        sa.Column("common_errors", JSON(), nullable=True),
        sa.Column("critical_errors", JSON(), nullable=True),
        sa.Column("hints", JSON(), nullable=True),
        sa.Column("status", sa.String(50), server_default="published_seed", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_scenarios_trainer_product_id"
        ),
        sa.UniqueConstraint("scenario_id", name="uq_scenarios_scenario_id"),
    )
    op.create_index("ix_scenarios_scenario_id", "scenarios", ["scenario_id"])

    op.create_table(
        "scenario_steps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scenario_id", sa.String(36), nullable=False),
        sa.Column("step_id", sa.String(100), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("prompt_key", sa.String(255), nullable=False),
        sa.Column("expected_actions", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["scenario_id"], ["scenarios.id"], name="fk_scenario_steps_scenario_id"
        ),
        sa.UniqueConstraint("scenario_id", "step_id", name="uq_scenario_step"),
    )

    # =========================================================================
    # 5. Skills / Rubrics
    # =========================================================================

    op.create_table(
        "skill_maps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("skill_map_id", sa.String(100), nullable=False),
        sa.Column("skills", JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("skill_map_id", name="uq_skill_maps_skill_map_id"),
    )

    op.create_table(
        "skills",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("skill_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("levels", JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("skill_id", name="uq_skills_skill_id"),
    )

    op.create_table(
        "rubrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rubric_id", sa.String(100), nullable=False),
        sa.Column("scenario_id", sa.String(36), nullable=True),
        sa.Column("pass_score", sa.Integer(), server_default=sa.text("70"), nullable=False),
        sa.Column("critical_fail_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], name="fk_rubrics_scenario_id"),
        sa.UniqueConstraint("rubric_id", name="uq_rubrics_rubric_id"),
    )

    op.create_table(
        "rubric_criteria",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rubric_id", sa.String(36), nullable=False),
        sa.Column("criterion_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("evidence_required", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["rubric_id"], ["rubrics.id"], name="fk_rubric_criteria_rubric_id"),
        sa.UniqueConstraint("rubric_id", "criterion_id", name="uq_rubric_criterion"),
    )

    op.create_table(
        "critical_errors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("error_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("scenario_ids", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_critical_errors_trainer_product_id"
        ),
        sa.UniqueConstraint("error_id", name="uq_critical_errors_error_id"),
    )

    # =========================================================================
    # 6. Enrollment / Sessions / Attempts
    # =========================================================================

    op.create_table(
        "user_trainer_enrollments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_enrollments_user_id"),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_enrollments_trainer_product_id"
        ),
        sa.UniqueConstraint("user_id", "trainer_product_id", name="uq_user_enrollment"),
    )

    op.create_table(
        "simulation_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("scenario_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(50), server_default="active", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_sessions_user_id"),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], name="fk_sessions_scenario_id"),
    )

    op.create_table(
        "simulation_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("message_type", sa.String(50), server_default="answer", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"], ["simulation_sessions.id"], name="fk_messages_session_id"
        ),
    )

    op.create_table(
        "attempts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("scenario_id", sa.String(36), nullable=False),
        sa.Column("session_id", sa.String(36), nullable=True),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(50), server_default="in_progress", nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_retry", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("retry_of_attempt_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_attempts_user_id"),
        sa.ForeignKeyConstraint(["scenario_id"], ["scenarios.id"], name="fk_attempts_scenario_id"),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_attempts_trainer_product_id"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["simulation_sessions.id"], name="fk_attempts_session_id"
        ),
    )

    # =========================================================================
    # 7. Evaluations
    # =========================================================================

    op.create_table(
        "evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("attempt_id", sa.String(36), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("strengths", JSON(), nullable=True),
        sa.Column("weak_points", JSON(), nullable=True),
        sa.Column("critical_errors", JSON(), nullable=True),
        sa.Column("next_recommendation", JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("ai_model_used", sa.String(100), nullable=True),
        sa.Column("ai_cost_usd", sa.Float(), nullable=True),
        sa.Column("ai_latency_ms", sa.Integer(), nullable=True),
        sa.Column("raw_ai_output", JSON(), nullable=True),
        sa.Column("validation_status", sa.String(50), server_default="validated", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["attempt_id"], ["attempts.id"], name="fk_evaluations_attempt_id"),
        sa.UniqueConstraint("attempt_id", name="uq_evaluations_attempt_id"),
    )

    op.create_table(
        "evaluation_criteria_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("evaluation_id", sa.String(36), nullable=False),
        sa.Column("criterion_id", sa.String(100), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("improvement", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["evaluation_id"], ["evaluations.id"], name="fk_criteria_results_evaluation_id"
        ),
    )

    # =========================================================================
    # 8. Progress / Skill Scores
    # =========================================================================

    op.create_table(
        "trainer_progress",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("average_score", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("completed_scenarios", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("total_attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("readiness_status", sa.String(50), server_default="started", nullable=False),
        sa.Column("last_scenario_id", sa.String(36), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_progress_user_id"),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_progress_trainer_product_id"
        ),
        sa.UniqueConstraint("user_id", "trainer_product_id", name="uq_user_progress"),
    )

    op.create_table(
        "skill_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("trainer_product_id", sa.String(36), nullable=False),
        sa.Column("skill_id", sa.String(100), nullable=False),
        sa.Column("score", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("attempts_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("level", sa.String(50), server_default="not_observed", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_skill_scores_user_id"),
        sa.ForeignKeyConstraint(
            ["trainer_product_id"], ["trainer_products.id"], name="fk_skill_scores_trainer_product_id"
        ),
        sa.UniqueConstraint("user_id", "trainer_product_id", "skill_id", name="uq_user_skill_score"),
    )

    # =========================================================================
    # 9. Analytics / AI Requests
    # =========================================================================

    op.create_table(
        "analytics_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("trainer_slug", sa.String(100), nullable=True),
        sa.Column("scenario_id", sa.String(100), nullable=True),
        sa.Column("properties", JSON(), nullable=True),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_analytics_user_id"),
    )
    op.create_index("idx_analytics_event_type", "analytics_events", ["event_type"])
    op.create_index("idx_analytics_timestamp", "analytics_events", ["event_timestamp"])

    op.create_table(
        "ai_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("request_type", sa.String(100), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("prompt_template", sa.String(255), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), server_default="completed", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempt_id", sa.String(36), nullable=True),
        sa.Column("scenario_id", sa.String(100), nullable=True),
        sa.Column("request_metadata", JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # =========================================================================
    # 10. Feature Flags
    # =========================================================================

    op.create_table(
        "feature_flags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("flag_key", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner", sa.String(100), nullable=True),
        sa.Column("rollout_percentage", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_utcnow(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("flag_key", name="uq_feature_flags_flag_key"),
    )
    op.create_index("ix_feature_flags_flag_key", "feature_flags", ["flag_key"])


# ---------------------------------------------------------------------------
# Downgrade  (reverse order to respect FK constraints)
# ---------------------------------------------------------------------------

def downgrade() -> None:
    # Drop in reverse dependency order.

    # 10. Feature Flags
    op.drop_index("ix_feature_flags_flag_key", table_name="feature_flags")
    op.drop_table("feature_flags")

    # 9. Analytics / AI Requests
    op.drop_index("idx_analytics_timestamp", table_name="analytics_events")
    op.drop_index("idx_analytics_event_type", table_name="analytics_events")
    op.drop_table("analytics_events")
    op.drop_table("ai_requests")

    # 8. Progress / Skill Scores
    op.drop_table("skill_scores")
    op.drop_table("trainer_progress")

    # 7. Evaluations
    op.drop_table("evaluation_criteria_results")
    op.drop_table("evaluations")

    # 6. Enrollment / Sessions / Attempts
    op.drop_table("attempts")
    op.drop_table("simulation_messages")
    op.drop_table("simulation_sessions")
    op.drop_table("user_trainer_enrollments")

    # 5. Skills / Rubrics
    op.drop_table("critical_errors")
    op.drop_table("rubric_criteria")
    op.drop_table("rubrics")
    op.drop_table("skills")
    op.drop_table("skill_maps")

    # 4. Scenarios
    op.drop_index("ix_scenarios_scenario_id", table_name="scenarios")
    op.drop_table("scenario_steps")
    op.drop_table("scenarios")

    # 3. Tracks / Modules
    op.drop_table("modules")
    op.drop_table("tracks")

    # 2. Content / Domains
    op.drop_table("trainer_localizations")
    op.drop_table("trainer_versions")
    op.drop_index("ix_trainer_products_slug", table_name="trainer_products")
    op.drop_index("ix_trainer_products_trainer_product_id", table_name="trainer_products")
    op.drop_table("trainer_products")
    op.drop_index("ix_domains_slug", table_name="domains")
    op.drop_table("domains")

    # 1. Auth / Users
    op.drop_table("user_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
