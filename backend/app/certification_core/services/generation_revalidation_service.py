"""Corrective revalidation service — deterministically revalidates an existing candidate.

This service is used for corrective revalidation only. It:
- Loads a persisted candidate without re-generating or calling a provider.
- Runs the full V1–V15 validation pipeline.
- Appends a new validation run (original is preserved).
- Optionally creates a review handoff if the new decision permits.
- Records audit events for every step.

IMPORTANT: This service NEVER calls a provider, NEVER generates a new candidate,
and NEVER mutates the original candidate payload.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.generation_models import (
    GeneratedCandidate,
    GenerationRequest,
    GenerationSourceBinding,
    CandidateValidationRun,
    CandidateValidationResult,
    CandidateProvenance,
    CandidateReviewHandoff,
)
from app.certification_core.services.generation_audit_service import GenerationAuditService
from app.certification_core.services.generation_validation_service import ValidationOrchestrator
from app.certification_core.validators.generation_validators import (
    VALIDATION_POLICY_VERSION,
    VALIDATOR_VERSIONS,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class CandidateRevalidationError(Exception):
    """Raised when revalidation cannot proceed."""


class CandidateRevalidationService:
    """Deterministic revalidation of an existing candidate without provider calls."""

    REVALIDATION_BUNDLE_VERSION = "1.0.0"

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = GenerationAuditService(db)

    async def revalidate_existing_candidate(
        self,
        candidate_id: str,
        reason: str,
        actor_id: str = "system",
        actor_role: str = "system",
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute a full deterministic revalidation of an existing candidate.

        Args:
            candidate_id: The unique candidate_id (e.g. "cand-c1a83dade217").
            reason: Reason for revalidation (e.g. "V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX").
            actor_id: Actor performing the revalidation.
            actor_role: Actor role.
            correlation_id: Optional correlation ID for audit trace.

        Returns:
            Dict with full revalidation results.

        Raises:
            CandidateRevalidationError: If candidate is missing or content changed.
        """
        # Load the candidate
        candidate = await self._load_candidate(candidate_id)
        if not candidate:
            raise CandidateRevalidationError(f"Candidate not found: {candidate_id}")

        # Load generation request
        gen_request = await self._load_generation_request(candidate.generation_request_id)
        if not gen_request:
            raise CandidateRevalidationError(
                f"Generation request not found for candidate: {candidate_id}"
            )

        effective_correlation_id = correlation_id or gen_request.correlation_id or str(uuid.uuid4())

        # Record content hash BEFORE revalidation to verify no change
        content_hash_before = self._compute_candidate_hash(candidate)

        # Record the start
        revalidation_run_id = f"rr-{uuid.uuid4().hex[:12]}"
        started_at = datetime.now(timezone.utc)

        await self.audit.record(
            action="candidate_corrective_revalidation_started",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="generated_candidate",
            resource_id=candidate_id,
            reason=reason,
            correlation_id=effective_correlation_id,
        )

        logger.info(
            "Corrective revalidation started",
            candidate_id=candidate_id,
            reason=reason,
            revalidation_run_id=revalidation_run_id,
        )

        # Build request params from generation request
        request_params = self._build_request_params(gen_request)

        # Load source bindings for citation resolution
        source_bindings = await self._load_source_bindings(gen_request.id)
        source_registry = self._build_source_registry(source_bindings)

        # Load existing candidates for duplicate detection
        existing_candidates = await self._load_other_candidates(candidate_id, gen_request.id)

        # Build V10 validation context for self-exclusion
        validation_context = {
            "current_candidate_id": candidate.candidate_id,
            "generation_request_id": gen_request.request_id,
            "current_normalized_payload_hash": candidate.normalized_payload_hash or "",
            "current_raw_response_hash": candidate.raw_response_hash or "",
        }

        # Run full validation pipeline
        orchestrator = ValidationOrchestrator(self.db)
        validation_run = await orchestrator.run_full_validation(
            candidate=candidate,
            request_params=request_params,
            existing_candidates=existing_candidates,
            validation_context=validation_context,
            source_registry=source_registry,
        )

        # Verify candidate content didn't change during revalidation
        content_hash_after = self._compute_candidate_hash(candidate)
        if content_hash_before != content_hash_after:
            raise CandidateRevalidationError(
                "Candidate content hash changed during revalidation — REJECTED"
            )

        # Record validator-specific audit events
        # Load validation results directly (avoids async lazy loading issues)
        from app.certification_core.models.generation_models import CandidateValidationResult
        vr_rows = await self.db.execute(
            select(CandidateValidationResult).where(
                CandidateValidationResult.validation_run_id == validation_run.id
            ).order_by(CandidateValidationResult.validator_code)
        )
        vr_results_list = list(vr_rows.scalars().all())

        v3_result = next(
            (r for r in vr_results_list if r.validator_code == "V3"), None
        )
        if v3_result:
            await self.audit.record(
                action="candidate_validator_v3_corrective_run_completed",
                actor_id=actor_id,
                actor_role=actor_role,
                resource_type="generated_candidate",
                resource_id=candidate_id,
                reason=f"V3 status: {v3_result.status}, reason: {v3_result.reason_code}",
                correlation_id=effective_correlation_id,
            )

        v10_result = next(
            (r for r in vr_results_list if r.validator_code == "V10"), None
        )
        if v10_result:
            await self.audit.record(
                action="candidate_validator_v10_corrective_run_completed",
                actor_id=actor_id,
                actor_role=actor_role,
                resource_type="generated_candidate",
                resource_id=candidate_id,
                reason=f"V10 status: {v10_result.status}, reason: {v10_result.reason_code}",
                correlation_id=effective_correlation_id,
            )

        await self.audit.record(
            action="candidate_corrective_revalidation_completed",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="generated_candidate",
            resource_id=candidate_id,
            reason=f"Decision: {validation_run.decision}",
            correlation_id=effective_correlation_id,
        )

        completed_at = datetime.now(timezone.utc)

        # Create review handoff if decision permits
        review_handoff = None
        if validation_run.decision == "READY_FOR_HUMAN_REVIEW":
            review_handoff = await self._create_corrective_review_handoff(
                candidate=candidate,
                validation_run=validation_run,
                validation_results=vr_results_list,
                gen_request=gen_request,
                correlation_id=effective_correlation_id,
                actor_id=actor_id,
                actor_role=actor_role,
            )

        # Update provenance with new validator versions
        await self._update_provenance(candidate, validation_run, vr_results_list)

        # Build result
        result = self._build_revalidation_result(
            candidate=candidate,
            gen_request=gen_request,
            validation_run=validation_run,
            validation_results=vr_results_list,
            revalidation_run_id=revalidation_run_id,
            reason=reason,
            started_at=started_at,
            completed_at=completed_at,
            content_hash_before=content_hash_before,
            content_hash_after=content_hash_after,
            review_handoff=review_handoff,
            existing_candidates_count=len(existing_candidates),
        )

        logger.info(
            "Corrective revalidation completed",
            candidate_id=candidate_id,
            decision=validation_run.decision,
            revalidation_run_id=revalidation_run_id,
        )

        return result

    async def _load_candidate(self, candidate_id: str) -> GeneratedCandidate | None:
        """Load a candidate by its candidate_id."""
        result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.candidate_id == candidate_id
            )
        )
        return result.scalar_one_or_none()

    async def _load_generation_request(self, db_id: str) -> GenerationRequest | None:
        """Load generation request by DB id."""
        result = await self.db.execute(
            select(GenerationRequest).where(GenerationRequest.id == db_id)
        )
        return result.scalar_one_or_none()

    async def _load_source_bindings(self, request_db_id: str) -> list[GenerationSourceBinding]:
        """Load source bindings for a generation request."""
        result = await self.db.execute(
            select(GenerationSourceBinding).where(
                GenerationSourceBinding.generation_request_id == request_db_id
            )
        )
        return list(result.scalars().all())

    async def _load_other_candidates(
        self, candidate_id: str, generation_request_id: str
    ) -> list[dict[str, Any]]:
        """Load candidates other than the current one for duplicate comparison.

        This loads candidates from the SAME generation request AND from OTHER
        generation requests to ensure cross-generation duplicate detection.
        """
        from app.certification_core.models.generation_models import GeneratedCandidate

        # Load all candidates except the current one
        result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.candidate_id != candidate_id
            )
        )
        candidates = list(result.scalars().all())
        return [
            {
                "candidate_id": c.candidate_id,
                "stem": c.stem,
                "options": c.options,
                "normalized_payload_hash": c.normalized_payload_hash,
            }
            for c in candidates
        ]

    def _build_request_params(self, gen_request: GenerationRequest) -> dict[str, Any]:
        """Build request params from a generation request."""
        return {
            "trusted_source_version_ids": gen_request.trusted_source_version_ids or [],
            "competency_id": gen_request.competency_id,
            "domain_id": gen_request.domain_id,
            "difficulty": gen_request.difficulty,
            "locale": gen_request.locale,
            "item_family_id": gen_request.item_family_id,
            "prompt_template_version": gen_request.prompt_template_version,
            "generation_policy_version": gen_request.generation_policy_version,
            "status": gen_request.status,
        }

    def _build_source_registry(self, bindings: list[GenerationSourceBinding]) -> list[dict[str, Any]]:
        """Build source registry from bindings for V3 citation resolution."""
        return [
            {
                "source_version_id": b.source_version_id,
                "source_checksum": b.source_checksum,
                "source_title": b.source_title,
                "source_locale": b.source_locale,
                "source_status": b.source_status,
            }
            for b in bindings
        ]

    def _compute_candidate_hash(self, candidate: GeneratedCandidate) -> str:
        """Compute a hash of the candidate's mutable content fields."""
        payload = {
            "stem": candidate.stem,
            "options": candidate.options,
            "answer_key": candidate.answer_key,
            "rationale": candidate.rationale,
            "rubric": candidate.rubric,
            "source_citations": candidate.source_citations,
            "item_type": candidate.item_type,
        }
        raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    async def _create_corrective_review_handoff(
        self,
        candidate: GeneratedCandidate,
        validation_run: CandidateValidationRun,
        validation_results: list,
        gen_request: GenerationRequest,
        correlation_id: str,
        actor_id: str,
        actor_role: str,
    ) -> CandidateReviewHandoff:
        """Create a review handoff for the revalidated candidate."""
        # Check if one already exists
        result = await self.db.execute(
            select(CandidateReviewHandoff).where(
                CandidateReviewHandoff.candidate_id == candidate.id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            logger.info(
                "Review handoff already exists for candidate",
                candidate_id=candidate.candidate_id,
                handoff_id=existing.handoff_id,
            )
            return existing

        # Collect warnings from validation run
        warnings = []
        for vr in validation_results:
            if vr.status == "warning":
                warnings.append({
                    "validator_code": vr.validator_code,
                    "reason_code": vr.reason_code,
                    "details": vr.details,
                })

        handoff = CandidateReviewHandoff(
            handoff_id=f"ho-cr-{uuid.uuid4().hex[:12]}",
            candidate_id=candidate.id,
            status="pending_human_review",
            validation_summary={
                "decision": validation_run.decision,
                "total_validators": validation_run.total_validators,
                "passed": validation_run.passed_count,
                "failed": validation_run.failed_count,
                "warnings": validation_run.warning_count,
                "critical_failures": validation_run.critical_failures,
                "major_failures": validation_run.major_failures,
                "validation_policy_version": validation_run.validation_policy_version,
                "revalidation": True,
            },
            warnings=warnings,
            reviewer_roles_allowed=["platform_admin", "domain_owner", "psychometric_reviewer"],
            forbidden_actions=[
                "publish",
                "approve",
                "add_to_pilot",
                "add_to_exam_eligible",
                "assemble_exam",
                "production_accept",
            ],
            human_review_completed=False,
            human_accepted=False,
            pilot_allowed=False,
            exam_eligible_allowed=False,
            publication_allowed=False,
        )
        self.db.add(handoff)
        await self.db.flush()

        await self.audit.record(
            action="candidate_review_handoff_created_corrective",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="review_handoff",
            resource_id=handoff.handoff_id,
            reason=f"Corrective revalidation decision: {validation_run.decision}",
            correlation_id=correlation_id,
        )

        return handoff

    async def _update_provenance(
        self,
        candidate: GeneratedCandidate,
        validation_run: CandidateValidationRun,
        validation_results: list,
    ) -> None:
        """Update candidate provenance with new validator versions."""
        result = await self.db.execute(
            select(CandidateProvenance).where(
                CandidateProvenance.candidate_id == candidate.id
            )
        )
        provenance = result.scalar_one_or_none()
        if provenance:
            current_versions = dict(provenance.validator_versions or {})
            current_versions.update({
                "revalidation_policy_version": VALIDATION_POLICY_VERSION,
                "revalidation_run_id": validation_run.validation_run_id,
            })
            # Add or update specific validator versions
            for vr in validation_results:
                current_versions[f"{vr.validator_code}_corrective"] = vr.validator_version
            provenance.validator_versions = current_versions

    def _build_revalidation_result(
        self,
        candidate: GeneratedCandidate,
        gen_request: GenerationRequest,
        validation_run: CandidateValidationRun,
        validation_results: list,
        revalidation_run_id: str,
        reason: str,
        started_at: datetime,
        completed_at: datetime,
        content_hash_before: str,
        content_hash_after: str,
        review_handoff: CandidateReviewHandoff | None,
        existing_candidates_count: int,
    ) -> dict[str, Any]:
        """Build the complete revalidation result dict."""
        # Gather individual validator results
        validator_details = []
        for vr in validation_results:
            validator_details.append({
                "validator_code": vr.validator_code,
                "validator_version": vr.validator_version,
                "status": vr.status,
                "severity": vr.severity,
                "reason_code": vr.reason_code,
                "details": vr.details,
                "executed_at": vr.executed_at.isoformat() if vr.executed_at else None,
            })

        return {
            "revalidation_run_id": revalidation_run_id,
            "candidate_id": candidate.candidate_id,
            "generation_request_id": gen_request.request_id,
            "reason": reason,
            "trigger_type": "controlled_corrective_revalidation",
            "provider_call_required": False,
            "generation_required": False,
            "retry": False,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "content_hash_before": content_hash_before,
            "content_hash_after": content_hash_after,
            "candidate_content_unchanged": content_hash_before == content_hash_after,
            "original_validation_run_preserved": True,
            "corrective_validation_run_appended": True,
            "validator_bundle_version": self.REVALIDATION_BUNDLE_VERSION,
            "validation_policy_version": VALIDATION_POLICY_VERSION,
            "original_provider": candidate.provider,
            "original_model": candidate.model,
            "previous_generation_request_id": gen_request.request_id,
            "validation": {
                "total_validators": validation_run.total_validators,
                "passed": validation_run.passed_count,
                "failed": validation_run.failed_count,
                "warnings": validation_run.warning_count,
                "not_run": validation_run.not_run_count,
                "critical_failures": validation_run.critical_failures,
                "major_failures": validation_run.major_failures,
                "decision": validation_run.decision,
                "decision_policy_version": validation_run.validation_policy_version,
            },
            "validator_details": validator_details,
            "review_handoff": {
                "created": review_handoff is not None,
                "handoff_id": review_handoff.handoff_id if review_handoff else None,
                "status": review_handoff.status if review_handoff else "not_created",
                "human_review_completed": review_handoff.human_review_completed if review_handoff else False,
                "human_accepted": review_handoff.human_accepted if review_handoff else False,
                "pilot_allowed": review_handoff.pilot_allowed if review_handoff else False,
                "exam_eligible_allowed": review_handoff.exam_eligible_allowed if review_handoff else False,
                "publication_allowed": review_handoff.publication_allowed if review_handoff else False,
            },
            "production_accepted": False,
            "release_allowed": False,
            "correlation_id_recorded": True,
            "append_only": True,
            "candidate_content_unchanged": content_hash_before == content_hash_after,
            "provider_call_executed": False,
            "generation_executed": False,
            "automatic_retry_executed": False,
            "manual_retry_executed": False,
        }
