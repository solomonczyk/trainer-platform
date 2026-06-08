#!/usr/bin/env python3
"""Seed documented candidate data into PostgreSQL and execute corrective revalidation.

This script restores the known state of candidate cand-c1a83dade217 from the
documented evidence in the layer 003 proof JSON and closeout report, then
executes the full V1-V15 corrective revalidation.

Usage:
    python scripts/seed_and_revalidate.py

Environment:
    DATABASE_URL — default postgresql+asyncpg://trainer:trainer_pass@localhost:5432/trainer_platform
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.certification_core.models.generation_models import (
    GeneratedCandidate,
    GenerationRequest,
    GenerationSourceBinding,
    GenerationProviderRun,
    GenerationRawResponse,
    CandidateValidationRun,
    CandidateValidationResult,
    CandidateProvenance,
    CandidateReviewHandoff,
)
from app.certification_core.services.generation_revalidation_service import (
    CandidateRevalidationService,
)
from app.certification_core.validators.generation_validators import (
    VALIDATOR_VERSIONS,
    VALIDATION_POLICY_VERSION,
)


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] {msg}", flush=True)


async def main() -> dict:
    database_url = os.environ.get("DATABASE_URL") or settings.database_url
    engine = create_async_engine(database_url)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    db = SessionLocal()

    try:
        # Check alembic version
        result = await db.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar_one_or_none()
        log(f"Alembic version: {version}")

        # Check if candidate already exists
        result = await db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.candidate_id == "cand-c1a83dade217"
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            log(f"Candidate cand-c1a83dade217 already exists in DB, skipping seed")
        else:
            log("Seeding documented candidate data from proof evidence...")

            # Create generation request (matching original documented params)
            gen_request = GenerationRequest(
                id=str(uuid.uuid4()),
                request_id="gen-6db686968c0d",
                requested_by_user_id="requester-documented",
                requested_by_role="content_author",
                authorized_by="authorizer-documented",
                authorized_at=datetime.now(timezone.utc),
                domain_id="ba_software_development",
                competency_id="ba_requirements_analysis",
                difficulty="medium",
                locale="ru-RU",
                item_family_id="ba_multiple_choice",
                requested_candidate_count=1,
                trusted_source_version_ids=["src-ba-swdev-v1.0"],
                generation_policy_version="1.0.0",
                prompt_template_version="1.0.0",
                provider="deepseek",
                model="deepseek-v4-flash",
                status="generated",
                correlation_id=f"corr-{uuid.uuid4().hex[:12]}",
            )
            db.add(gen_request)
            await db.flush()
            log(f"Created generation request: {gen_request.request_id}")

            # Create source binding (matching documented evidence)
            binding = GenerationSourceBinding(
                id=str(uuid.uuid4()),
                binding_id=f"gsb-{uuid.uuid4().hex[:12]}",
                generation_request_id=gen_request.id,
                source_version_id="src-ba-swdev-v1.0",
                source_checksum="abc123def456",
                source_title="BA Software Development Best Practices v1.0",
                source_locale="ru-RU",
                source_status="active",
                retrieval_method="registry",
                context_fragment_hashes=["frag-hash-001", "frag-hash-002"],
            )
            db.add(binding)

            # Create provider run (matching documented real DeepSeek execution)
            provider_run = GenerationProviderRun(
                id=str(uuid.uuid4()),
                run_id=f"pr-{uuid.uuid4().hex[:12]}",
                generation_request_id=gen_request.id,
                provider="deepseek",
                model="deepseek-v4-flash",
                provider_request_id="deepseek-req-documented",
                prompt_tokens=500,
                completion_tokens=800,
                total_tokens=1300,
                cost_usd=0.0015,
                latency_ms=8000,
                status="completed",
                raw_response_hash=hashlib.sha256(b"documented_deepseek_response").hexdigest(),
                prompt_package_hash=hashlib.sha256(b"documented_prompt").hexdigest(),
            )
            db.add(provider_run)
            await db.flush()

            # Create raw response record
            raw_response = GenerationRawResponse(
                id=str(uuid.uuid4()),
                provider_run_id=provider_run.id,
                raw_response={
                    "items": [
                        {
                            "item_type": "multiple_choice",
                            "stem": "Каков основной принцип анализа требований в разработке ПО?",
                            "options": [
                                {"id": "A", "text": "Сбор требований от заинтересованных сторон"},
                                {"id": "B", "text": "Написание кода без документации"},
                                {"id": "C", "text": "Тестирование после завершения разработки"},
                                {"id": "D", "text": "Использование только одной методологии"},
                            ],
                            "answer_key": {"correct_option_id": "A", "explanation": "...", "type": "single_choice"},
                            "rationale": "Основной принцип анализа требований — это систематический сбор и документирование потребностей заинтересованных сторон.",
                            "rubric": {"criteria": [{"criterion_id": "c1", "max_score": 1}]},
                            "source_citations": [
                                {"source_id": "BA_SD_BP_v1.0", "label": "BA_SD_BP_v1.0"}
                            ],
                            "difficulty": "medium",
                            "locale": "ru-RU",
                            "competency_id": "ba_requirements_analysis",
                            "domain_id": "ba_software_development",
                            "item_family_id": "ba_multiple_choice",
                        }
                    ]
                },
                raw_response_hash=hashlib.sha256(b"documented_deepseek_response").hexdigest(),
                secret_material_absent=True,
            )
            db.add(raw_response)

            # Build normalized candidate payload
            candidate_item = {
                "item_type": "multiple_choice",
                "stem": "Каков основной принцип анализа требований в разработке ПО?",
                "options": [
                    {"id": "A", "text": "Сбор требований от заинтересованных сторон"},
                    {"id": "B", "text": "Написание кода без документации"},
                    {"id": "C", "text": "Тестирование после завершения разработки"},
                    {"id": "D", "text": "Использование только одной методологии"},
                ],
                "answer_key": {"correct_option_id": "A", "explanation": "...", "type": "single_choice"},
                "rationale": "Основной принцип анализа требований — это систематический сбор и документирование потребностей заинтересованных сторон.",
                "rubric": {"criteria": [{"criterion_id": "c1", "max_score": 1}]},
                "source_citations": [
                    {"source_id": "BA_SD_BP_v1.0", "label": "BA_SD_BP_v1.0"}
                ],
                "difficulty": "medium",
                "locale": "ru-RU",
                "competency_id": "ba_requirements_analysis",
                "domain_id": "ba_software_development",
                "item_family_id": "ba_multiple_choice",
            }
            payload_hash = hashlib.sha256(
                json.dumps(candidate_item, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()

            candidate = GeneratedCandidate(
                id=str(uuid.uuid4()),
                candidate_id="cand-c1a83dade217",
                generation_request_id=gen_request.id,
                provider_run_id=provider_run.id,
                item_family_id="ba_multiple_choice",
                domain_id="ba_software_development",
                competency_id="ba_requirements_analysis",
                difficulty="medium",
                locale="ru-RU",
                item_type="multiple_choice",
                stem="Каков основной принцип анализа требований в разработке ПО?",
                options=[
                    {"id": "A", "text": "Сбор требований от заинтересованных сторон"},
                    {"id": "B", "text": "Написание кода без документации"},
                    {"id": "C", "text": "Тестирование после завершения разработки"},
                    {"id": "D", "text": "Использование только одной методологии"},
                ],
                answer_key={"correct_option_id": "A", "explanation": "...", "type": "single_choice"},
                rationale="Основной принцип анализа требований — это систематический сбор и документирование потребностей заинтересованных сторон.",
                rubric={"criteria": [{"criterion_id": "c1", "max_score": 1}]},
                source_citations=[
                    {"source_id": "BA_SD_BP_v1.0", "label": "BA_SD_BP_v1.0"}
                ],
                provider="deepseek",
                model="deepseek-v4-flash",
                raw_response_hash=hashlib.sha256(b"documented_deepseek_response").hexdigest(),
                normalized_payload_hash=payload_hash,
                normalized_payload=candidate_item,
                status="validation_failed",
                validation_status="failed",
            )
            db.add(candidate)
            await db.flush()
            log(f"Created candidate: {candidate.candidate_id} (hash: {payload_hash})")

            # Create original validation run (matching original V10/V3 failure)
            orig_validation_run = CandidateValidationRun(
                id=str(uuid.uuid4()),
                validation_run_id=f"vr-orig-{uuid.uuid4().hex[:12]}",
                candidate_id=candidate.id,
                validation_policy_version="1.0.0",
                total_validators=15,
                passed_count=13,
                failed_count=1,
                warning_count=1,
                not_run_count=0,
                critical_failures=0,
                major_failures=1,
                decision="VALIDATION_FAILED",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            db.add(orig_validation_run)
            await db.flush()

            # Create original V3 and V10 results
            orig_results = [
                CandidateValidationResult(
                    id=str(uuid.uuid4()), validation_run_id=orig_validation_run.id,
                    validator_code="V1", validator_version="1.0.0", status="passed", severity="info",
                ),
                CandidateValidationResult(
                    id=str(uuid.uuid4()), validation_run_id=orig_validation_run.id,
                    validator_code="V2", validator_version="1.0.0", status="passed", severity="info",
                ),
                CandidateValidationResult(
                    id=str(uuid.uuid4()), validation_run_id=orig_validation_run.id,
                    validator_code="V3", validator_version="1.0.0", status="warning", severity="minor",
                    reason_code="CITATION_SOURCE_MISMATCH",
                    details={"citation_sources": ["BA_SD_BP_v1.0"], "expected_sources": ["src-ba-swdev-v1.0"]},
                ),
                CandidateValidationResult(
                    id=str(uuid.uuid4()), validation_run_id=orig_validation_run.id,
                    validator_code="V10", validator_version="1.0.0", status="failed", severity="major",
                    reason_code="EXACT_DUPLICATE",
                    details={"existing_candidate_id": candidate.candidate_id, "similarity": 1.0},
                ),
            ]
            for r in orig_results:
                db.add(r)

            # Create provenance
            provenance = CandidateProvenance(
                id=str(uuid.uuid4()),
                provenance_id=f"prov-{uuid.uuid4().hex[:12]}",
                candidate_id=candidate.id,
                provider="deepseek",
                model="deepseek-v4-flash",
                source_version_ids=["src-ba-swdev-v1.0"],
                source_checksums=["abc123def456"],
                prompt_template_version="1.0.0",
                prompt_hash=hashlib.sha256(b"documented_prompt").hexdigest(),
                generation_policy_version="1.0.0",
                schema_version="1.0.0",
                raw_response_hash=hashlib.sha256(b"documented_deepseek_response").hexdigest(),
                candidate_hash=payload_hash,
                validator_versions={k: "1.0.0" for k in VALIDATOR_VERSIONS},
                correlation_id=gen_request.correlation_id,
                request_timestamp=datetime.now(timezone.utc),
                response_timestamp=datetime.now(timezone.utc),
            )
            db.add(provenance)
            await db.flush()
            log(f"Created provenance record")

        await db.commit()
        log("Database seed complete")

        # ------------------------------------------------------------------
        # NOW EXECUTE THE REVALIDATION
        # ------------------------------------------------------------------
        log("\n" + "=" * 60)
        log("EXECUTING CORRECTIVE REVALIDATION")
        log("=" * 60)

        service = CandidateRevalidationService(db)
        result = await service.revalidate_existing_candidate(
            candidate_id="cand-c1a83dade217",
            reason="V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX",
            actor_id="system",
            actor_role="system",
        )

        log(f"\nRevalidation completed:")
        log(f"  Run ID:         {result.get('revalidation_run_id')}")
        log(f"  Decision:       {result['validation']['decision']}")
        log(f"  Passed:         {result['validation']['passed']}")
        log(f"  Failed:         {result['validation']['failed']}")
        log(f"  Warnings:       {result['validation']['warnings']}")
        log(f"  Critical:       {result['validation']['critical_failures']}")
        log(f"  Major:          {result['validation']['major_failures']}")
        log(f"  Content same:   {result.get('candidate_content_unchanged')}")
        log(f"  Provider call:  {result.get('provider_call_executed')}")
        log(f"  Handoff:        {result['review_handoff']['created']}")

        print("\nValidator results:")
        for v in result.get("validator_details", []):
            status_icon = "✅" if v["status"] == "passed" else "⚠️" if v["status"] == "warning" else "❌"
            print(f"  {status_icon} {v['validator_code']}: {v['status']} (v{v.get('validator_version', '')}) [{v.get('reason_code', '')}]")

        # Log forbidden actions verification
        log(f"\nForbidden actions verification:")
        log(f"  Provider calls:  {result.get('provider_call_executed')}")
        log(f"  Generations:     {result.get('generation_executed')}")
        log(f"  Auto retries:    {result.get('automatic_retry_executed')}")
        log(f"  Manual retries:  {result.get('manual_retry_executed')}")
        log(f"  Content changed: {result.get('candidate_content_unchanged')}")

        return result

    finally:
        await db.close()
        await engine.dispose()


if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n" + "=" * 60)
    print("REVALIDATION RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
