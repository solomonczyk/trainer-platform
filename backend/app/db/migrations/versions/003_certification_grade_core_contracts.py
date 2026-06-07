"""Add certification-grade core contracts tables.

Revision ID: 003
Revises: 002_ba_trainer_activities
Create Date: 2026-06-07

This migration creates the certification-grade core tables:
- cert_competency_frameworks / cert_competencies
- cert_exam_blueprints / cert_blueprint_sections
- cert_knowledge_sources
- cert_item_families / cert_items / cert_item_versions
- cert_rubrics / cert_rubric_criteria
- cert_domain_packs
- cert_audit_events

No destructive changes to existing BA/QA tables.
"""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002_ba_trainer_activities"
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # Competency Framework
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_competency_frameworks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("framework_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("domain_pack_id", sa.String(100), nullable=True, index=True),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en-US"),
        sa.Column("market", sa.String(50), nullable=False, server_default="global"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("framework_id", "version", name="uq_competency_framework_version"),
    )

    op.create_table(
        "cert_competencies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("competency_id", sa.String(100), index=True, nullable=False),
        sa.Column("framework_id", sa.String(36),
                  sa.ForeignKey("cert_competency_frameworks.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parent_id", sa.String(36),
                  sa.ForeignKey("cert_competencies.id"), nullable=True),
        sa.Column("cognitive_levels", sa.JSON, nullable=True),
        sa.Column("critical", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("weight", sa.Float, nullable=False, server_default="0"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("competency_id", "framework_id", name="uq_competency_per_framework"),
    )

    # ------------------------------------------------------------------ #
    # Exam Blueprint
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_exam_blueprints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("blueprint_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("domain_pack_id", sa.String(100), nullable=True, index=True),
        sa.Column("competency_framework_version", sa.String(100), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("exam_duration_minutes", sa.Integer, nullable=False, server_default="60"),
        sa.Column("total_items", sa.Integer, nullable=False, server_default="0"),
        sa.Column("pass_policy_id", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("blueprint_id", "version", name="uq_blueprint_version"),
    )

    op.create_table(
        "cert_blueprint_sections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("blueprint_id", sa.String(36),
                  sa.ForeignKey("cert_exam_blueprints.id"), nullable=False),
        sa.Column("section_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("competency_ids", sa.JSON, nullable=False),
        sa.Column("weight_percent", sa.Float, nullable=False),
        sa.Column("minimum_items", sa.Integer, nullable=False, server_default="0"),
        sa.Column("maximum_items", sa.Integer, nullable=False, server_default="0"),
        sa.Column("difficulty_distribution", sa.JSON, nullable=True),
        sa.Column("cognitive_distribution", sa.JSON, nullable=True),
        sa.Column("critical_section", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("blueprint_id", "section_id", name="uq_blueprint_section"),
    )

    # ------------------------------------------------------------------ #
    # Knowledge Sources
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_knowledge_sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="standard"),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("publisher", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(1000), nullable=True),
        sa.Column("jurisdiction", sa.String(100), nullable=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en-US"),
        sa.Column("market", sa.String(50), nullable=False, server_default="global"),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("content_hash", sa.String(128), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(100), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("superseded_by", sa.String(100), nullable=True),
        sa.Column("change_category", sa.String(30), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("source_id", "version", name="uq_knowledge_source_version"),
    )

    # ------------------------------------------------------------------ #
    # Item Families
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_item_families",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("family_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("domain_pack_id", sa.String(100), nullable=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("template_schema", sa.JSON, nullable=True),
        sa.Column("allowed_item_types", sa.JSON, nullable=True),
        sa.Column("competency_ids", sa.JSON, nullable=True),
        sa.Column("variant_policy", sa.JSON, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en-US"),
        sa.Column("market", sa.String(50), nullable=False, server_default="global"),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ------------------------------------------------------------------ #
    # Items
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("item_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("item_family_id", sa.String(36),
                  sa.ForeignKey("cert_item_families.id"), nullable=True, index=True),
        sa.Column("domain_pack_id", sa.String(100), nullable=True, index=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("prompt", sa.JSON, nullable=True),
        sa.Column("response_contract", sa.JSON, nullable=True),
        sa.Column("answer_key", sa.JSON, nullable=True),
        sa.Column("rubric_id", sa.String(100), nullable=True),
        sa.Column("competency_ids", sa.JSON, nullable=True),
        sa.Column("knowledge_source_refs", sa.JSON, nullable=True),
        sa.Column("difficulty_target", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("difficulty_measured", sa.Float, nullable=True),
        sa.Column("discrimination_measured", sa.Float, nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft", index=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en-US"),
        sa.Column("market", sa.String(50), nullable=False, server_default="global"),
        sa.Column("valid_from", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("reviewed_by", sa.String(100), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exposure_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("compromise_risk", sa.String(20), nullable=False, server_default="low"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "cert_item_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("item_id", sa.String(36),
                  sa.ForeignKey("cert_items.id"), nullable=False, index=True),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("snapshot", sa.JSON, nullable=False),
        sa.Column("change_reason", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("item_id", "version", name="uq_item_version"),
    )

    # ------------------------------------------------------------------ #
    # Rubrics
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_rubrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rubric_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("domain_pack_id", sa.String(100), nullable=True, index=True),
        sa.Column("competency_ids", sa.JSON, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("total_weight", sa.Float, nullable=False, server_default="100"),
        sa.Column("validation_dataset_ref", sa.String(100), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("rubric_id", "version", name="uq_rubric_version"),
    )

    op.create_table(
        "cert_rubric_criteria",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rubric_id", sa.String(36),
                  sa.ForeignKey("cert_rubrics.id"), nullable=False),
        sa.Column("criterion_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("levels", sa.JSON, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("rubric_id", "criterion_id", name="uq_rubric_criterion"),
    )

    # ------------------------------------------------------------------ #
    # Domain Packs
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_domain_packs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("domain_pack_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en-US"),
        sa.Column("market", sa.String(50), nullable=False, server_default="global"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("competency_framework_id", sa.String(100), nullable=True),
        sa.Column("blueprint_ids", sa.JSON, nullable=True),
        sa.Column("knowledge_source_ids", sa.JSON, nullable=True),
        sa.Column("item_bank_policy_id", sa.String(100), nullable=True),
        sa.Column("scoring_policy_id", sa.String(100), nullable=True),
        sa.Column("pass_policy_id", sa.String(100), nullable=True),
        sa.Column("rubric_ids", sa.JSON, nullable=True),
        sa.Column("supported_modes", sa.JSON, nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("domain_pack_id", "version", name="uq_domain_pack_version"),
    )

    # ------------------------------------------------------------------ #
    # Audit Events
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("audit_event_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False, index=True),
        sa.Column("entity_id", sa.String(100), nullable=False, index=True),
        sa.Column("entity_version", sa.String(20), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("actor_id", sa.String(100), nullable=False),
        sa.Column("actor_role", sa.String(50), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("before_hash", sa.String(128), nullable=True),
        sa.Column("after_hash", sa.String(128), nullable=True),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create additional indexes
    op.create_index("idx_comp_fw_domain_pack", "cert_competency_frameworks", ["domain_pack_id"])
    op.create_index("idx_comp_fw_status", "cert_competency_frameworks", ["status"])
    op.create_index("idx_comp_framework", "cert_competencies", ["framework_id"])
    op.create_index("idx_comp_parent", "cert_competencies", ["parent_id"])
    op.create_index("idx_bp_domain_pack", "cert_exam_blueprints", ["domain_pack_id"])
    op.create_index("idx_bp_status", "cert_exam_blueprints", ["status"])
    op.create_index("idx_bp_section_blueprint", "cert_blueprint_sections", ["blueprint_id"])
    op.create_index("idx_ks_type", "cert_knowledge_sources", ["source_type"])
    op.create_index("idx_ks_status", "cert_knowledge_sources", ["status"])
    op.create_index("idx_ks_locale_market", "cert_knowledge_sources", ["locale", "market"])
    op.create_index("idx_if_domain_pack", "cert_item_families", ["domain_pack_id"])
    op.create_index("idx_if_status", "cert_item_families", ["status"])
    op.create_index("idx_item_domain_pack", "cert_items", ["domain_pack_id"])
    op.create_index("idx_item_status", "cert_items", ["status"])
    op.create_index("idx_item_family", "cert_items", ["item_family_id"])
    op.create_index("idx_item_difficulty", "cert_items", ["difficulty_target"])
    op.create_index("idx_rubric_domain_pack", "cert_rubrics", ["domain_pack_id"])
    op.create_index("idx_rubric_status", "cert_rubrics", ["status"])
    op.create_index("idx_dp_status", "cert_domain_packs", ["status"])
    op.create_index("idx_dp_locale_market", "cert_domain_packs", ["locale", "market"])
    op.create_index("idx_audit_entity", "cert_audit_events", ["entity_type", "entity_id"])
    op.create_index("idx_audit_actor", "cert_audit_events", ["actor_id"])
    op.create_index("idx_audit_timestamp", "cert_audit_events", ["event_timestamp"])
    op.create_index("idx_audit_action", "cert_audit_events", ["action"])


def downgrade() -> None:
    """Rollback certification-grade core tables.

    WARNING: This will drop certification-grade data.
    Existing BA/QA tables are NOT affected.
    """
    # Drop in reverse dependency order
    op.drop_table("cert_audit_events")
    op.drop_table("cert_item_versions")
    op.drop_table("cert_items")
    op.drop_table("cert_item_families")
    op.drop_table("cert_rubric_criteria")
    op.drop_table("cert_rubrics")
    op.drop_table("cert_blueprint_sections")
    op.drop_table("cert_exam_blueprints")
    op.drop_table("cert_knowledge_sources")
    op.drop_table("cert_competencies")
    op.drop_table("cert_competency_frameworks")
    op.drop_table("cert_domain_packs")
