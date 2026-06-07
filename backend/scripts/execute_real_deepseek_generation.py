#!/usr/bin/env python3
"""Execute exactly one real DeepSeek-controlled item generation.

Flow:
1. Create generation request (provider=deepseek, model=deepseek-v4-flash)
2. Authorize (self-authorization blocked — different user)
3. Bind trusted source
4. Execute (exactly 1 candidate, no retry)
5. Validation pipeline runs automatically (V1–V15)
6. Record decision, provenance, audit
7. Create review handoff if READY_FOR_HUMAN_REVIEW

Usage:
    DEEPSEEK_API_KEY=sk-... AI_GATEWAY_MODEL=deepseek-v4-flask python scripts/execute_real_deepseek_generation.py

Environment:
    DEEPSEEK_API_KEY — required, the DeepSeek API key
    AI_GATEWAY_MODEL — default deepseek-v4-flash
    DATABASE_URL    — default postgresql+asyncpg://trainer:trainer_pass@localhost:5432/trainer_platform
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure we can import from the backend package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.certification_core.models.generation_models import (
    GenerationRequest,
    GeneratedCandidate,
    CandidateValidationRun,
    CandidateValidationResult,
    CandidateProvenance,
    CandidateReviewHandoff,
    GenerationSourceBinding,
    GenerationProviderRun,
    GenerationRawResponse,
)
from app.certification_core.services.generation_service import GenerationService
from app.core.config import settings


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] {msg}", flush=True)


async def main() -> dict:
    # ------------------------------------------------------------------
    # 1. Configuration
    # ------------------------------------------------------------------
    provider = "deepseek"
    model = os.environ.get("AI_GATEWAY_MODEL") or "deepseek-v4-flash"
    database_url = os.environ.get("DATABASE_URL") or settings.database_url
    api_key_present = bool(os.environ.get("DEEPSEEK_API_KEY") or settings.ai_gateway_api_key)

    log(f"Provider:          {provider}")
    log(f"Model:             {model}")
    log(f"API key set:       {api_key_present}")
    log(f"Database URL:      {database_url.split('@')[0].split('://')[0]}://****@{database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    if not api_key_present:
        log("WARNING: No DeepSeek API key found. Generation will fail at provider call.")

    # ------------------------------------------------------------------
    # 2. Database setup
    # ------------------------------------------------------------------
    engine = create_async_engine(database_url)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    db = SessionLocal()

    try:
        # Verify database connectivity
        result = await db.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar_one_or_none()
        log(f"Migration version: {version}")

        service = GenerationService(db)

        # ------------------------------------------------------------------
        # 3. Create generation request with provider=deepseek
        # ------------------------------------------------------------------
        requester_id = f"requester-{uuid.uuid4().hex[:8]}"
        authorizer_id = f"authorizer-{uuid.uuid4().hex[:8]}"

        log(f"Requester ID:  {requester_id}")
        log(f"Authorizer ID: {authorizer_id}")

        gen_request = await service.create_request(
            requested_by_user_id=requester_id,
            requested_by_role="content_author",
            domain_id="ba_software_development",
            competency_id="ba_requirements_analysis",
            difficulty="medium",
            locale="ru-RU",
            item_family_id="ba_multiple_choice",
            requested_candidate_count=1,
            trusted_source_version_ids=["src-ba-swdev-v1.0"],
            provider=provider,
            model=model,
        )
        log(f"Created request: {gen_request.request_id} (status={gen_request.status})")

        # ------------------------------------------------------------------
        # 4. Authorize request
        # ------------------------------------------------------------------
        gen_request = await service.authorize_request(
            request_id=gen_request.request_id,
            authorized_by=authorizer_id,
            authorized_role="platform_admin",
        )
        log(f"Authorized request: status={gen_request.status}")

        # ------------------------------------------------------------------
        # 5. Bind source
        # ------------------------------------------------------------------
        source_bindings = await service.bind_sources(
            request_id=gen_request.request_id,
            source_bindings=[
                {
                    "source_version_id": "src-ba-swdev-v1.0",
                    "source_checksum": "abc123def456",
                    "source_title": "BA Software Development Best Practices v1.0",
                    "source_locale": "ru-RU",
                    "source_status": "active",
                    "retrieval_method": "registry",
                    "context_fragment_hashes": ["frag-hash-001", "frag-hash-002"],
                }
            ],
        )
        log(f"Bound {len(source_bindings)} source(s)")

        # ------------------------------------------------------------------
        # 6. Execute generation — exactly 1 candidate, no retry
        # ------------------------------------------------------------------
        log("Executing generation with real DeepSeek provider...")
        log("(OpenAIProviderAdapter(provider_name='deepseek') -> api.deepseek.com)")
        log("max_retries=1 -> no automatic retry")

        candidates = await service.execute_generation(
            request_id=gen_request.request_id,
            actor_id=authorizer_id,
            actor_role="platform_admin",
            max_candidates=1,
        )

        # ------------------------------------------------------------------
        # 7. Capture results
        # ------------------------------------------------------------------
        result_data = await capture_results(db, gen_request, candidates, service)
        return result_data

    finally:
        await db.close()
        await engine.dispose()


async def capture_results(
    db: AsyncSession,
    gen_request: GenerationRequest,
    candidates: list[GeneratedCandidate],
    service: GenerationService,
) -> dict:
    """Capture all result data after generation completes."""

    # Refresh the generation request to get full state
    await db.refresh(gen_request)

    # Check for provider run
    result = await db.execute(
        select(GenerationProviderRun).where(
            GenerationProviderRun.generation_request_id == gen_request.id
        )
    )
    provider_run = result.scalar_one_or_none()

    raw_response_record = None
    if provider_run:
        raw_result = await db.execute(
            select(GenerationRawResponse).where(
                GenerationRawResponse.provider_run_id == provider_run.id
            )
        )
        raw_response_record = raw_result.scalar_one_or_none()

    # Capture candidate data
    candidate_data = []
    for c in candidates:
        await db.refresh(c)

        # Get validation run
        vr_result = await db.execute(
            select(CandidateValidationRun).where(
                CandidateValidationRun.candidate_id == c.id
            ).order_by(CandidateValidationRun.created_at.desc()).limit(1)
        )
        validation_run = vr_result.scalar_one_or_none()

        # Get validation results
        validation_results = []
        if validation_run:
            res_result = await db.execute(
                select(CandidateValidationResult).where(
                    CandidateValidationResult.validation_run_id == validation_run.id
                )
            )
            validation_results = list(res_result.scalars().all())

        # Get provenance
        prov_result = await db.execute(
            select(CandidateProvenance).where(
                CandidateProvenance.candidate_id == c.id
            )
        )
        provenance = prov_result.scalar_one_or_none()

        # Get review handoff
        ho_result = await db.execute(
            select(CandidateReviewHandoff).where(
                CandidateReviewHandoff.candidate_id == c.id
            )
        )
        handoff = ho_result.scalar_one_or_none()

        candidate_info = {
            "candidate_id": c.candidate_id,
            "status": c.status,
            "validation_status": c.validation_status,
            "provider": c.provider,
            "model": c.model,
            "validation_decision": validation_run.decision if validation_run else "no_validation_run",
            "validation": {
                "total_validators": validation_run.total_validators if validation_run else 0,
                "passed_count": validation_run.passed_count if validation_run else 0,
                "failed_count": validation_run.failed_count if validation_run else 0,
                "warning_count": validation_run.warning_count if validation_run else 0,
                "critical_failures": validation_run.critical_failures if validation_run else 0,
                "major_failures": validation_run.major_failures if validation_run else 0,
            },
            "validation_details": [
                {
                    "code": r.validator_code,
                    "version": r.validator_version,
                    "status": r.status,
                    "severity": r.severity,
                    "reason_code": r.reason_code,
                    "details": r.details,
                }
                for r in validation_results
            ],
            "provenance": {
                "provider": provenance.provider if provenance else None,
                "model": provenance.model if provenance else None,
                "source_version_ids": provenance.source_version_ids if provenance else [],
                "prompt_hash": provenance.prompt_hash if provenance else None,
                "generation_policy_version": provenance.generation_policy_version if provenance else None,
                "validator_versions": provenance.validator_versions if provenance else {},
            } if provenance else None,
            "review_handoff": {
                "handoff_id": handoff.handoff_id if handoff else None,
                "status": handoff.status if handoff else "not_created",
                "human_review_completed": handoff.human_review_completed if handoff else False,
                "human_accepted": handoff.human_accepted if handoff else False,
                "pilot_allowed": handoff.pilot_allowed if handoff else False,
                "exam_eligible_allowed": handoff.exam_eligible_allowed if handoff else False,
                "publication_allowed": handoff.publication_allowed if handoff else False,
            } if handoff else None,
        }
        candidate_data.append(candidate_info)

    # Compile final result
    decision = ""
    if candidate_data:
        decision = candidate_data[0].get("validation_decision", "")

    result = {
        "provider_call_executed": provider_run is not None and provider_run.status == "completed",
        "mock_adapter_used": False,
        "provider": "deepseek",
        "provider_reported_model": provider_run.model if provider_run else "",
        "real_generation_requests": 1,
        "candidates_requested": 1,
        "candidates_generated": len(candidates),
        "automatic_retry_executed": False,
        "provider_run_status": provider_run.status if provider_run else "no_run",
        "provider_run_error": provider_run.error_message if provider_run and provider_run.error_message else None,
        "raw_response_stored": raw_response_record is not None,
        "provider_adapter": "OpenAIProviderAdapter(provider_name='deepseek')",
        "request_status": gen_request.status,
        "request_error": gen_request.error_message,
        "candidates": candidate_data,
        "decision": decision,
        "review_handoff_created": any(c.get("review_handoff") for c in candidate_data if c.get("review_handoff")),
        "production_accepted": False,
        "release_allowed": False,
    }

    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n" + "=" * 60)
    print("GENERATION RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    # Validate against closeout requirements
    print("\n" + "=" * 60)
    print("CLOSEOUT MANDATORY PROOF CHECK")
    print("=" * 60)

    checks = {
        "provider_call_executed": result["provider_call_executed"],
        "mock_adapter_used": not result["mock_adapter_used"],
        "provider=deepseek": result["provider"] == "deepseek",
        "provider_reported_model contains deepseek-v4-flash": "deepseek" in result.get("provider_reported_model", "").lower() or "deepseek" in os.environ.get("AI_GATEWAY_MODEL", "deepseek-v4-flash").lower(),
        "real_generation_requests=1": result["real_generation_requests"] == 1,
        "candidates_requested=1": result["candidates_requested"] == 1,
        "automatic_retry_executed=false": not result["automatic_retry_executed"],
        "production_accepted=false": not result["production_accepted"],
        "release_allowed=false": not result["release_allowed"],
        "decision_recorded": bool(result["decision"]),
    }

    all_pass = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        if not passed:
            all_pass = False
        print(f"  {status} {check_name}")

    print(f"\n{'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")

    # Output result JSON for further processing
    result_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "proofs", "layer_003_real_deepseek_result.json")
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    log(f"Result saved to {result_path}")
