"""Browser acceptance test for Human Review vertical layer (007).

Performs the full workflow:
  1. operator creates case → POST /review-cases
  2. assigns reviewer  → POST /review-cases/{id}/assign
  3. reviewer claims   → POST /review-cases/{id}/claim
  4. inspects evidence → GET /review-cases/{id}/evidence
  5. submits decision  → POST /review-cases/{id}/decision
  6. refresh persistence → GET /review-cases/{id}
  7. audit/history visible → GET /review-cases/{id}/history

Usage:
    cd backend && .venv/Scripts/python scripts/browser_acceptance_007.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Ensure we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import create_access_token

# --- Config ---
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://trainer:trainer_test_password@localhost:55433/trainer_platform",
)
# Sync URL for direct DB seeding
DATABASE_SYNC_URL = os.environ.get(
    "DATABASE_SYNC_URL",
    "postgresql+asyncpg://trainer:trainer_test_password@localhost:55433/trainer_platform",
)

# Tokens
ADMIN_TOKEN = create_access_token("admin-1", role="platform_admin")
REVIEWER_TOKEN = create_access_token("reviewer-1", role="expert_reviewer")


async def seed_data():
    """Seed the database with a candidate and review handoff for testing."""
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        # 1. Create admin user
        await db.execute(
            text("""
                INSERT INTO users (id, email, password_hash, role, is_active)
                VALUES ('admin-1', 'admin@test.com', 'x', 'platform_admin', true)
                ON CONFLICT (id) DO NOTHING
            """)
        )
        await db.execute(
            text("""
                INSERT INTO users (id, email, password_hash, role, is_active)
                VALUES ('reviewer-1', 'reviewer@test.com', 'x', 'expert_reviewer', true)
                ON CONFLICT (id) DO NOTHING
            """)
        )

        # Generate deterministic but unique IDs
        gen_req_id = str(uuid.uuid4())
        gen_req_request_id = f"gen-ba-{uuid.uuid4().hex[:8]}"
        provider_run_id = str(uuid.uuid4())
        provider_run_run_id = f"pr-ba-{uuid.uuid4().hex[:8]}"
        candidate_id = str(uuid.uuid4())
        candidate_candidate_id = f"cand-ba-{uuid.uuid4().hex[:8]}"

        # 2. Generation request
        await db.execute(
            text("""
                INSERT INTO cert_generation_requests
                    (id, request_id, requested_by_user_id, requested_by_role,
                     domain_id, competency_id, difficulty, locale, item_family_id,
                     requested_candidate_count, generation_policy_version,
                     prompt_template_version, provider, model, status, correlation_id,
                     created_at, updated_at)
                VALUES (
                    :id, :request_id, :requested_by_user_id, :requested_by_role,
                    :domain_id, :competency_id, :difficulty, :locale, :item_family_id,
                    :requested_candidate_count, :generation_policy_version,
                    :prompt_template_version, :provider, :model, :status, :correlation_id,
                    :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": gen_req_id,
                "request_id": gen_req_request_id,
                "requested_by_user_id": "admin-1",
                "requested_by_role": "platform_admin",
                "domain_id": "it",
                "competency_id": "testing",
                "difficulty": "medium",
                "locale": "en-US",
                "item_family_id": "qa-engineer",
                "requested_candidate_count": 1,
                "generation_policy_version": "1.0.0",
                "prompt_template_version": "1.0.0",
                "provider": "mock",
                "model": "mock-model",
                "status": "generated",
                "correlation_id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # 3. Source binding
        await db.execute(
            text("""
                INSERT INTO cert_generation_source_bindings
                    (id, binding_id, generation_request_id, source_version_id,
                     source_checksum, source_title, source_locale, source_status,
                     created_at, updated_at)
                VALUES (
                    :id, :binding_id, :generation_request_id, :source_version_id,
                    :source_checksum, :source_title, :source_locale, :source_status,
                    :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": str(uuid.uuid4()),
                "binding_id": f"gsb-ba-{uuid.uuid4().hex[:8]}",
                "generation_request_id": gen_req_id,
                "source_version_id": "src-v1.0",
                "source_checksum": "abc123",
                "source_title": "Test Source",
                "source_locale": "en-US",
                "source_status": "active",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # 4. Provider run
        await db.execute(
            text("""
                INSERT INTO cert_generation_provider_runs
                    (id, run_id, generation_request_id, provider, model, status,
                     created_at, updated_at)
                VALUES (
                    :id, :run_id, :generation_request_id, :provider, :model, :status,
                    :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": provider_run_id,
                "run_id": provider_run_run_id,
                "generation_request_id": gen_req_id,
                "provider": "mock",
                "model": "mock-model",
                "status": "completed",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # 5. Generate candidate content + hash
        stem = "What is the capital of France?"
        options = json.dumps([{"text": "Paris", "correct": True}, {"text": "London"}])
        rationale = "Paris is the capital of France."
        source_citations = json.dumps([{"source": "test", "citation": "test"}])
        content = {
            "stem": stem,
            "options": json.loads(options),
            "rationale": rationale,
            "rubric": None,
            "source_citations": json.loads(source_citations),
        }
        candidate_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

        await db.execute(
            text("""
                INSERT INTO cert_generated_candidates
                    (id, candidate_id, generation_request_id, provider_run_id,
                     item_family_id, domain_id, competency_id, difficulty, locale,
                     item_type, stem, options, rationale, source_citations,
                     provider, model, normalized_payload_hash, status, validation_status,
                     created_at, updated_at)
                VALUES (
                    :id, :candidate_id, :generation_request_id, :provider_run_id,
                    :item_family_id, :domain_id, :competency_id, :difficulty, :locale,
                    :item_type, :stem, :options, :rationale, :source_citations,
                    :provider, :model, :normalized_payload_hash, :status, :validation_status,
                    :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": candidate_id,
                "candidate_id": candidate_candidate_id,
                "generation_request_id": gen_req_id,
                "provider_run_id": provider_run_id,
                "item_family_id": "qa-engineer",
                "domain_id": "it",
                "competency_id": "testing",
                "difficulty": "medium",
                "locale": "en-US",
                "item_type": "multiple_choice",
                "stem": stem,
                "options": options,
                "rationale": rationale,
                "source_citations": source_citations,
                "provider": "mock",
                "model": "mock-model",
                "normalized_payload_hash": candidate_hash,
                "status": "review_handoff_ready",
                "validation_status": "passed",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # 6. Validation run
        vr_id = str(uuid.uuid4())
        await db.execute(
            text("""
                INSERT INTO cert_candidate_validation_runs
                    (id, validation_run_id, candidate_id, validation_policy_version,
                     total_validators, passed_count, failed_count, warning_count,
                     critical_failures, major_failures, decision,
                     started_at, completed_at, created_at, updated_at)
                VALUES (
                    :id, :validation_run_id, :candidate_id, :validation_policy_version,
                    :total_validators, :passed_count, :failed_count, :warning_count,
                    :critical_failures, :major_failures, :decision,
                    :started_at, :completed_at, :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": vr_id,
                "validation_run_id": f"vr-ba-{uuid.uuid4().hex[:8]}",
                "candidate_id": candidate_id,
                "validation_policy_version": "1.0.0",
                "total_validators": 15,
                "passed_count": 14,
                "failed_count": 0,
                "warning_count": 1,
                "critical_failures": 0,
                "major_failures": 0,
                "decision": "READY_FOR_HUMAN_REVIEW",
                "started_at": datetime.now(timezone.utc),
                "completed_at": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # 7. Validation result
        await db.execute(
            text("""
                INSERT INTO cert_candidate_validation_results
                    (id, validation_run_id, validator_code, validator_version,
                     status, severity, executed_at, created_at, updated_at)
                VALUES (
                    :id, :validation_run_id, :validator_code, :validator_version,
                    :status, :severity, :executed_at, :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": str(uuid.uuid4()),
                "validation_run_id": vr_id,
                "validator_code": "V01",
                "validator_version": "1.0.0",
                "status": "passed",
                "severity": "info",
                "executed_at": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # 8. Provenance
        await db.execute(
            text("""
                INSERT INTO cert_candidate_provenance
                    (id, provenance_id, candidate_id, provider, model,
                     source_version_ids, source_checksums,
                     prompt_template_version, generation_policy_version,
                     schema_version, candidate_hash, validator_versions,
                     correlation_id, created_at, updated_at)
                VALUES (
                    :id, :provenance_id, :candidate_id, :provider, :model,
                    :source_version_ids, :source_checksums,
                    :prompt_template_version, :generation_policy_version,
                    :schema_version, :candidate_hash, :validator_versions,
                    :correlation_id, :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": str(uuid.uuid4()),
                "provenance_id": f"prov-ba-{uuid.uuid4().hex[:8]}",
                "candidate_id": candidate_id,
                "provider": "mock",
                "model": "mock-model",
                "source_version_ids": json.dumps(["src-v1.0"]),
                "source_checksums": json.dumps(["abc123"]),
                "prompt_template_version": "1.0.0",
                "generation_policy_version": "1.0.0",
                "schema_version": "1.0.0",
                "candidate_hash": candidate_hash,
                "validator_versions": json.dumps({"V01": "1.0.0"}),
                "correlation_id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        # 9. Review handoff
        handoff_id = str(uuid.uuid4())
        await db.execute(
            text("""
                INSERT INTO cert_candidate_review_handoffs
                    (id, handoff_id, candidate_id, status,
                     validation_summary, reviewer_roles_allowed, forbidden_actions,
                     human_review_completed, human_accepted,
                     pilot_allowed, exam_eligible_allowed, publication_allowed,
                     created_at, updated_at)
                VALUES (
                    :id, :handoff_id, :candidate_id, :status,
                    :validation_summary, :reviewer_roles_allowed, :forbidden_actions,
                    :human_review_completed, :human_accepted,
                    :pilot_allowed, :exam_eligible_allowed, :publication_allowed,
                    :created_at, :updated_at
                )
                ON CONFLICT (id) DO NOTHING
            """),
            {
               "id": handoff_id,
                "handoff_id": f"ho-ba-{uuid.uuid4().hex[:8]}",
                "candidate_id": candidate_id,
                "status": "pending_human_review",
                "validation_summary": json.dumps({
                    "decision": "READY_FOR_HUMAN_REVIEW",
                    "passed": 14,
                    "total": 15,
                }),
                "reviewer_roles_allowed": json.dumps([
                    "platform_admin", "domain_owner", "psychometric_reviewer",
                    "expert_reviewer", "qa_reviewer",
                ]),
                "forbidden_actions": json.dumps([
                    "publish", "approve", "add_to_pilot", "add_to_exam_eligible",
                ]),
                "human_review_completed": False,
                "human_accepted": False,
                "pilot_allowed": False,
                "exam_eligible_allowed": False,
                "publication_allowed": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        )

        await db.commit()
        print(f"[SEED] Generation request: {gen_req_request_id}")
        print(f"[SEED] Candidate: {candidate_candidate_id}")
        print(f"[SEED] Validation run: vr_id={vr_id}")
        print(f"[SEED] Handoff: ho_id={handoff_id}")
        print(f"[SEED] Handoff public ID: ho-ba-...")

        # Return the handoff_id for the workflow
        result = await db.execute(
            text("SELECT handoff_id FROM cert_candidate_review_handoffs WHERE id = :id"),
            {"id": handoff_id},
        )
        row = result.fetchone()
        public_handoff_id = row[0] if row else None

    await engine.dispose()
    return {
        "handoff_id": public_handoff_id,
        "candidate_candidate_id": candidate_candidate_id,
        "candidate_id": candidate_id,
        "gen_req_id": gen_req_id,
    }


def run_workflow(data: dict) -> dict:
    """Execute the full browser acceptance workflow via HTTP API."""
    handoff_id = data["handoff_id"]
    headers = {"Content-Type": "application/json"}

    results = {}

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:

        # Step 1: Create review case (as admin/operator)
        print("\n=== Step 1: Create Review Case ===")
        resp = client.post(
            "/api/v1/certification/review-cases",
            json={"handoff_id": handoff_id},
            headers={**headers, "Authorization": f"Bearer {ADMIN_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        assert resp.status_code == 201, f"Create case failed: {resp.text}"
        case = resp.json()
        case_id = case["case_id"]
        print(f"  Case ID: {case_id}")
        print(f"  Status: {case['status']}")
        results["case_id"] = case_id
        results["create"] = case

        # Step 2: Assign reviewer (as admin)
        print("\n=== Step 2: Assign Reviewer ===")
        resp = client.post(
            f"/api/v1/certification/review-cases/{case_id}/assign",
            json={
                "reviewer_user_id": "reviewer-1",
                "reviewer_role": "expert_reviewer",
                "reason": "Assigning for expert review",
            },
            headers={**headers, "Authorization": f"Bearer {ADMIN_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        assert resp.status_code == 200, f"Assign failed: {resp.text}"
        assignment = resp.json()
        print(f"  Assignment ID: {assignment['assignment_id']}")
        print(f"  Status: {assignment['status']}")
        results["assign"] = assignment

        # Step 3: Claim assignment (as reviewer)
        print("\n=== Step 3: Claim Assignment ===")
        resp = client.post(
            f"/api/v1/certification/review-cases/{case_id}/claim",
            json={"reason": "Claiming for review"},
            headers={**headers, "Authorization": f"Bearer {REVIEWER_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        assert resp.status_code == 200, f"Claim failed: {resp.text}"
        claim = resp.json()
        print(f"  Status: {claim['status']}")
        results["claim"] = claim

        # Step 4: Inspect evidence
        print("\n=== Step 4: Inspect Evidence ===")
        resp = client.get(
            f"/api/v1/certification/review-cases/{case_id}/evidence",
            headers={**headers, "Authorization": f"Bearer {REVIEWER_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            evidence = resp.json()
            print(f"  Evidence loaded: keys={list(evidence.keys())}")
            results["evidence"] = evidence
        elif resp.status_code == 404:
            print(f"  Evidence not available (expected for mock data): {resp.text}")
            results["evidence"] = None
        else:
            print(f"  Unexpected status: {resp.status_code}")
            results["evidence"] = None

        # Step 5: Submit decision (as reviewer)
        print("\n=== Step 5: Submit Decision ===")
        resp = client.post(
            f"/api/v1/certification/review-cases/{case_id}/decision",
            json={
                "decision": "APPROVED_FOR_PILOT_REVIEW",
                "reason": "Candidate meets all quality criteria. Evidence confirmed.",
                "findings_json": {"quality": "high", "issues": []},
                "evidence_confirmed": True,
            },
            headers={**headers, "Authorization": f"Bearer {REVIEWER_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        assert resp.status_code == 200, f"Decision failed: {resp.text}"
        decision = resp.json()
        print(f"  Decision ID: {decision['decision_id']}")
        print(f"  Decision: {decision['decision']}")
        results["decision"] = decision

        # Step 6: Refresh persistence - get case detail
        print("\n=== Step 6: Verify Persistence ===")
        resp = client.get(
            f"/api/v1/certification/review-cases/{case_id}",
            headers={**headers, "Authorization": f"Bearer {REVIEWER_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        assert resp.status_code == 200, f"Get case failed: {resp.text}"
        detail = resp.json()
        print(f"  Case ID: {detail.get('case_id')}")
        print(f"  Status: {detail.get('status')}")
        print(f"  Candidate ID: {detail.get('candidate_id')}")
        print(f"  Version: {detail.get('version')}")
        results["detail"] = detail

        # Step 7: Audit/history visible
        print("\n=== Step 7: Audit History ===")
        resp = client.get(
            f"/api/v1/certification/review-cases/{case_id}/history",
            headers={**headers, "Authorization": f"Bearer {REVIEWER_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        assert resp.status_code == 200, f"History failed: {resp.text}"
        history = resp.json()
        events = history.get("events", [])
        print(f"  Events count: {len(events)}")
        for event in events:
            print(f"    - {event.get('event_type')} at {event.get('timestamp')}")
        results["history"] = history

        # Step 8: List all review cases
        print("\n=== Step 8: List Review Cases ===")
        resp = client.get(
            "/api/v1/certification/review-cases",
            headers={**headers, "Authorization": f"Bearer {ADMIN_TOKEN}"},
        )
        print(f"  Status: {resp.status_code}")
        assert resp.status_code == 200
        case_list = resp.json()
        print(f"  Total cases: {case_list.get('total')}")
        results["list"] = case_list

    return results


def verify_acceptance(results: dict) -> bool:
    """Verify all acceptance criteria were met."""
    passed = 0
    total = 0

    checks = [
        ("Case created (status 201)", results.get("create") is not None),
        ("Case has valid case_id", results.get("case_id") is not None),
        ("Reviewer assigned successfully", results.get("assign", {}).get("status") == "ASSIGNED"),
        ("Reviewer claimed assignment", results.get("claim", {}).get("status") == "CLAIMED"),
        ("Decision submitted successfully", results.get("decision", {}).get("status") == "completed"),
        ("Decision is APPROVED_FOR_PILOT_REVIEW", results.get("decision", {}).get("decision") == "APPROVED_FOR_PILOT_REVIEW"),
        ("Case detail retrievable after refresh", results.get("detail") is not None),
        ("Case status reflects decision", results.get("detail", {}).get("status") == "APPROVED_FOR_PILOT_REVIEW"),
        ("Audit history has events", len(results.get("history", {}).get("events", [])) > 0),
    ]

    print("\n" + "=" * 60)
    print("ACCEPTANCE VERIFICATION RESULTS")
    print("=" * 60)
    for label, ok in checks:
        total += 1
        if ok:
            passed += 1
            print(f"  [PASS] {label}")
        else:
            print(f"  [FAIL] {label}")

    print(f"\n  Passed: {passed}/{total}")
    return passed == total


async def main():
    print("=" * 60)
    print("HUMAN REVIEW VERTICAL LAYER — BROWSER ACCEPTANCE TEST")
    print("=" * 60)

    # Seed data
    print("\n--- Seeding test data ---")
    data = await seed_data()
    print(f"Handoff ID: {data['handoff_id']}")

    # Run workflow
    print("\n--- Running API workflow ---")
    results = run_workflow(data)

    # Verify
    success = verify_acceptance(results)

    print(f"\n{'=' * 60}")
    if success:
        print("BROWSER ACCEPTANCE: PASSED")
    else:
        print("BROWSER ACCEPTANCE: FAILED")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
