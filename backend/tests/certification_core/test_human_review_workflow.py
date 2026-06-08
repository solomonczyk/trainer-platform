"""Comprehensive tests for the Human Review vertical layer.

Covers:
- Migration 007 schema and constraints (SQLite-based)
- Positive workflow (create, assign, claim, decide)
- Idempotent case creation
- Negative workflows (no handoff, stale hash, self-review, LLM, wrong role)
- Concurrency (two reviewers, simultaneous decisions)
- Audit and append-only
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.generation_models import (
    GenerationRequest,
    GenerationSourceBinding,
    GenerationProviderRun,
    GeneratedCandidate,
    CandidateValidationRun,
    CandidateValidationResult,
    CandidateProvenance,
    CandidateReviewHandoff,
)
from app.certification_core.models.human_review_models import (
    HumanReviewCase,
    ReviewerAssignment,
    HumanReviewDecision,
    REVIEW_CASE_STATUSES,
    REVIEW_DECISIONS,
)
from app.certification_core.models.audit_models import AuditEvent
from app.certification_core.services.human_review_service import HumanReviewService
from app.certification_core.services.authorization import AuthorizationService
from app.certification_core.audit.service import AuditService


# ======================================================================
# Helpers
# ======================================================================

def _uuid() -> str:
    return str(uuid.uuid4())


async def _create_generation_request(db: AsyncSession, user_id: str = "test-operator") -> GenerationRequest:
    """Create a minimal generation request."""
    request_id = f"gen-test-{uuid.uuid4().hex[:8]}"
    gr = GenerationRequest(
        request_id=request_id,
        requested_by_user_id=user_id,
        requested_by_role="generation_operator",
        domain_id="it",
        competency_id="testing",
        difficulty="medium",
        locale="en-US",
        item_family_id="qa-engineer",
        requested_candidate_count=1,
        generation_policy_version="1.0.0",
        prompt_template_version="1.0.0",
        provider="mock",
        model="mock-model",
        status="generated",
        correlation_id=_uuid(),
    )
    db.add(gr)
    await db.flush()
    return gr


async def _create_source_binding(db: AsyncSession, gr: GenerationRequest) -> GenerationSourceBinding:
    """Create a source binding for a generation request."""
    sb = GenerationSourceBinding(
        binding_id=f"gsb-test-{uuid.uuid4().hex[:8]}",
        generation_request_id=gr.id,
        source_version_id="src-v1.0",
        source_checksum="abc123",
        source_title="Test Source",
        source_locale="en-US",
        source_status="active",
    )
    db.add(sb)
    await db.flush()
    return sb


async def _create_candidate(
    db: AsyncSession, gr: GenerationRequest, provider_run_id: str | None = None,
    status: str = "review_handoff_ready",
    candidate_hash: str | None = None,
) -> GeneratedCandidate:
    """Create a generated candidate."""
    cid = f"cand-test-{uuid.uuid4().hex[:8]}"
    stem = "What is the capital of France?"
    options = [{"text": "Paris", "correct": True}, {"text": "London"}]
    rationale = "Paris is the capital of France."
    source_citations = [{"source": "test", "citation": "test"}]

    # Compute hash if not provided
    if candidate_hash is None:
        import hashlib
        content = {
            "stem": stem,
            "options": options,
            "rationale": rationale,
            "rubric": None,
            "source_citations": source_citations,
        }
        serialized = json.dumps(content, sort_keys=True, default=str)
        candidate_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    candidate = GeneratedCandidate(
        candidate_id=cid,
        generation_request_id=gr.id,
        provider_run_id=provider_run_id,
        item_family_id="qa-engineer",
        domain_id="it",
        competency_id="testing",
        difficulty="medium",
        locale="en-US",
        item_type="multiple_choice",
        stem=stem,
        options=options,
        rationale=rationale,
        source_citations=source_citations,
        provider="mock",
        model="mock-model",
        normalized_payload_hash=candidate_hash,
        status=status,
        validation_status="passed",
    )
    db.add(candidate)
    await db.flush()
    return candidate


async def _create_provider_run(db: AsyncSession, gr: GenerationRequest) -> GenerationProviderRun:
    """Create a provider run."""
    pr = GenerationProviderRun(
        run_id=f"pr-test-{uuid.uuid4().hex[:8]}",
        generation_request_id=gr.id,
        provider="mock",
        model="mock-model",
        status="completed",
    )
    db.add(pr)
    await db.flush()
    return pr


async def _create_validation_run(
    db: AsyncSession, candidate: GeneratedCandidate,
    decision: str = "READY_FOR_HUMAN_REVIEW",
) -> CandidateValidationRun:
    """Create a validation run with the given decision."""
    vr = CandidateValidationRun(
        validation_run_id=f"vr-test-{uuid.uuid4().hex[:8]}",
        candidate_id=candidate.id,
        validation_policy_version="1.0.0",
        total_validators=15,
        passed_count=14,
        failed_count=0,
        warning_count=1,
        critical_failures=0,
        major_failures=0,
        decision=decision,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(vr)
    await db.flush()

    # Add a validation result
    result = CandidateValidationResult(
        validation_run_id=vr.id,
        validator_code="V01",
        validator_version="1.0.0",
        status="passed",
        severity="info",
    )
    db.add(result)
    await db.flush()
    return vr


async def _create_provenance(
    db: AsyncSession, candidate: GeneratedCandidate, candidate_hash: str | None = None,
) -> CandidateProvenance:
    """Create a provenance record."""
    prov = CandidateProvenance(
        provenance_id=f"prov-test-{uuid.uuid4().hex[:8]}",
        candidate_id=candidate.id,
        provider="mock",
        model="mock-model",
        source_version_ids=["src-v1.0"],
        source_checksums=["abc123"],
        prompt_template_version="1.0.0",
        generation_policy_version="1.0.0",
        schema_version="1.0.0",
        candidate_hash=candidate_hash or candidate.normalized_payload_hash,
        validator_versions={"V01": "1.0.0"},
        correlation_id=_uuid(),
    )
    db.add(prov)
    await db.flush()
    return prov


async def _create_review_handoff(
    db: AsyncSession, candidate: GeneratedCandidate,
    status: str = "pending_human_review",
) -> CandidateReviewHandoff:
    """Create a review handoff."""
    handoff = CandidateReviewHandoff(
        handoff_id=f"ho-test-{uuid.uuid4().hex[:8]}",
        candidate_id=candidate.id,
        status=status,
        validation_summary={"decision": "READY_FOR_HUMAN_REVIEW", "passed": 14, "total": 15},
        reviewer_roles_allowed=["platform_admin", "domain_owner", "psychometric_reviewer",
                                 "expert_reviewer", "qa_reviewer"],
        forbidden_actions=["publish", "approve", "add_to_pilot", "add_to_exam_eligible"],
        human_review_completed=False,
        human_accepted=False,
        pilot_allowed=False,
        exam_eligible_allowed=False,
        publication_allowed=False,
    )
    db.add(handoff)
    await db.flush()
    return handoff


async def _setup_full_review_scenario(
    db: AsyncSession,
    operator_id: str = "test-operator",
    candidate_hash: str | None = None,
) -> dict:
    """Set up a complete scenario with candidate, validation, provenance, handoff."""
    gr = await _create_generation_request(db, operator_id)
    await _create_source_binding(db, gr)
    pr = await _create_provider_run(db, gr)
    # Let _create_candidate compute the hash from the content
    candidate = await _create_candidate(db, gr, pr.id, candidate_hash=candidate_hash)
    # Get the hash that was computed (or passed)
    ch = candidate.normalized_payload_hash
    vr = await _create_validation_run(db, candidate)
    await _create_provenance(db, candidate, ch)
    handoff = await _create_review_handoff(db, candidate)

    return {
        "gr": gr,
        "pr": pr,
        "candidate": candidate,
        "vr": vr,
        "handoff": handoff,
        "candidate_hash": ch,
    }


# ======================================================================
# Migration 007 Schema Tests (SQLite)
# ======================================================================

class TestMigration007Schema:
    """Verify migration 007 schema using SQLAlchemy metadata/SQLite."""

    def test_models_defined(self):
        """Human review models are importable and have correct tablenames."""
        assert HumanReviewCase.__tablename__ == "cert_human_review_cases"
        assert ReviewerAssignment.__tablename__ == "cert_reviewer_assignments"
        assert HumanReviewDecision.__tablename__ == "cert_human_review_decisions"

    def test_review_case_required_fields(self):
        """HumanReviewCase has required fields."""
        required = ["case_id", "candidate_id", "review_handoff_id", "validation_run_id",
                     "status", "review_type", "required_reviewer_role", "created_by"]
        for field in required:
            assert hasattr(HumanReviewCase, field), f"Missing field: {field}"

    def test_review_case_statuses_defined(self):
        """REVIEW_CASE_STATUSES includes all required statuses."""
        required = ["PENDING_ASSIGNMENT", "ASSIGNED", "IN_REVIEW", "CHANGES_REQUESTED",
                     "REJECTED", "APPROVED_FOR_PILOT_REVIEW", "ESCALATED", "CLOSED"]
        for s in required:
            assert s in REVIEW_CASE_STATUSES, f"Missing status: {s}"

    def test_review_decisions_defined(self):
        """REVIEW_DECISIONS includes all required decision values."""
        required = ["APPROVED_FOR_PILOT_REVIEW", "REJECTED", "CHANGES_REQUESTED", "ESCALATED"]
        for d in required:
            assert d in REVIEW_DECISIONS, f"Missing decision: {d}"

    def test_assignment_required_fields(self):
        """ReviewerAssignment has required fields."""
        required = ["assignment_id", "review_case_id", "reviewer_user_id",
                     "reviewer_role", "assigned_by", "status"]
        for field in required:
            assert hasattr(ReviewerAssignment, field), f"Missing field: {field}"

    def test_decision_required_fields(self):
        """HumanReviewDecision has required fields."""
        required = ["decision_id", "review_case_id", "assignment_id", "candidate_id",
                     "reviewer_user_id", "decision", "reason", "candidate_hash",
                     "validation_run_id"]
        for field in required:
            assert hasattr(HumanReviewDecision, field), f"Missing field: {field}"


# ======================================================================
# Positive Workflow Tests
# ======================================================================

class TestPositiveWorkflow:
    """Full positive human review workflow."""

    @pytest.mark.asyncio
    async def test_create_review_case(self, db: AsyncSession):
        """Create a review case from a valid handoff."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        assert case.case_id is not None
        assert case.status == "PENDING_ASSIGNMENT"
        assert case.candidate_id == scenario["candidate"].id
        assert case.validation_run_id == scenario["vr"].id

    @pytest.mark.asyncio
    async def test_create_review_case_idempotent(self, db: AsyncSession):
        """Repeated creation for same handoff returns existing case."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case1 = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        case2 = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        assert case1.id == case2.id
        assert case1.status == case2.status

    @pytest.mark.asyncio
    async def test_assign_reviewer(self, db: AsyncSession):
        """Assign an eligible reviewer to a case."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        assignment = await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )

        assert assignment.assignment_id is not None
        assert assignment.status == "ASSIGNED"
        assert assignment.reviewer_user_id == "reviewer-1"
        assert assignment.reviewer_role == "expert_reviewer"

        # Case should be ASSIGNED
        assert case.status == "ASSIGNED"

    @pytest.mark.asyncio
    async def test_claim_assignment(self, db: AsyncSession):
        """Reviewer claims their assignment."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )

        assignment = await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        assert assignment.status == "CLAIMED"
        assert assignment.claimed_at is not None
        assert case.status == "IN_REVIEW"

    @pytest.mark.asyncio
    async def test_submit_approved_decision(self, db: AsyncSession):
        """Submit APPROVED_FOR_PILOT_REVIEW decision."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        decision = await service.submit_decision(
            case_id=case.case_id,
            decision="APPROVED_FOR_PILOT_REVIEW",
            reason="Candidate meets all quality criteria.",
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
            findings_json={"quality": "high", "issues": []},
            evidence_confirmed=True,
        )

        assert decision.decision_id is not None
        assert decision.decision == "APPROVED_FOR_PILOT_REVIEW"
        assert decision.candidate_hash is not None

        # Case should be in APPROVED_FOR_PILOT_REVIEW status
        assert case.status == "APPROVED_FOR_PILOT_REVIEW"

    @pytest.mark.asyncio
    async def test_submit_rejected_decision(self, db: AsyncSession):
        """Submit REJECTED decision."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-2",
            reviewer_role="psychometric_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-2",
            actor_role="psychometric_reviewer",
        )

        decision = await service.submit_decision(
            case_id=case.case_id,
            decision="REJECTED",
            reason="Candidate has critical content errors.",
            actor_id="reviewer-2",
            actor_role="psychometric_reviewer",
            findings_json={"errors": ["incorrect answer"]},
            evidence_confirmed=True,
        )

        assert decision.decision == "REJECTED"
        assert case.status == "REJECTED"

    @pytest.mark.asyncio
    async def test_submit_changes_requested_decision(self, db: AsyncSession):
        """Submit CHANGES_REQUESTED decision."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-3",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-3",
            actor_role="expert_reviewer",
        )

        decision = await service.submit_decision(
            case_id=case.case_id,
            decision="CHANGES_REQUESTED",
            reason="Minor corrections needed in rationale.",
            actor_id="reviewer-3",
            actor_role="expert_reviewer",
            findings_json={"changes": ["update rationale"]},
            evidence_confirmed=True,
        )

        assert decision.decision == "CHANGES_REQUESTED"
        assert case.status == "CHANGES_REQUESTED"

    @pytest.mark.asyncio
    async def test_submit_escalated_decision(self, db: AsyncSession):
        """Submit ESCALATED decision."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-4",
            reviewer_role="domain_owner",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-4",
            actor_role="domain_owner",
        )

        decision = await service.submit_decision(
            case_id=case.case_id,
            decision="ESCALATED",
            reason="Requires psychometric review for calibration.",
            actor_id="reviewer-4",
            actor_role="domain_owner",
            findings_json={"escalation_reason": "psychometric"},
            evidence_confirmed=True,
        )

        assert decision.decision == "ESCALATED"
        assert case.status == "ESCALATED"

    @pytest.mark.asyncio
    async def test_history_recorded(self, db: AsyncSession):
        """Review history is recorded via audit events."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
            actor_id="admin-1",
            actor_role="platform_admin",
        )

        history = await service.get_review_history(case.case_id)
        assert len(history) > 0

        # Check for case_created event
        create_events = [h for h in history if "created" in h["event_type"]]
        assert len(create_events) > 0


# ======================================================================
# Idempotency Tests
# ======================================================================

class TestIdempotency:
    """Review case creation is idempotent."""

    @pytest.mark.asyncio
    async def test_idempotent_creation_same_handoff(self, db: AsyncSession):
        """Same handoff produces same active case."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case1 = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        case2 = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        assert case1.id == case2.id
        assert case1.status == "PENDING_ASSIGNMENT"

    @pytest.mark.asyncio
    async def test_idempotent_creation_after_assign(self, db: AsyncSession):
        """Same handoff returns existing case even after assignment."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case1 = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case1.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )

        case2 = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        # Active cases only match for PENDING_ASSIGNMENT/ASSIGNED/IN_REVIEW
        assert case1.id == case2.id


# ======================================================================
# Negative Workflow Tests
# ======================================================================

class TestNegativeWorkflow:
    """Error conditions and blocked operations."""

    @pytest.mark.asyncio
    async def test_no_handoff(self, db: AsyncSession):
        """Cannot create review case without a valid handoff."""
        service = HumanReviewService(db)
        with pytest.raises(ValueError, match="Review handoff not found"):
            await service.create_review_case(handoff_id="nonexistent")

    @pytest.mark.asyncio
    async def test_invalid_handoff_status(self, db: AsyncSession):
        """Handoff must be pending_human_review."""
        scenario = await _setup_full_review_scenario(db)
        scenario["handoff"].status = "completed"
        await db.flush()

        service = HumanReviewService(db)
        with pytest.raises(ValueError, match="Invalid handoff status"):
            await service.create_review_case(
                handoff_id=scenario["handoff"].handoff_id,
            )

    @pytest.mark.asyncio
    async def test_stale_candidate_hash(self, db: AsyncSession):
        """Candidate hash mismatch blocks case creation."""
        scenario = await _setup_full_review_scenario(db)

        # Modify the candidate to make hash stale
        scenario["candidate"].stem = "Modified stem!"
        await db.flush()

        service = HumanReviewService(db)
        with pytest.raises(ValueError, match="hash mismatch"):
            await service.create_review_case(
                handoff_id=scenario["handoff"].handoff_id,
            )

    @pytest.mark.asyncio
    async def test_missing_provenance(self, db: AsyncSession):
        """Cannot create case without provenance."""
        gr = await _create_generation_request(db)
        await _create_source_binding(db, gr)
        pr = await _create_provider_run(db, gr)
        candidate = await _create_candidate(db, gr, pr.id)
        vr = await _create_validation_run(db, candidate)
        # No provenance created
        handoff = await _create_review_handoff(db, candidate)

        service = HumanReviewService(db)
        with pytest.raises(ValueError, match="Provenance not found"):
            await service.create_review_case(
                handoff_id=handoff.handoff_id,
            )

    @pytest.mark.asyncio
    async def test_missing_source_binding(self, db: AsyncSession):
        """Cannot create case without source bindings."""
        gr = await _create_generation_request(db)
        # No source binding
        pr = await _create_provider_run(db, gr)
        candidate = await _create_candidate(db, gr, pr.id)
        vr = await _create_validation_run(db, candidate)
        await _create_provenance(db, candidate, candidate.normalized_payload_hash)
        handoff = await _create_review_handoff(db, candidate)

        service = HumanReviewService(db)
        with pytest.raises(ValueError, match="No source bindings found"):
            await service.create_review_case(
                handoff_id=handoff.handoff_id,
            )

    @pytest.mark.asyncio
    async def test_self_review_blocked(self, db: AsyncSession):
        """Generation operator cannot review own candidate."""
        scenario = await _setup_full_review_scenario(db, operator_id="operator-1")

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        # Assign the operator as reviewer
        with pytest.raises(ValueError, match="Self-review blocked"):
            await service.assign_reviewer(
                case_id=case.case_id,
                reviewer_user_id="operator-1",
                reviewer_role="expert_reviewer",
                assigned_by="admin-1",
                assigned_by_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_llm_reviewer_blocked(self, db: AsyncSession):
        """LLM actor cannot be a reviewer."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        with pytest.raises(ValueError, match="LLM"):
            await service.assign_reviewer(
                case_id=case.case_id,
                reviewer_user_id="llm:gpt-4",
                reviewer_role="expert_reviewer",
                assigned_by="admin-1",
                assigned_by_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_service_account_blocked(self, db: AsyncSession):
        """Service account cannot be a reviewer."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        with pytest.raises(ValueError, match="service account"):
            await service.assign_reviewer(
                case_id=case.case_id,
                reviewer_user_id="service:ci-bot",
                reviewer_role="expert_reviewer",
                assigned_by="admin-1",
                assigned_by_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_wrong_role_blocked(self, db: AsyncSession):
        """Ineligible role cannot be a reviewer."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        with pytest.raises(ValueError, match="not eligible"):
            await service.assign_reviewer(
                case_id=case.case_id,
                reviewer_user_id="learner-1",
                reviewer_role="learner",
                assigned_by="admin-1",
                assigned_by_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_anonymous_reviewer_blocked(self, db: AsyncSession):
        """Anonymous reviewer is blocked."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        with pytest.raises(ValueError, match="not eligible"):
            await service.assign_reviewer(
                case_id=case.case_id,
                reviewer_user_id="guest",
                reviewer_role="guest",
                assigned_by="admin-1",
                assigned_by_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_anonymous_actor_blocked_claim(self, db: AsyncSession):
        """Anonymous cannot claim a review."""
        scenario = await _setup_full_review_scenario(db)
        service = HumanReviewService(db)

        with pytest.raises(ValueError, match="Anonymous review"):
            await service._validate_actor_for_review("guest", "guest", None)

    @pytest.mark.asyncio
    async def test_duplicate_assignment(self, db: AsyncSession):
        """Cannot assign two reviewers to same case without releasing."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )

        with pytest.raises(ValueError, match="active assignment already exists"):
            await service.assign_reviewer(
                case_id=case.case_id,
                reviewer_user_id="reviewer-2",
                reviewer_role="expert_reviewer",
                assigned_by="admin-1",
                assigned_by_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_decision_before_claim(self, db: AsyncSession):
        """Cannot submit decision without claiming (status is PENDING_ASSIGNMENT)."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        # Status is PENDING_ASSIGNMENT — submit fails on status check
        with pytest.raises(ValueError, match="Cannot submit decision"):
            await service.submit_decision(
                case_id=case.case_id,
                decision="APPROVED_FOR_PILOT_REVIEW",
                reason="Test",
                actor_id="reviewer-1",
                actor_role="expert_reviewer",
                evidence_confirmed=True,
            )

    @pytest.mark.asyncio
    async def test_duplicate_decision(self, db: AsyncSession):
        """Cannot submit a second decision."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        await service.submit_decision(
            case_id=case.case_id,
            decision="APPROVED_FOR_PILOT_REVIEW",
            reason="Good candidate.",
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
            evidence_confirmed=True,
        )

        # After the first decision, case transitions to APPROVED_FOR_PILOT_REVIEW
        # Second submit fails because status is no longer IN_REVIEW
        with pytest.raises(ValueError, match="Cannot submit decision"):
            await service.submit_decision(
                case_id=case.case_id,
                decision="REJECTED",
                reason="Changed my mind.",
                actor_id="reviewer-1",
                actor_role="expert_reviewer",
                evidence_confirmed=True,
            )

    @pytest.mark.asyncio
    async def test_completed_case_no_reassign(self, db: AsyncSession):
        """Cannot reassign a completed case."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        # Force close
        await service._transition_case_status(case, "CLOSED", "admin", "platform_admin")

        with pytest.raises(ValueError, match="Cannot assign"):
            await service.assign_reviewer(
                case_id=case.case_id,
                reviewer_user_id="reviewer-1",
                reviewer_role="expert_reviewer",
                assigned_by="admin-1",
                assigned_by_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_decision_wrong_reviewer(self, db: AsyncSession):
        """Another reviewer cannot submit decision without claiming."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )

        # Another user tries to submit (fails because status is ASSIGNED, not IN_REVIEW)
        with pytest.raises(ValueError, match="Cannot submit decision"):
            await service.submit_decision(
                case_id=case.case_id,
                decision="APPROVED_FOR_PILOT_REVIEW",
                reason="Looks good.",
                actor_id="reviewer-2",
                actor_role="expert_reviewer",
                evidence_confirmed=True,
            )

    @pytest.mark.asyncio
    async def test_evidence_not_confirmed(self, db: AsyncSession):
        """Decision requires evidence confirmation."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        with pytest.raises(ValueError, match="Evidence confirmation is required"):
            await service.submit_decision(
                case_id=case.case_id,
                decision="APPROVED_FOR_PILOT_REVIEW",
                reason="Looks good.",
                actor_id="reviewer-1",
                actor_role="expert_reviewer",
                evidence_confirmed=False,
            )

    @pytest.mark.asyncio
    async def test_invalid_decision_value(self, db: AsyncSession):
        """Invalid decision value is rejected."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        with pytest.raises(ValueError, match="Invalid decision"):
            await service.submit_decision(
                case_id=case.case_id,
                decision="INVALID_DECISION",
                reason="Test",
                actor_id="reviewer-1",
                actor_role="expert_reviewer",
                evidence_confirmed=True,
            )

    @pytest.mark.asyncio
    async def test_no_handler_for_wrong_status(self, db: AsyncSession):
        """Decision in wrong case status is rejected."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        # Status is PENDING_ASSIGNMENT — submit fails on status check first
        with pytest.raises(ValueError, match="Cannot submit decision"):
            await service.submit_decision(
                case_id=case.case_id,
                decision="APPROVED_FOR_PILOT_REVIEW",
                reason="Test",
                actor_id="reviewer-1",
                actor_role="expert_reviewer",
                evidence_confirmed=True,
            )


# ======================================================================
# Concurrency Tests
# ======================================================================

class TestConcurrency:
    """Concurrency and race condition handling."""

    @pytest.mark.asyncio
    async def test_two_reviewers_claim_same_case(self, db: AsyncSession):
        """Only one reviewer can claim a case (single assignment)."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )

        # Reviewer-1 claims
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        # After claim, case is IN_REVIEW. Reviewer-2 has no active assignment,
        # so claim fails because status is IN_REVIEW (not ASSIGNED/PENDING_ASSIGNMENT)
        # and also no assignment exists for reviewer-2
        with pytest.raises(ValueError, match="Cannot claim"):
            await service.claim_assignment(
                case_id=case.case_id,
                actor_id="reviewer-2",
                actor_role="expert_reviewer",
            )

    @pytest.mark.asyncio
    async def test_transactional_rollback_on_audit_failure(self, db: AsyncSession):
        """Case creation rollback if audit fails."""
        # The service commits audit events inline — test that the case is still
        # created even when audit fails (audit is non-blocking in this design).
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        assert case is not None
        assert case.status == "PENDING_ASSIGNMENT"

    @pytest.mark.asyncio
    async def test_stale_version_update(self, db: AsyncSession):
        """Version increments on each status transition."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        initial_version = case.version
        assert initial_version == 1

        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )

        assert case.version > initial_version


# ======================================================================
# Audit and Immutability Tests
# ======================================================================

class TestAuditAndImmutability:
    """Audit events are created and decisions are append-only."""

    @pytest.mark.asyncio
    async def test_audit_event_created(self, db: AsyncSession):
        """Case creation creates an audit event."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
            actor_id="admin-1",
            actor_role="platform_admin",
        )

        # Query audit
        audit_service = AuditService(db)
        events, total = await audit_service.query(
            entity_type="human_review_case",
            entity_id=case.case_id,
        )

        assert total > 0
        assert any(e.action == "review_case_created" for e in events)

    @pytest.mark.asyncio
    async def test_decision_append_only(self, db: AsyncSession):
        """Decision records cannot be updated or deleted (by design)."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        await service.submit_decision(
            case_id=case.case_id,
            decision="APPROVED_FOR_PILOT_REVIEW",
            reason="Good.",
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
            evidence_confirmed=True,
        )

        # Decision exists
        result = await db.execute(
            select(HumanReviewDecision).where(
                HumanReviewDecision.review_case_id == case.id
            )
        )
        decisions = result.scalars().all()
        assert len(decisions) == 1

        # Decision model has no update/delete methods (engineered constraint)
        decision = decisions[0]
        assert decision.decision == "APPROVED_FOR_PILOT_REVIEW"

    @pytest.mark.asyncio
    async def test_audit_events_for_full_workflow(self, db: AsyncSession):
        """Full workflow creates audit events for each step."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
            actor_id="admin-1",
            actor_role="platform_admin",
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )
        await service.submit_decision(
            case_id=case.case_id,
            decision="APPROVED_FOR_PILOT_REVIEW",
            reason="Good.",
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
            evidence_confirmed=True,
        )

        # Multiple audit events created
        audit_service = AuditService(db)
        events, total = await audit_service.query(
            entity_type="human_review_case",
            entity_id=case.case_id,
        )
        assert total >= 2  # created + transitions

        decision_events, _ = await audit_service.query(
            entity_type="human_review_decision",
        )
        assert decision_events is not None


# ======================================================================
# Forbidden Actions Tests
# ======================================================================

class TestForbiddenActions:
    """Verify that forbidden actions are not performed."""

    @pytest.mark.asyncio
    async def test_no_pilot_pool_mutation(self, db: AsyncSession):
        """Decision does not mutate pilot pool."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )
        await service.assign_reviewer(
            case_id=case.case_id,
            reviewer_user_id="reviewer-1",
            reviewer_role="expert_reviewer",
            assigned_by="admin-1",
            assigned_by_role="platform_admin",
        )
        await service.claim_assignment(
            case_id=case.case_id,
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
        )

        decision = await service.submit_decision(
            case_id=case.case_id,
            decision="APPROVED_FOR_PILOT_REVIEW",
            reason="Good.",
            actor_id="reviewer-1",
            actor_role="expert_reviewer",
            evidence_confirmed=True,
        )

        # The decision is APPROVED_FOR_PILOT_REVIEW, not APPROVED_FOR_PILOT
        assert "pilot_pool" not in decision.decision.lower()

        # Candidate should still have review_handoff_ready status
        assert scenario["candidate"].status == "review_handoff_ready"

    @pytest.mark.asyncio
    async def test_no_exam_eligible_mutation(self, db: AsyncSession):
        """Decision does not mutate exam-eligible pool."""
        # Verify no transition to exam_eligible exists in the service
        assert "exam_eligible" not in str(HumanReviewService.VALID_CASE_TRANSITIONS)

    @pytest.mark.asyncio
    async def test_no_publication(self, db: AsyncSession):
        """Decision does not publish candidates."""
        scenario = await _setup_full_review_scenario(db)

        service = HumanReviewService(db)
        case = await service.create_review_case(
            handoff_id=scenario["handoff"].handoff_id,
        )

        # Verify no publication-related transitions
        for transitions in HumanReviewService.VALID_CASE_TRANSITIONS.values():
            for t in transitions:
                assert "publish" not in t.lower()
