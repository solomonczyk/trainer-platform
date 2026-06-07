"""Create controlled item generation pipeline tables.

Revision ID: 006
Revises: 005
Create Date: 2026-06-07

Creates tables:
- cert_generation_requests
- cert_generation_source_bindings
- cert_generation_provider_runs
- cert_generation_raw_responses
- cert_generated_candidates
- cert_candidate_validation_runs
- cert_candidate_validation_results
- cert_candidate_provenance
- cert_candidate_review_handoffs

No destructive changes to existing certification or BA/QA tables.
"""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. cert_generation_requests
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_generation_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("request_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("requested_by_user_id", sa.String(100), nullable=False),
        sa.Column("requested_by_role", sa.String(50), nullable=False),
        sa.Column("authorized_by", sa.String(100), nullable=True),
        sa.Column("authorized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("domain_id", sa.String(100), nullable=False, index=True),
        sa.Column("competency_id", sa.String(100), nullable=False, index=True),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False),
        sa.Column("item_family_id", sa.String(100), nullable=False, index=True),
        sa.Column("requested_candidate_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("trusted_source_version_ids", sa.JSON, nullable=True),
        sa.Column("generation_policy_version", sa.String(20), nullable=False),
        sa.Column("prompt_template_version", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft", index=True),
        sa.Column("correlation_id", sa.String(100), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_gr_status", "cert_generation_requests", ["status"])
    op.create_index("idx_gr_requested_by", "cert_generation_requests", ["requested_by_user_id"])
    op.create_index("idx_gr_domain_competency", "cert_generation_requests", ["domain_id", "competency_id"])

    # ------------------------------------------------------------------ #
    # 2. cert_generation_source_bindings
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_generation_source_bindings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("binding_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("generation_request_id", sa.String(36),
                  sa.ForeignKey("cert_generation_requests.id"), nullable=False, index=True),
        sa.Column("source_version_id", sa.String(100), nullable=False),
        sa.Column("source_checksum", sa.String(128), nullable=True),
        sa.Column("source_title", sa.String(500), nullable=False),
        sa.Column("source_locale", sa.String(10), nullable=False),
        sa.Column("source_status", sa.String(20), server_default="active"),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("retrieval_method", sa.String(50), server_default="registry"),
        sa.Column("context_fragment_hashes", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_gsb_request", "cert_generation_source_bindings", ["generation_request_id"])
    op.create_index("idx_gsb_source", "cert_generation_source_bindings", ["source_version_id"])

    # ------------------------------------------------------------------ #
    # 3. cert_generation_provider_runs
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_generation_provider_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("generation_request_id", sa.String(36),
                  sa.ForeignKey("cert_generation_requests.id"), nullable=False, index=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("provider_request_id", sa.String(200), nullable=True),
        sa.Column("prompt_tokens", sa.Integer, nullable=True),
        sa.Column("completion_tokens", sa.Integer, nullable=True),
        sa.Column("total_tokens", sa.Integer, nullable=True),
        sa.Column("cost_usd", sa.Float, nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("status", sa.String(20), server_default="completed"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("raw_response_hash", sa.String(128), nullable=True),
        sa.Column("prompt_package_system_prompt_hash", sa.String(128), nullable=True),
        sa.Column("prompt_package_context_hash", sa.String(128), nullable=True),
        sa.Column("prompt_package_hash", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_gpr_request", "cert_generation_provider_runs", ["generation_request_id"])

    # ------------------------------------------------------------------ #
    # 4. cert_generation_raw_responses
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_generation_raw_responses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_run_id", sa.String(36),
                  sa.ForeignKey("cert_generation_provider_runs.id"),
                  unique=True, nullable=False, index=True),
        sa.Column("raw_response", sa.JSON, nullable=False),
        sa.Column("reasoning_content", sa.Text, nullable=True),
        sa.Column("raw_response_hash", sa.String(128), nullable=False),
        sa.Column("response_size_bytes", sa.Integer, nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("secret_material_absent", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ------------------------------------------------------------------ #
    # 5. cert_generated_candidates
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_generated_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("candidate_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("generation_request_id", sa.String(36),
                  sa.ForeignKey("cert_generation_requests.id"), nullable=False, index=True),
        sa.Column("provider_run_id", sa.String(36),
                  sa.ForeignKey("cert_generation_provider_runs.id"), nullable=True, index=True),
        sa.Column("item_family_id", sa.String(100), nullable=False, index=True),
        sa.Column("domain_id", sa.String(100), nullable=False, index=True),
        sa.Column("competency_id", sa.String(100), nullable=False, index=True),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("stem", sa.Text, nullable=False),
        sa.Column("options", sa.JSON, nullable=True),
        sa.Column("answer_key", sa.JSON, nullable=True),
        sa.Column("rationale", sa.Text, server_default=""),
        sa.Column("rubric", sa.JSON, nullable=True),
        sa.Column("source_citations", sa.JSON, nullable=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("provider_request_id", sa.String(200), nullable=True),
        sa.Column("raw_response_hash", sa.String(128), nullable=True),
        sa.Column("normalized_payload_hash", sa.String(128), nullable=False),
        sa.Column("normalized_payload", sa.JSON, nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="generated", index=True),
        sa.Column("validation_status", sa.String(30), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_gc_request", "cert_generated_candidates", ["generation_request_id"])
    op.create_index("idx_gc_status", "cert_generated_candidates", ["status"])
    op.create_index("idx_gc_competency", "cert_generated_candidates", ["competency_id"])
    op.create_index("idx_gc_difficulty", "cert_generated_candidates", ["difficulty"])

    # ------------------------------------------------------------------ #
    # 6. cert_candidate_validation_runs
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_candidate_validation_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("validation_run_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("candidate_id", sa.String(36),
                  sa.ForeignKey("cert_generated_candidates.id"), nullable=False, index=True),
        sa.Column("validation_policy_version", sa.String(20), nullable=False),
        sa.Column("total_validators", sa.Integer, server_default="0"),
        sa.Column("passed_count", sa.Integer, server_default="0"),
        sa.Column("failed_count", sa.Integer, server_default="0"),
        sa.Column("warning_count", sa.Integer, server_default="0"),
        sa.Column("not_run_count", sa.Integer, server_default="0"),
        sa.Column("critical_failures", sa.Integer, server_default="0"),
        sa.Column("major_failures", sa.Integer, server_default="0"),
        sa.Column("decision", sa.String(30), server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_cvr_candidate", "cert_candidate_validation_runs", ["candidate_id"])

    # ------------------------------------------------------------------ #
    # 7. cert_candidate_validation_results
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_candidate_validation_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("validation_run_id", sa.String(36),
                  sa.ForeignKey("cert_candidate_validation_runs.id"), nullable=False, index=True),
        sa.Column("validator_code", sa.String(10), nullable=False),
        sa.Column("validator_version", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("reason_code", sa.String(100), nullable=True),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ------------------------------------------------------------------ #
    # 8. cert_candidate_provenance
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_candidate_provenance",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provenance_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("candidate_id", sa.String(36),
                  sa.ForeignKey("cert_generated_candidates.id"),
                  unique=True, nullable=False, index=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("source_version_ids", sa.JSON, nullable=True),
        sa.Column("source_checksums", sa.JSON, nullable=True),
        sa.Column("prompt_template_version", sa.String(20), nullable=False),
        sa.Column("prompt_hash", sa.String(128), nullable=True),
        sa.Column("generation_policy_version", sa.String(20), nullable=False),
        sa.Column("schema_version", sa.String(20), nullable=False),
        sa.Column("raw_response_hash", sa.String(128), nullable=True),
        sa.Column("candidate_hash", sa.String(128), nullable=False),
        sa.Column("validator_versions", sa.JSON, nullable=True),
        sa.Column("correlation_id", sa.String(100), nullable=True),
        sa.Column("request_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ------------------------------------------------------------------ #
    # 9. cert_candidate_review_handoffs
    # ------------------------------------------------------------------ #
    op.create_table(
        "cert_candidate_review_handoffs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("handoff_id", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("candidate_id", sa.String(36),
                  sa.ForeignKey("cert_generated_candidates.id"),
                  unique=True, nullable=False, index=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending_human_review"),
        sa.Column("validation_summary", sa.JSON, nullable=True),
        sa.Column("warnings", sa.JSON, nullable=True),
        sa.Column("reviewer_roles_allowed", sa.JSON, nullable=True),
        sa.Column("forbidden_actions", sa.JSON, nullable=True),
        sa.Column("human_review_completed", sa.Boolean, server_default="false"),
        sa.Column("human_accepted", sa.Boolean, server_default="false"),
        sa.Column("reviewed_by", sa.String(100), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pilot_allowed", sa.Boolean, server_default="false"),
        sa.Column("exam_eligible_allowed", sa.Boolean, server_default="false"),
        sa.Column("publication_allowed", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_crh_status", "cert_candidate_review_handoffs", ["status"])
    op.create_index("idx_crh_candidate", "cert_candidate_review_handoffs", ["candidate_id"])


def downgrade() -> None:
    """Drop all generation pipeline tables."""
    op.drop_table("cert_candidate_review_handoffs")
    op.drop_table("cert_candidate_provenance")
    op.drop_table("cert_candidate_validation_results")
    op.drop_table("cert_candidate_validation_runs")
    op.drop_table("cert_generated_candidates")
    op.drop_table("cert_generation_raw_responses")
    op.drop_table("cert_generation_provider_runs")
    op.drop_table("cert_generation_source_bindings")
    op.drop_table("cert_generation_requests")
