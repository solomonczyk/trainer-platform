"""Validation orchestration service — runs all validators and aggregates results."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.generation_models import (
    GeneratedCandidate,
    CandidateValidationRun,
    CandidateValidationResult,
)
from app.certification_core.validators.generation_validators import (
    VALIDATOR_VERSIONS,
    VALIDATION_POLICY_VERSION,
    ValidatorResult,
    validate_schema,
    validate_required_fields,
    validate_source_citations,
    validate_competency_alignment,
    validate_difficulty,
    validate_item_family,
    validate_answer_consistency,
    validate_rubric,
    validate_ambiguity,
    validate_duplicate,
    validate_safety,
    validate_locale,
    validate_answer_key_leak,
    validate_provenance,
    validate_pool_mutation_guard,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ValidationOrchestrator:
    """Orchestrates all validators for a generated candidate."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_full_validation(
        self,
        candidate: GeneratedCandidate,
        request_params: dict[str, Any],
        existing_candidates: list[dict[str, Any]] | None = None,
        validation_context: dict[str, Any] | None = None,
        source_registry: list[dict[str, Any]] | None = None,
    ) -> CandidateValidationRun:
        """Run all 15 validators against a candidate and return the aggregated run.

        Args:
            candidate: The candidate to validate.
            request_params: Generation request parameters.
            existing_candidates: Existing candidates for duplicate comparison.
            validation_context: Optional context for V10 self-exclusion.
                Keys: current_candidate_id, generation_request_id,
                      current_normalized_payload_hash, current_raw_response_hash.
            source_registry: Optional source records for V3 citation resolution.
        """
        validation_run = CandidateValidationRun(
            validation_run_id=f"vr-{uuid.uuid4().hex[:12]}",
            candidate_id=candidate.id,
            validation_policy_version=VALIDATION_POLICY_VERSION,
            started_at=datetime.now(timezone.utc),
            decision="pending",
        )
        self.db.add(validation_run)
        await self.db.flush()

        candidate_payload = candidate.normalized_payload or {}
        source_version_ids = request_params.get("trusted_source_version_ids", [])
        expected_competency_id = request_params.get("competency_id", "")
        expected_domain_id = request_params.get("domain_id", "")
        expected_difficulty = request_params.get("difficulty", "")
        expected_locale = request_params.get("locale", "")
        item_family_id = request_params.get("item_family_id", "")

        # Build provenance info
        provenance = {
            "provider": candidate.provider,
            "model": candidate.model,
            "prompt_template_version": request_params.get("prompt_template_version", ""),
            "generation_policy_version": request_params.get("generation_policy_version", ""),
            "schema_version": "1.0.0",
            "candidate_hash": candidate.normalized_payload_hash,
        }

        # Build V10 validation context for self-exclusion
        v10_context = dict(validation_context or {})
        if "current_candidate_id" not in v10_context:
            v10_context["current_candidate_id"] = candidate.candidate_id
        if "current_normalized_payload_hash" not in v10_context:
            v10_context["current_normalized_payload_hash"] = candidate.normalized_payload_hash or ""

        # Run all validators
        validators = [
            ("V1", validate_schema(candidate_payload)),
            ("V2", validate_required_fields(candidate_payload)),
            ("V3", validate_source_citations(candidate_payload, source_version_ids, source_registry)),
            ("V4", validate_competency_alignment(candidate_payload, expected_competency_id, expected_domain_id)),
            ("V5", validate_difficulty(candidate_payload, expected_difficulty)),
            ("V6", validate_item_family(candidate_payload, item_family_id)),
            ("V7", validate_answer_consistency(candidate_payload)),
            ("V8", validate_rubric(candidate_payload)),
            ("V9", validate_ambiguity(candidate_payload)),
            ("V10", validate_duplicate(candidate_payload, existing_candidates or [], validation_context=v10_context)),
            ("V11", validate_safety(candidate_payload)),
            ("V12", validate_locale(candidate_payload, expected_locale)),
            ("V13", validate_answer_key_leak(candidate_payload)),
            ("V14", validate_provenance(provenance)),
            ("V15", validate_pool_mutation_guard(candidate_payload, request_params.get("status", "draft"))),
        ]

        passed = 0
        failed = 0
        warning_count = 0
        not_run = 0
        critical = 0
        major = 0

        for code, result in validators:
            # Persist each result
            db_result = CandidateValidationResult(
                validation_run_id=validation_run.id,
                validator_code=result.validator_code,
                validator_version=result.validator_version,
                status=result.status,
                severity=result.severity,
                reason_code=result.reason_code,
                details=result.details,
                executed_at=result.executed_at,
            )
            self.db.add(db_result)

            # Count
            if result.status == "passed":
                passed += 1
            elif result.status == "failed":
                failed += 1
            elif result.status == "warning":
                warning_count += 1
            elif result.status == "not_run":
                not_run += 1

            if result.severity == "critical" and result.status == "failed":
                critical += 1
            elif result.severity == "major" and result.status == "failed":
                major += 1

        # Determine decision
        decision = self._aggregate_decision(critical, major, failed)

        validation_run.total_validators = len(validators)
        validation_run.passed_count = passed
        validation_run.failed_count = failed
        validation_run.warning_count = warning_count
        validation_run.not_run_count = not_run
        validation_run.critical_failures = critical
        validation_run.major_failures = major
        validation_run.decision = decision
        validation_run.completed_at = datetime.now(timezone.utc)

        await self.db.flush()

        logger.info(
            "Validation completed",
            candidate_id=candidate.candidate_id,
            decision=decision,
            critical=critical,
            major=major,
            warnings=warning_count,
        )

        return validation_run

    def _aggregate_decision(
        self, critical: int, major: int, failed: int
    ) -> str:
        """Aggregate validation results into a final decision.

        REJECTED — any critical failure
        VALIDATION_FAILED — major failures but no critical
        READY_FOR_HUMAN_REVIEW — no critical or major failures
        """
        if critical > 0:
            return "REJECTED"
        if major > 0:
            return "VALIDATION_FAILED"
        # Warnings alone still allow review handoff
        return "READY_FOR_HUMAN_REVIEW"

    def get_validator_versions(self) -> dict[str, str]:
        """Return all validator versions."""
        return dict(VALIDATOR_VERSIONS)
