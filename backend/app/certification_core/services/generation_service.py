"""Controlled item generation service — orchestrates the full generation pipeline.

Flow:
Authorized Generation Request
→ Generation Policy Gate
→ Source Snapshot Binding
→ Prompt Package Construction
→ AI Gateway
→ Provider Adapter
→ Raw Response Capture
→ Candidate Normalization
→ Schema Validation
→ Deterministic Validation
→ Semantic / AI Validation
→ Risk and Safety Decision
→ Candidate Persistence
→ Provenance Record
→ Audit Record
→ Human Review Queue
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_gateway.adapters.base import BaseProviderAdapter
from app.ai_gateway.adapters.mock import MockProviderAdapter
from app.certification_core.models.generation_models import (
    GenerationRequest,
    GenerationSourceBinding,
    GenerationProviderRun,
    GenerationRawResponse,
    GeneratedCandidate,
    CandidateValidationRun,
    CandidateProvenance,
    CandidateReviewHandoff,
)
from app.certification_core.services.generation_audit_service import GenerationAuditService
from app.certification_core.services.generation_validation_service import ValidationOrchestrator
from app.certification_core.services.prompt_package import (
    GENERATION_POLICY_VERSION,
    PROMPT_TEMPLATE_VERSION,
    SCHEMA_VERSION,
    build_generation_prompt,
    extract_json_from_response,
    hash_payload,
    hash_prompt,
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GenerationService:
    """Core service for controlled item generation."""

    VALID_STATUS_TRANSITIONS = {
        "draft": ["authorized"],
        "authorized": ["generating"],
        "generating": ["generated"],
        "generated": ["validation_in_progress"],
        "validation_in_progress": ["validation_failed", "review_handoff_ready", "rejected"],
        "validation_failed": ["draft"],
        "review_handoff_ready": [],
        "rejected": [],
        "cancelled": [],
    }

    FORBIDDEN_TRANSITIONS = [
        ("draft", "generated"),
        ("draft", "review_handoff_ready"),
        ("validation_failed", "generating"),
        ("review_handoff_ready", "exam_eligible"),
    ]

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = GenerationAuditService(db)

    # ------------------------------------------------------------------
    # Status Management
    # ------------------------------------------------------------------

    async def _transition_status(
        self, request: GenerationRequest, new_status: str, actor_id: str, actor_role: str
    ) -> None:
        """Apply a status transition with validation."""
        current = request.status
        allowed = self.VALID_STATUS_TRANSITIONS.get(current, [])

        if new_status not in allowed:
            raise ValueError(
                f"Forbidden transition: {current} → {new_status}. "
                f"Allowed: {allowed}"
            )

        # Check specific forbidden transitions
        if (current, new_status) in self.FORBIDDEN_TRANSITIONS:
            raise ValueError(
                f"Specifically forbidden transition: {current} → {new_status}"
            )

        old_status = request.status
        request.status = new_status
        if new_status in ("generated", "rejected", "cancelled"):
            request.completed_at = datetime.now(timezone.utc)

        await self.db.flush()

        # Audit
        action_map = {
            "authorized": "generation_request_authorized",
            "generating": "generation_started",
            "generated": "generation_request_completed",
        }
        action = action_map.get(new_status, f"request_status_{new_status}")
        await self.audit.record(
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="generation_request",
            resource_id=request.request_id,
            reason=f"Status transition: {old_status} → {new_status}",
            correlation_id=request.correlation_id,
        )

    # ------------------------------------------------------------------
    # Request Management
    # ------------------------------------------------------------------

    async def create_request(
        self,
        requested_by_user_id: str,
        requested_by_role: str,
        domain_id: str,
        competency_id: str,
        difficulty: str,
        locale: str,
        item_family_id: str,
        requested_candidate_count: int = 1,
        trusted_source_version_ids: list[str] | None = None,
        generation_policy_version: str = GENERATION_POLICY_VERSION,
        prompt_template_version: str = PROMPT_TEMPLATE_VERSION,
        provider: str = "mock",
        model: str = "mock-model",
    ) -> GenerationRequest:
        """Create a new generation request in draft status."""
        request_id = f"gen-{uuid.uuid4().hex[:12]}"
        correlation_id = str(uuid.uuid4())

        gen_request = GenerationRequest(
            request_id=request_id,
            requested_by_user_id=requested_by_user_id,
            requested_by_role=requested_by_role,
            domain_id=domain_id,
            competency_id=competency_id,
            difficulty=difficulty,
            locale=locale,
            item_family_id=item_family_id,
            requested_candidate_count=max(1, min(3, requested_candidate_count)),
            trusted_source_version_ids=trusted_source_version_ids or [],
            generation_policy_version=generation_policy_version,
            prompt_template_version=prompt_template_version,
            provider=provider,
            model=model,
            status="draft",
            correlation_id=correlation_id,
        )
        self.db.add(gen_request)
        await self.db.flush()

        await self.audit.record(
            action="generation_request_created",
            actor_id=requested_by_user_id,
            actor_role=requested_by_role,
            resource_type="generation_request",
            resource_id=request_id,
            correlation_id=correlation_id,
        )

        return gen_request

    async def authorize_request(
        self,
        request_id: str,
        authorized_by: str,
        authorized_role: str,
    ) -> GenerationRequest:
        """Authorize a generation request (status: draft → authorized)."""
        gen_request = await self._get_request(request_id)

        if gen_request.requested_by_user_id == authorized_by:
            raise PermissionError("Requester self-authorization is blocked")

        await self._transition_status(gen_request, "authorized", authorized_by, authorized_role)
        gen_request.authorized_by = authorized_by
        gen_request.authorized_at = datetime.now(timezone.utc)

        await self.db.flush()
        return gen_request

    async def bind_sources(
        self,
        request_id: str,
        source_bindings: list[dict[str, Any]],
    ) -> list[GenerationSourceBinding]:
        """Bind trusted source versions to a generation request."""
        gen_request = await self._get_request(request_id)
        bindings = []

        for src in source_bindings:
            binding = GenerationSourceBinding(
                binding_id=f"gsb-{uuid.uuid4().hex[:12]}",
                generation_request_id=gen_request.id,
                source_version_id=src.get("source_version_id", ""),
                source_checksum=src.get("source_checksum", ""),
                source_title=src.get("source_title", ""),
                source_locale=src.get("source_locale", ""),
                source_status=src.get("source_status", "active"),
                retrieval_method=src.get("retrieval_method", "registry"),
                context_fragment_hashes=src.get("context_fragment_hashes"),
            )
            self.db.add(binding)
            bindings.append(binding)

        await self.db.flush()
        return bindings

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute_generation(
        self,
        request_id: str,
        actor_id: str,
        actor_role: str,
        max_candidates: int = 1,
        generate_real: bool = False,
    ) -> list[GeneratedCandidate]:
        """Execute controlled generation for an authorized request."""
        gen_request = await self._get_request(request_id)

        if gen_request.status != "authorized":
            raise ValueError(f"Cannot execute generation: status is '{gen_request.status}', expected 'authorized'")

        # Validate source bindings
        source_bindings = await self._get_source_bindings(gen_request.id)
        if not source_bindings:
            raise ValueError("No trusted source bindings found. Generation blocked.")

        # Transition to generating
        candidate_count = max(1, min(max_candidates, 3))
        await self._transition_status(gen_request, "generating", actor_id, actor_role)

        # Build prompt
        system_prompt, user_prompt, combined_prompt = await self._build_prompt(gen_request, source_bindings)
        prompt_hash = hash_prompt(combined_prompt)
        system_hash = hash_prompt(system_prompt)

        # Resolve provider adapter
        provider_run = await self._call_provider(
            gen_request, combined_prompt, candidate_count
        )
        provider_run.prompt_package_hash = prompt_hash
        provider_run.prompt_package_system_prompt_hash = system_hash
        await self.db.flush()

        # Check if provider call succeeded
        if provider_run.status == "failed":
            gen_request.status = "generated"
            gen_request.error_message = provider_run.error_message
            await self.db.flush()
            return []

        # Parse and normalize candidates
        raw_response = await self._get_raw_response(provider_run)
        if not raw_response:
            return []

        candidates = await self._normalize_and_validate(
            gen_request=gen_request,
            provider_run=provider_run,
            raw_response_data=raw_response.raw_response,
            system_prompt_hash=system_hash,
            prompt_hash=prompt_hash,
            candidate_count=candidate_count,
        )

        # Update request status based on results
        if candidates:
            await self._transition_status(gen_request, "generated", actor_id, actor_role)
        else:
            gen_request.status = "generated"
            gen_request.error_message = "No valid candidates generated"

        await self.db.flush()
        return candidates

    async def _build_prompt(
        self,
        gen_request: GenerationRequest,
        source_bindings: list[GenerationSourceBinding],
    ) -> tuple[str, str, str]:
        """Build prompt package from request and source bindings."""
        context_fragments = []
        for binding in source_bindings:
            context_fragments.append({
                "title": binding.source_title,
                "source_version_id": binding.source_version_id,
                "source_checksum": binding.source_checksum,
            })

        return build_generation_prompt(
            domain=gen_request.domain_id,
            competency=gen_request.competency_id,
            difficulty=gen_request.difficulty,
            locale=gen_request.locale,
            context_fragments=context_fragments if context_fragments else None,
            candidate_count=gen_request.requested_candidate_count,
        )

    async def _call_provider(
        self,
        gen_request: GenerationRequest,
        prompt: str,
        candidate_count: int,
    ) -> GenerationProviderRun:
        """Call the configured AI provider for generation."""
        provider_run = GenerationProviderRun(
            run_id=f"pr-{uuid.uuid4().hex[:12]}",
            generation_request_id=gen_request.id,
            provider=gen_request.provider,
            model=gen_request.model,
            status="running",
        )
        self.db.add(provider_run)
        await self.db.flush()

        start_time = time.monotonic()
        raw_output: dict[str, Any] | None = None
        error_message = ""
        status = "completed"

        try:
            adapter = self._get_provider_adapter(gen_request.provider)
            # Use the adapter to generate
            raw_output = await self._call_adapter(adapter, prompt)
            latency_ms = int((time.monotonic() - start_time) * 1000)

            if raw_output:
                raw_hash = hashlib.sha256(
                    json.dumps(raw_output, sort_keys=True).encode("utf-8")
                ).hexdigest()

                # Store raw response
                raw_resp = GenerationRawResponse(
                    provider_run_id=provider_run.id,
                    raw_response=raw_output,
                    reasoning_content=raw_output.pop("reasoning_content", None) if isinstance(raw_output, dict) else None,
                    raw_response_hash=raw_hash,
                    secret_material_absent=True,
                )
                self.db.add(raw_resp)
                provider_run.raw_response_hash = raw_hash

            provider_run.latency_ms = latency_ms
            provider_run.status = "completed"

            # Audit
            await self.audit.record(
                action="provider_call_completed",
                actor_id=gen_request.requested_by_user_id,
                actor_role="system",
                resource_type="provider_run",
                resource_id=provider_run.run_id,
                correlation_id=gen_request.correlation_id,
            )

        except Exception as exc:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            error_message = str(exc)
            provider_run.status = "failed"
            provider_run.error_message = error_message
            provider_run.latency_ms = latency_ms

            await self.audit.record(
                action="provider_call_failed",
                actor_id=gen_request.requested_by_user_id,
                actor_role="system",
                resource_type="provider_run",
                resource_id=provider_run.run_id,
                reason=error_message,
                correlation_id=gen_request.correlation_id,
            )
            logger.error(f"Provider call failed: {error_message}")

        await self.db.flush()
        return provider_run

    async def _call_adapter(self, adapter: BaseProviderAdapter, prompt: str) -> dict:
        """Call provider adapter with generation prompt."""
        # All adapters use async generate_items
        return await adapter.generate_items(prompt)

    def _get_provider_adapter(self, provider_name: str) -> BaseProviderAdapter:
        """Get the appropriate provider adapter."""
        if provider_name == "mock":
            return MockProviderAdapter()
        elif provider_name in ("openai", "deepseek"):
            from app.ai_gateway.adapters.openai_adapter import OpenAIProviderAdapter
            return OpenAIProviderAdapter(provider_name=provider_name)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    async def _get_raw_response(
        self, provider_run: GenerationProviderRun
    ) -> GenerationRawResponse | None:
        """Get the raw response for a provider run."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        result = await self.db.execute(
            select(GenerationRawResponse).where(
                GenerationRawResponse.provider_run_id == provider_run.id
            )
        )
        return result.scalar_one_or_none()

    async def _normalize_and_validate(
        self,
        gen_request: GenerationRequest,
        provider_run: GenerationProviderRun,
        raw_response_data: dict[str, Any],
        system_prompt_hash: str,
        prompt_hash: str,
        candidate_count: int,
    ) -> list[GeneratedCandidate]:
        """Normalize provider output into candidates and run validation."""
        candidates = []

        # Extract items from response
        items = self._extract_items(raw_response_data)
        if not items:
            logger.warning("No items extracted from provider response")
            return []

        for idx, item_data in enumerate(items[:candidate_count]):
            # Normalize
            candidate_hash = hash_payload(item_data)
            candidate_id = f"cand-{uuid.uuid4().hex[:12]}"

            candidate = GeneratedCandidate(
                candidate_id=candidate_id,
                generation_request_id=gen_request.id,
                provider_run_id=provider_run.id,
                item_family_id=gen_request.item_family_id,
                domain_id=gen_request.domain_id,
                competency_id=gen_request.competency_id,
                difficulty=gen_request.difficulty,
                locale=gen_request.locale,
                item_type=item_data.get("item_type", "multiple_choice"),
                stem=item_data.get("stem", ""),
                options=item_data.get("options"),
                answer_key=item_data.get("answer_key"),
                rationale=item_data.get("rationale", ""),
                rubric=item_data.get("rubric"),
                source_citations=item_data.get("source_citations"),
                provider=gen_request.provider,
                model=gen_request.model,
                raw_response_hash=provider_run.raw_response_hash,
                normalized_payload_hash=candidate_hash,
                normalized_payload=item_data,
                status="generated",
                validation_status="pending",
            )
            self.db.add(candidate)
            await self.db.flush()

            await self.audit.record(
                action="candidate_normalized",
                actor_id="system",
                actor_role="system",
                resource_type="generated_candidate",
                resource_id=candidate_id,
                correlation_id=gen_request.correlation_id,
            )

            # Create provenance
            provenance = CandidateProvenance(
                provenance_id=f"prov-{uuid.uuid4().hex[:12]}",
                candidate_id=candidate.id,
                provider=gen_request.provider,
                model=gen_request.model,
                source_version_ids=gen_request.trusted_source_version_ids,
                source_checksums=[],
                prompt_template_version=gen_request.prompt_template_version,
                prompt_hash=prompt_hash,
                generation_policy_version=gen_request.generation_policy_version,
                schema_version=SCHEMA_VERSION,
                raw_response_hash=provider_run.raw_response_hash,
                candidate_hash=candidate_hash,
                validator_versions={},
                correlation_id=gen_request.correlation_id,
                request_timestamp=gen_request.created_at,
                response_timestamp=datetime.now(timezone.utc),
            )
            self.db.add(provenance)
            await self.db.flush()

            # Build request params for validation
            request_params = {
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

            # Load existing candidates for duplicate detection
            existing = await self._load_existing_candidates(gen_request.id)

            # Run validation
            await self.audit.record(
                action="candidate_validation_started",
                actor_id="system",
                actor_role="system",
                resource_type="generated_candidate",
                resource_id=candidate_id,
                correlation_id=gen_request.correlation_id,
            )

            orchestrator = ValidationOrchestrator(self.db)
            validation_run = await orchestrator.run_full_validation(
                candidate=candidate,
                request_params=request_params,
                existing_candidates=existing,
            )

            # Update provenance with validator versions
            provenance.validator_versions = orchestrator.get_validator_versions()

            # Update candidate status based on validation
            decision = validation_run.decision
            if decision == "REJECTED":
                candidate.status = "rejected"
                candidate.validation_status = "failed"
                await self.audit.record(
                    action="candidate_rejected",
                    actor_id="system",
                    actor_role="system",
                    resource_type="generated_candidate",
                    resource_id=candidate_id,
                    reason=f"Validation REJECTED: {validation_run.critical_failures} critical failures",
                    correlation_id=gen_request.correlation_id,
                )
            elif decision == "VALIDATION_FAILED":
                candidate.status = "validation_failed"
                candidate.validation_status = "failed"
                await self.audit.record(
                    action="candidate_validation_failed",
                    actor_id="system",
                    actor_role="system",
                    resource_type="generated_candidate",
                    resource_id=candidate_id,
                    reason=f"Validation FAILED: {validation_run.major_failures} major failures",
                    correlation_id=gen_request.correlation_id,
                )
            elif decision == "READY_FOR_HUMAN_REVIEW":
                candidate.status = "review_handoff_ready"
                candidate.validation_status = "passed"

                # Create review handoff
                await self._create_review_handoff(candidate, validation_run, gen_request)

            await self.db.flush()
            candidates.append(candidate)

        return candidates

    async def _create_review_handoff(
        self,
        candidate: GeneratedCandidate,
        validation_run: CandidateValidationRun,
        gen_request: GenerationRequest,
    ) -> CandidateReviewHandoff:
        """Create a human review handoff for a validated candidate."""
        handoff = CandidateReviewHandoff(
            handoff_id=f"ho-{uuid.uuid4().hex[:12]}",
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
            },
            warnings=[],
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
            action="candidate_review_handoff_created",
            actor_id="system",
            actor_role="system",
            resource_type="review_handoff",
            resource_id=handoff.handoff_id,
            correlation_id=gen_request.correlation_id,
        )

        return handoff

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_items(self, raw_response: dict) -> list[dict]:
        """Extract item candidates from provider raw response."""
        if not raw_response:
            return []

        items = raw_response.get("items", [])
        # Handle nested response structures
        if not items and isinstance(raw_response, dict):
            # Try common response shapes
            for key in ("candidates", "questions", "items", "output"):
                val = raw_response.get(key, [])
                if isinstance(val, list):
                    items = val
                    break
            if not items:
                # Check if the whole response is a single item
                if "stem" in raw_response or "item_type" in raw_response:
                    items = [raw_response]

        return items

    async def _load_existing_candidates(self, request_id: str) -> list[dict]:
        """Load existing candidates for duplicate detection."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.generation_request_id == request_id
            )
        )
        existing = result.scalars().all()
        return [
            {
                "candidate_id": c.candidate_id,
                "stem": c.stem,
                "options": c.options,
            }
            for c in existing
        ]

    async def _get_request(self, request_id: str) -> GenerationRequest:
        """Get a generation request by its request_id."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(GenerationRequest).where(
                GenerationRequest.request_id == request_id
            )
        )
        gen_request = result.scalar_one_or_none()
        if not gen_request:
            raise ValueError(f"Generation request not found: {request_id}")
        return gen_request

    async def _get_source_bindings(self, generation_request_db_id: str) -> list[GenerationSourceBinding]:
        """Get source bindings for a generation request."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(GenerationSourceBinding).where(
                GenerationSourceBinding.generation_request_id == generation_request_db_id
            )
        )
        return list(result.scalars().all())
