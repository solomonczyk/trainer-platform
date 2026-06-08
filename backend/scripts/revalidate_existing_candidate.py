#!/usr/bin/env python3
"""Corrective revalidation CLI — revalidate an existing candidate without provider calls.

Usage:
    # Dry-run inspection (no changes)
    python scripts/revalidate_existing_candidate.py \\
        --candidate-id cand-c1a83dade217 \\
        --reason V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX

    # Execute revalidation
    python scripts/revalidate_existing_candidate.py \\
        --candidate-id cand-c1a83dade217 \\
        --reason V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX \\
        --execute

Environment:
    DATABASE_URL — default postgresql+asyncpg://trainer:trainer_pass@localhost:5432/trainer_platform
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.certification_core.services.generation_revalidation_service import (
    CandidateRevalidationService,
    CandidateRevalidationError,
)
from app.core.config import settings


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] {msg}", flush=True)


async def main() -> dict:
    parser = argparse.ArgumentParser(
        description="Corrective revalidation of an existing candidate"
    )
    parser.add_argument(
        "--candidate-id",
        required=True,
        help="Candidate ID to revalidate (e.g. cand-c1a83dade217)",
    )
    parser.add_argument(
        "--reason",
        required=True,
        help="Reason for revalidation",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute revalidation (without this flag, dry-run only)",
    )
    args = parser.parse_args()

    database_url = os.environ.get("DATABASE_URL") or settings.database_url

    log(f"Candidate ID:     {args.candidate_id}")
    log(f"Reason:           {args.reason}")
    log(f"Execute:          {args.execute}")
    log(f"Database URL:     {database_url.split('@')[0].split('://')[0]}://****@{database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    # Connect to database
    engine = create_async_engine(database_url)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    db = SessionLocal()

    try:
        # Verify connectivity
        result = await db.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar_one_or_none()
        log(f"Migration version: {version}")

        if not args.execute:
            log("=== DRY-RUN MODE ===")
            log("Inspecting candidate without executing revalidation...")

            # Just load the candidate for inspection
            from sqlalchemy import select
            from app.certification_core.models.generation_models import GeneratedCandidate

            result = await db.execute(
                select(GeneratedCandidate).where(
                    GeneratedCandidate.candidate_id == args.candidate_id
                )
            )
            candidate = result.scalar_one_or_none()
            if not candidate:
                log(f"ERROR: Candidate {args.candidate_id} not found")
                return {"status": "CANDIDATE_NOT_FOUND"}

            log(f"Candidate found:  {candidate.candidate_id}")
            log(f"Provider:         {candidate.provider}")
            log(f"Model:            {candidate.model}")
            log(f"Status:           {candidate.status}")
            log(f"Validation:       {candidate.validation_status}")
            log(f"Payload hash:     {candidate.normalized_payload_hash}")
            log(f"Item type:        {candidate.item_type}")
            log(f"Difficulty:       {candidate.difficulty}")
            log(f"Locale:           {candidate.locale}")
            log("")
            log("Dry-run complete. Pass --execute to run revalidation.")
            return {"status": "DRY_RUN_OK", "candidate_id": args.candidate_id}

        # Execute revalidation
        log("=== EXECUTING CORRECTIVE REVALIDATION ===")
        service = CandidateRevalidationService(db)
        result = await service.revalidate_existing_candidate(
            candidate_id=args.candidate_id,
            reason=args.reason,
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

        # Print validator details
        print("\nValidator results:")
        for v in result.get("validator_details", []):
            status_icon = "✅" if v["status"] == "passed" else "⚠️" if v["status"] == "warning" else "❌"
            print(f"  {status_icon} {v['validator_code']}: {v['status']} ({v.get('reason_code', '')})")

        return result

    except CandidateRevalidationError as e:
        log(f"REVALIDATION ERROR: {e}")
        return {"status": "REJECTED", "error": str(e)}
    except Exception as e:
        log(f"UNEXPECTED ERROR: {e}")
        raise
    finally:
        await db.close()
        await engine.dispose()


if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n" + "=" * 60)
    print("REVALIDATION RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
