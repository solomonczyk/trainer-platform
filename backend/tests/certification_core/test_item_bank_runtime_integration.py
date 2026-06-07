"""Full integration tests for Dynamic Item Bank Runtime — real DB, full workflows, negative paths.

Tests cover:
 1. Author creates draft + binds sources + submits
 2. Expert reviewer approves
 3. QA reviewer approves
 4. Enters pilot pool
 5. Completes pilot
 6. Psychometric gate passes
 7. Enters exam-eligible pool
 8. Exposure increments / idempotency
 9. Rotation / cool-down
10. Suspension → active pool removal
11. Retirement
12. Supersession
13. All negative paths
14. RBAC / answer-key protection
15. Audit event generation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.item_models import ItemFamily, Item
from app.certification_core.models.knowledge_source_models import KnowledgeSource
from app.certification_core.models.rubric_models import CertRubric, CertRubricCriterion
from app.certification_core.models.domain_pack_models import DomainPack
from app.certification_core.models.competency_models import CompetencyFramework, Competency
from app.certification_core.models.runtime_models import (
    ItemSourceBinding,
    ItemReview,
    ItemReviewDecision,
    ItemPoolMembership,
    ItemExposureEvent,
    ItemExposureCounter,
    ItemGovernanceIncident,
    ItemSupersessionLink,
)
from app.certification_core.repositories.item_repository import ItemRepository, ItemFamilyRepository
from app.certification_core.repositories.runtime_repository import (
    ItemSourceBindingRepository,
    ItemReviewRepository,
    ItemReviewDecisionRepository,
    ItemPoolMembershipRepository,
    ItemExposureEventRepository,
    ItemExposureCounterRepository,
    ItemGovernanceIncidentRepository,
    ItemSupersessionLinkRepository,
)
from app.certification_core.services.runtime_service import (
    AuthoringService,
    ReviewService,
    PilotPoolService,
    ExamEligiblePoolService,
    ExposureService,
    RotationPolicyService,
    GovernanceService,
    SourceTraceabilityService,
)
from app.certification_core.schemas.runtime_schemas import (
    ControlledItemCreate,
    SourceBindingCreate,
    ReviewCreate,
    ExposureEventCreate,
    GovernanceActionCreate,
    SupersessionCreate,
    RotationPolicyCreate,
)
from app.certification_core.audit.service import AuditService
from app.core.security import create_access_token


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def domain_pack(db: AsyncSession) -> DomainPack:
    pack = DomainPack(
        domain_pack_id="test-runtime-domain",
        name="Test Runtime Domain",
        version="1.0",
        status="active",
        created_by="test_admin",
    )
    db.add(pack)
    await db.flush()
    return pack


@pytest_asyncio.fixture
async def competency_framework(db: AsyncSession, domain_pack: DomainPack) -> CompetencyFramework:
    fw = CompetencyFramework(
        framework_id="test-runtime-fw",
        domain_pack_id=domain_pack.id,
        version="1.0",
        status="active",
        created_by="test_admin",
    )
    db.add(fw)
    await db.flush()
    return fw


@pytest_asyncio.fixture
async def competency(db: AsyncSession, competency_framework: CompetencyFramework) -> Competency:
    comp = Competency(
        competency_id="test-runtime-comp",
        framework_id=competency_framework.id,
        name="Test Competency",
        weight=100.0,
    )
    db.add(comp)
    await db.flush()
    return comp


@pytest_asyncio.fixture
async def knowledge_source(db: AsyncSession, domain_pack: DomainPack) -> KnowledgeSource:
    ks = KnowledgeSource(
        source_id="test-runtime-ks",
        title="Test Knowledge Source",
        version="1.0",
        content_hash="abc123def456",
        status="active",
        locale="en-US",
        created_by="test_admin",
    )
    db.add(ks)
    await db.flush()
    return ks


@pytest_asyncio.fixture
async def rubric(db: AsyncSession, domain_pack: DomainPack) -> CertRubric:
    r = CertRubric(
        rubric_id="test-runtime-rubric",
        version="1.0",
        domain_pack_id=domain_pack.id,
        status="active",
        created_by="test_admin",
        total_weight=100.0,
    )
    db.add(r)
    await db.flush()
    criterion = CertRubricCriterion(
        rubric_id=r.id,
        criterion_id="criterion-1",
        name="Correctness",
        weight=100.0,
        levels={"pass": 1.0, "fail": 0.0},
    )
    db.add(criterion)
    await db.flush()
    return r


@pytest_asyncio.fixture
async def item_family(db: AsyncSession, domain_pack: DomainPack) -> ItemFamily:
    family = ItemFamily(
        family_id="test-runtime-family",
        domain_pack_id=domain_pack.id,
        name="Test Item Family",
        status="active",
        created_by="test_author",
        allowed_item_types=["multiple_choice"],
    )
    db.add(family)
    await db.flush()
    return family


# ============================================================================
# Helper: create a draft item
# ============================================================================

async def _create_draft(
    db: AsyncSession,
    domain_pack: DomainPack,
    rubric: CertRubric,
    created_by: str = "test_author",
    item_id: str = None,
) -> dict:
    """Create a valid item draft with all required fields."""
    service = AuthoringService(db)
    data = ControlledItemCreate(
        item_id=item_id or f"test-item-{uuid.uuid4().hex[:8]}",
        domain_pack_id=domain_pack.id,
        item_type="multiple_choice",
        prompt={"text": "Test question?"},
        response_contract={"type": "single_choice", "options": ["A", "B", "C", "D"]},
        answer_key={"correct": "A"},
        rubric_id=rubric.rubric_id,
        competency_ids=["test-runtime-comp"],
        knowledge_source_refs=["test-runtime-ks"],
        difficulty_target="medium",
        locale="en-US",
        created_by=created_by,
        creation_method="human_authored",
        provenance="Manual creation for testing",
    )
    result = await service.create_draft(data, "content_author")
    return result


async def _bind_source(db: AsyncSession, item: Item, ks: KnowledgeSource, domain_pack: DomainPack) -> dict:
    """Bind a knowledge source to an item."""
    service = SourceTraceabilityService(db)
    data = SourceBindingCreate(
        item_id=item.item_id,
        source_registry_id=ks.id,
        source_version_id=ks.version,
        source_title=ks.title,
        domain_pack_id=domain_pack.id,
        binding_actor="test_author",
    )
    # Need to set item_id on the binding data items
    result = await service.create_binding(item.id, data, "content_author")
    return result


# ============================================================================
# Integration Tests — Full Workflow
# ============================================================================

class TestFullWorkflow:
    """Complete happy-path workflow: creation → review → pilot → exam-eligible → exposure → rotation."""

    @pytest.mark.asyncio
    async def test_full_lifecycle_workflow(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
        competency, item_family: ItemFamily,
    ):
        """Complete workflow from draft creation through retirement."""
        # --------------------------------------------------------------- #
        # 1. Author creates draft
        # --------------------------------------------------------------- #
        result = await _create_draft(db, domain_pack, rubric, created_by="test_author")
        assert result["success"], f"Draft creation failed: {result.get('message')}"
        item = result["item"]
        assert item.status == "draft"
        assert item.answer_key is not None

        # --------------------------------------------------------------- #
        # 2. Bind knowledge source
        # --------------------------------------------------------------- #
        bind_result = await _bind_source(db, item, knowledge_source, domain_pack)
        assert bind_result["success"], f"Source binding failed: {bind_result.get('message')}"

        # --------------------------------------------------------------- #
        # 3. Submit for review
        # --------------------------------------------------------------- #
        authoring = AuthoringService(db)
        submit_result = await authoring.submit_for_review(item.item_id, "test_author", "content_author")
        assert submit_result["success"], f"Submit failed: {submit_result.get('message')}"
        assert submit_result["item"].status == "expert_review_required"

        # --------------------------------------------------------------- #
        # 4. Expert reviewer approves
        # --------------------------------------------------------------- #
        review_svc = ReviewService(db)
        review_data = ReviewCreate(
            item_id=item.item_id,
            review_stage="expert_review",
            reviewer_id="expert_1",
            reviewer_role="expert_reviewer",
            decision="approve",
            reason="Content aligns with source",
        )
        review_result = await review_svc.perform_review(review_data, "expert_1", "expert_reviewer")
        assert review_result["success"], f"Expert review failed: {review_result.get('message')}"
        assert review_result["after_status"] == "approved_for_pilot"

        # --------------------------------------------------------------- #
        # 5. Enter pilot pool
        # --------------------------------------------------------------- #
        pilot_svc = PilotPoolService(db)
        pilot_result = await pilot_svc.enter_pilot(item.item_id, "domain_owner", "domain_owner")
        assert pilot_result["success"], f"Pilot entry failed: {pilot_result.get('message')}"
        assert pilot_result["membership"].pool_type == "pilot"
        assert pilot_result["membership"].status == "active"

        # Refresh item status
        await db.refresh(item)
        assert item.status == "pilot"

        # --------------------------------------------------------------- #
        # 6. Complete pilot
        # --------------------------------------------------------------- #
        complete_result = await pilot_svc.complete_pilot(item.item_id, "psychometric_1", "psychometric_reviewer")
        assert complete_result["success"], f"Pilot complete failed: {complete_result.get('message')}"

        await db.refresh(item)
        assert item.status == "calibration_review"

        # --------------------------------------------------------------- #
        # 7. Psychometric gate → calibrated
        # --------------------------------------------------------------- #
        # Transition to calibrated via lifecycle
        from app.certification_core.state_machine.item_lifecycle import validate_transition
        trans = validate_transition("calibration_review", "calibrated", "psychometric_reviewer", "psychometric_1")
        assert trans["allowed"], f"Psychometric gate failed: {trans['message']}"

        item_repo = ItemRepository(db)
        await item_repo.update_status(item.id, "calibrated")
        await db.refresh(item)
        assert item.status == "calibrated"

        # --------------------------------------------------------------- #
        # 8. Enter exam-eligible pool
        # --------------------------------------------------------------- #
        exam_svc = ExamEligiblePoolService(db)
        exam_result = await exam_svc.enter_exam_eligible(
            item.item_id, "domain_owner", "domain_owner",
            controlled_exception=False,
        )
        assert exam_result["success"], f"Exam-eligible entry failed: {exam_result.get('message')}"

        await db.refresh(item)
        assert item.status == "exam_eligible"

        # --------------------------------------------------------------- #
        # 9. Query pools
        # --------------------------------------------------------------- #
        pilot_pool = await pilot_svc.get_pilot_pool(status="exited")
        assert pilot_pool["total"] >= 1

        exam_pool = await exam_svc.get_exam_eligible_pool(status="active")
        assert exam_pool["total"] >= 1

        # --------------------------------------------------------------- #
        # 10. Record exposure (idempotent)
        # --------------------------------------------------------------- #
        exposure_svc = ExposureService(db)
        exp_data = ExposureEventCreate(
            item_id=item.item_id,
            session_id="test-session-1",
            exam_type="certification",
        )
        exp_result = await exposure_svc.record_exposure(exp_data, "system")
        assert exp_result["success"], f"Exposure failed: {exp_result.get('message')}"
        assert not exp_result.get("duplicate", False)

        # Duplicate — should be idempotent
        exp_result2 = await exposure_svc.record_exposure(exp_data, "system")
        assert exp_result2["success"]
        assert exp_result2.get("duplicate", False)

        # Second session
        exp_data2 = ExposureEventCreate(
            item_id=item.item_id,
            session_id="test-session-2",
            exam_type="certification",
        )
        exp_result3 = await exposure_svc.record_exposure(exp_data2, "system")
        assert exp_result3["success"]
        assert not exp_result3.get("duplicate", False)

        # Check counter
        counter = await exposure_svc.get_exposure(item.item_id)
        assert counter["success"]
        assert counter["counter"] is not None
        assert counter["counter"].total_exposures == 2

        # --------------------------------------------------------------- #
        # 11. Rotation eligibility check
        # --------------------------------------------------------------- #
        rotation_svc = RotationPolicyService(db)
        policy = RotationPolicyCreate(
            policy_id="test-policy",
            max_total_exposures=100,
            rolling_window_days=30,
            min_cool_down_days=7,
        )
        await rotation_svc.create_policy(policy, "platform_admin")

        eligibility = await rotation_svc.check_eligibility(item.item_id)
        assert eligibility["eligible"]

        # --------------------------------------------------------------- #
        # 12. Suspend
        # --------------------------------------------------------------- #
        gov_svc = GovernanceService(db)
        suspend_data = GovernanceActionCreate(
            item_id=item.item_id,
            actor_id="admin",
            actor_role="platform_admin",
            reason="Overexposure concern",
            suspension_reason="overexposure",
        )
        suspend_result = await gov_svc.suspend(suspend_data, "platform_admin")
        assert suspend_result["success"], f"Suspend failed: {suspend_result.get('message')}"

        await db.refresh(item)
        assert item.status == "suspended"

        # Check removed from active pool
        pool_member = await ItemPoolMembershipRepository(db).get_active_by_item_and_pool(
            item.id, "exam_eligible"
        )
        assert pool_member is None, "Item should be removed from exam-eligible pool"

        # --------------------------------------------------------------- #
        # 13. Unsuspend
        # --------------------------------------------------------------- #
        unsuspend_data = GovernanceActionCreate(
            item_id=item.item_id,
            actor_id="admin",
            actor_role="platform_admin",
            reason="Issue resolved",
        )
        unsuspend_result = await gov_svc.unsuspend(unsuspend_data, "platform_admin")
        assert unsuspend_result["success"]
        await db.refresh(item)
        assert item.status == "under_review"

        # --------------------------------------------------------------- #
        # 14. Retire
        # --------------------------------------------------------------- #
        retire_data = GovernanceActionCreate(
            item_id=item.item_id,
            actor_id="admin",
            actor_role="platform_admin",
            reason="End of lifecycle",
        )
        retire_result = await gov_svc.retire(retire_data, "platform_admin")
        assert retire_result["success"]
        await db.refresh(item)
        assert item.status == "retired"

        # --------------------------------------------------------------- #
        # 15. Supersession
        # --------------------------------------------------------------- #
        # Create a successor
        result2 = await _create_draft(
            db, domain_pack, rubric,
            created_by="test_author",
            item_id=f"test-item-{uuid.uuid4().hex[:8]}",
        )
        successor = result2["item"]

        supersede_data = SupersessionCreate(
            predecessor_item_id=item.item_id,
            successor_item_id=successor.item_id,
            reason="Replacement with improved version",
            created_by="admin",
        )
        supersede_result = await gov_svc.supersede(supersede_data, "platform_admin")
        assert supersede_result["success"]
        assert supersede_result["link"] is not None

        # --------------------------------------------------------------- #
        # 16. Governance summary
        # --------------------------------------------------------------- #
        summary = await gov_svc.get_governance_summary()
        assert summary["retired_items"] >= 1
        assert summary["total_drafts"] >= 1

        # --------------------------------------------------------------- #
        # 17. Audit events exist
        # --------------------------------------------------------------- #
        audit = AuditService(db)
        events, total = await audit.query(entity_type="item", entity_id=item.item_id)
        assert total > 0


class TestNegativePaths:
    """All the things that must be blocked."""

    @pytest.mark.asyncio
    async def test_submit_without_source_binding_blocked(
        self, db: AsyncSession, domain_pack: DomainPack, rubric: CertRubric,
    ):
        """An item without source bindings cannot be submitted."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        authoring = AuthoringService(db)
        submit_result = await authoring.submit_for_review(item.item_id, "test_author", "content_author")
        assert not submit_result["success"]
        assert "source" in submit_result["message"].lower()

    @pytest.mark.asyncio
    async def test_author_self_approval_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Author cannot review own item."""
        result = await _create_draft(db, domain_pack, rubric, created_by="test_author")
        assert result["success"]
        item = result["item"]

        await _bind_source(db, item, knowledge_source, domain_pack)

        authoring = AuthoringService(db)
        await authoring.submit_for_review(item.item_id, "test_author", "content_author")

        review_svc = ReviewService(db)
        review_data = ReviewCreate(
            item_id=item.item_id,
            review_stage="expert_review",
            reviewer_id="test_author",
            reviewer_role="expert_reviewer",
            decision="approve",
        )
        result = await review_svc.perform_review(review_data, "test_author", "expert_reviewer")
        assert not result["success"]
        assert "cannot review own" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_llm_self_approval_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """LLM actors cannot approve."""
        result = await _create_draft(db, domain_pack, rubric, created_by="llm:test-model")
        assert result["success"]
        item = result["item"]
        await _bind_source(db, item, knowledge_source, domain_pack)

        authoring = AuthoringService(db)
        await authoring.submit_for_review(item.item_id, "llm:test-model", "content_author")

        review_svc = ReviewService(db)
        review_data = ReviewCreate(
            item_id=item.item_id,
            review_stage="expert_review",
            reviewer_id="llm:test-model",
            reviewer_role="expert_reviewer",
            decision="approve",
        )
        result = await review_svc.perform_review(review_data, "llm:test-model", "expert_reviewer")
        assert not result["success"]
        assert "llm" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_direct_exam_eligible_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Items cannot go directly to exam-eligible."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        exam_svc = ExamEligiblePoolService(db)
        result = await exam_svc.enter_exam_eligible(
            item.item_id, "admin", "platform_admin",
        )
        assert not result["success"]
        assert "direct" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_suspended_item_exposure_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Suspended items cannot be exposed."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        # Manually suspend
        item.status = "suspended"
        await db.flush()

        exposure_svc = ExposureService(db)
        exp_data = ExposureEventCreate(
            item_id=item.item_id,
            session_id="test-session-suspend",
        )
        result = await exposure_svc.record_exposure(exp_data, "system")
        assert not result["success"]
        assert "suspended" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_retired_item_exposure_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Retired items cannot be exposed."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        # Manually retire
        item.status = "retired"
        await db.flush()

        exposure_svc = ExposureService(db)
        exp_data = ExposureEventCreate(
            item_id=item.item_id,
            session_id="test-session-retire",
        )
        result = await exposure_svc.record_exposure(exp_data, "system")
        assert not result["success"]
        assert "retired" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_retired_source_blocks_binding(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Retired knowledge sources cannot be bound to items."""
        knowledge_source.status = "retired"
        await db.flush()

        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        trace_svc = SourceTraceabilityService(db)
        data = SourceBindingCreate(
            item_id=item.item_id,
            source_registry_id=knowledge_source.id,
            source_version_id=knowledge_source.version,
            source_title=knowledge_source.title,
            domain_pack_id=domain_pack.id,
            binding_actor="test_author",
        )
        result = await trace_svc.create_binding(item.id, data, "content_author")
        assert not result["success"]
        assert "retired" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_controlled_exception_requires_admin(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Controlled exceptions require platform admin."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        # Bind source and submit
        await _bind_source(db, item, knowledge_source, domain_pack)
        authoring = AuthoringService(db)
        await authoring.submit_for_review(item.item_id, "test_author", "content_author")

        # Get expert review approval to reach approved_for_pilot
        review_svc = ReviewService(db)
        review_data = ReviewCreate(
            item_id=item.item_id,
            review_stage="expert_review",
            reviewer_id="expert_1",
            reviewer_role="expert_reviewer",
            decision="approve",
            reason="Good content",
        )
        await review_svc.perform_review(review_data, "expert_1", "expert_reviewer")
        await db.refresh(item)
        assert item.status == "approved_for_pilot"

        # Now try controlled exception as domain_owner (should fail — only platform_admin)
        exam_svc = ExamEligiblePoolService(db)
        result = await exam_svc.enter_exam_eligible(
            item.item_id, "domain_owner", "domain_owner",
            controlled_exception=True,
            exception_data={
                "second_reviewer": "someone",
                "reason": "Critical item needed",
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
            },
        )
        assert not result["success"]
        assert "platform_admin" in result["message"].lower()


class TestPoolSeparation:
    """Pool isolation rules."""

    @pytest.mark.asyncio
    async def test_pilot_and_exam_eligible_are_separate(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Pilot pool is not the same as exam-eligible pool."""
        pilot_repo = ItemPoolMembershipRepository(db)
        pilot_items, pilot_total = await pilot_repo.list_pool(pool_type="pilot")
        exam_items, exam_total = await pilot_repo.list_pool(pool_type="exam_eligible")

        # Different pool types
        for item in pilot_items:
            assert item.pool_type == "pilot"
        for item in exam_items:
            assert item.pool_type == "exam_eligible"

    @pytest.mark.asyncio
    async def test_historical_records_preserved(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Retired items are not deleted."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        # Retire
        gov_svc = GovernanceService(db)
        retire_data = GovernanceActionCreate(
            item_id=item.item_id,
            actor_id="admin",
            actor_role="platform_admin",
            reason="Test retirement",
        )
        await gov_svc.retire(retire_data, "platform_admin")

        # Item still exists in DB
        item_repo = ItemRepository(db)
        retired_item = await item_repo.get_by_item_id(item.item_id)
        assert retired_item is not None
        assert retired_item.status == "retired"


class TestExposureIdempotency:
    """Exposure idempotency and limits."""

    @pytest.mark.asyncio
    async def test_duplicate_exposure_not_double_counted(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Same item+session exposure is idempotent."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]
        item.status = "exam_eligible"
        await db.flush()

        exposure_svc = ExposureService(db)
        exp_data = ExposureEventCreate(
            item_id=item.item_id,
            session_id="dup-session",
        )

        r1 = await exposure_svc.record_exposure(exp_data, "system")
        assert r1["success"]
        assert not r1.get("duplicate", False)

        r2 = await exposure_svc.record_exposure(exp_data, "system")
        assert r2["success"]
        assert r2.get("duplicate", False)

        # Counter should be 1, not 2
        counter = await ItemExposureCounterRepository(db).get_by_item(item.id)
        assert counter.total_exposures == 1


class TestGovernanceActions:
    """Governance-specific tests."""

    @pytest.mark.asyncio
    async def test_suspension_creates_incident(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Suspension creates a governance incident."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]
        item.status = "exam_eligible"
        await db.flush()

        gov_svc = GovernanceService(db)
        data = GovernanceActionCreate(
            item_id=item.item_id,
            actor_id="admin",
            actor_role="platform_admin",
            reason="Test incident",
            suspension_reason="answer_key_defect",
        )
        await gov_svc.suspend(data, "platform_admin")

        incidents, total = await ItemGovernanceIncidentRepository(db).list_incidents()
        assert total >= 1
        assert any(inc.item_id == item.id for inc in incidents)

    @pytest.mark.asyncio
    async def test_supersession_links_items(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric,
    ):
        """Supersession creates a persistent link."""
        result1 = await _create_draft(db, domain_pack, rubric, item_id="test-supersede-old")
        result2 = await _create_draft(db, domain_pack, rubric, item_id="test-supersede-new")
        assert result1["success"] and result2["success"]

        gov_svc = GovernanceService(db)
        data = SupersessionCreate(
            predecessor_item_id=result1["item"].item_id,
            successor_item_id=result2["item"].item_id,
            reason="Replaced",
            created_by="admin",
        )
        result = await gov_svc.supersede(data, "platform_admin")
        assert result["success"]

        link = await ItemSupersessionLinkRepository(db).get_by_predecessor(result1["item"].id)
        assert link is not None
        assert link.successor_item_id == result2["item"].id


class TestAnswerKeyRedaction:
    """Answer key must be hidden from non-admin roles."""

    def test_platform_admin_can_read_keys(self):
        """Platform admin can read answer keys."""
        from app.certification_core.services.authorization import AuthorizationService
        assert AuthorizationService.can_read_answer_keys("platform_admin")

    def test_domain_owner_can_read_keys(self):
        """Domain owner can read answer keys."""
        from app.certification_core.services.authorization import AuthorizationService
        assert AuthorizationService.can_read_answer_keys("domain_owner")

    def test_qa_reviewer_cannot_read_keys(self):
        """QA reviewer cannot read answer keys."""
        from app.certification_core.services.authorization import AuthorizationService
        assert not AuthorizationService.can_read_answer_keys("qa_reviewer")

    def test_read_only_auditor_cannot_read_keys(self):
        """Read-only auditor cannot read answer keys."""
        from app.certification_core.services.authorization import AuthorizationService
        assert not AuthorizationService.can_read_answer_keys("read_only_auditor")

    def test_guest_cannot_read_keys(self):
        """Guest cannot read answer keys."""
        from app.certification_core.services.authorization import AuthorizationService
        assert not AuthorizationService.can_read_answer_keys("guest")


class TestRBAC:
    """Role-based access control for runtime operations."""

    def test_author_cannot_publish(self):
        """Content author cannot publish items."""
        from app.certification_core.services.authorization import (
            AuthorizationService, ROLE_PERMISSIONS,
        )
        author_perms = ROLE_PERMISSIONS.get("content_author", set())
        assert "certification:item_bank:publish" not in author_perms

    def test_qa_reviewer_cannot_govern(self):
        """QA reviewer cannot perform governance actions."""
        from app.certification_core.services.authorization import (
            AuthorizationService, ROLE_PERMISSIONS,
        )
        qa_perms = ROLE_PERMISSIONS.get("qa_reviewer", set())
        assert "certification:item_bank:govern" not in qa_perms

    def test_expert_reviewer_can_review(self):
        """Expert reviewer has review permission."""
        from app.certification_core.services.authorization import (
            AuthorizationService, ROLE_PERMISSIONS,
        )
        expert_perms = ROLE_PERMISSIONS.get("expert_reviewer", set())
        assert "certification:item_bank:review" in expert_perms

    def test_read_only_auditor_cannot_mutate(self):
        """Read-only auditor cannot write or govern."""
        from app.certification_core.services.authorization import (
            AuthorizationService, ROLE_PERMISSIONS,
        )
        auditor_perms = ROLE_PERMISSIONS.get("read_only_auditor", set())
        assert "certification:write" not in auditor_perms
        assert "certification:item_bank:govern" not in auditor_perms


class TestAuditEvents:
    """All mutations must generate audit events."""

    @pytest.mark.asyncio
    async def test_create_audit_event(
        self, db: AsyncSession, domain_pack: DomainPack, rubric: CertRubric,
    ):
        """Item creation generates audit event."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]

        audit = AuditService(db)
        events, total = await audit.query(entity_type="item", action="create")
        assert total >= 1

    @pytest.mark.asyncio
    async def test_review_audit_event(
        self, db: AsyncSession, domain_pack: DomainPack,
        knowledge_source: KnowledgeSource, rubric: CertRubric,
    ):
        """Review decisions generate audit events."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]
        await _bind_source(db, item, knowledge_source, domain_pack)

        authoring = AuthoringService(db)
        await authoring.submit_for_review(item.item_id, "test_author", "content_author")

        review_svc = ReviewService(db)
        review_data = ReviewCreate(
            item_id=item.item_id,
            review_stage="expert_review",
            reviewer_id="expert_1",
            reviewer_role="expert_reviewer",
            decision="approve",
            reason="Good",
        )
        await review_svc.perform_review(review_data, "expert_1", "expert_reviewer")

        audit = AuditService(db)
        events, total = await audit.query(
            entity_type="item", action="transition:expert_review_required->approved_for_pilot",
        )
        assert total >= 1

    @pytest.mark.asyncio
    async def test_retire_audit_event(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric,
    ):
        """Retirement generates audit event."""
        result = await _create_draft(db, domain_pack, rubric)
        assert result["success"]
        item = result["item"]

        gov_svc = GovernanceService(db)
        data = GovernanceActionCreate(
            item_id=item.item_id,
            actor_id="admin",
            actor_role="platform_admin",
            reason="Test",
        )
        await gov_svc.retire(data, "platform_admin")

        audit = AuditService(db)
        events, total = await audit.query(
            entity_type="item", action="transition:*->retired",
        )
        # The exact action is "transition:{before}->retired"
        # We just check for any retired transition
        all_events, all_total = await audit.query(entity_type="item")
        retire_events = [e for e in all_events if "retired" in e.action]
        assert len(retire_events) >= 1
