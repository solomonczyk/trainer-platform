"""Controlled exception contract tests — two-person control, expiration, audit.

Required negative tests:
- Missing reason
- Missing expiration
- Expiration in the past
- Requester tries to second-approve
- Author tries to approve
- No second reviewer
- Expired exception
- Revoked exception
- Exception applied to another item version
- Suspended item
- Retired item
- Invalid source
- Inactive rubric

Required positive test:
- platform_admin requests with reason and future expiration
- Independent second reviewer approves
- All non-psychometric gates pass
- Exam eligibility granted
- Complete audit history recorded
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.item_models import ItemFamily, Item
from app.certification_core.models.knowledge_source_models import KnowledgeSource
from app.certification_core.models.rubric_models import CertRubric, CertRubricCriterion
from app.certification_core.models.domain_pack_models import DomainPack
from app.certification_core.models.competency_models import CompetencyFramework, Competency
from app.certification_core.models.runtime_models import (
    ItemSourceBinding,
    ItemExceptionApproval,
)
from app.certification_core.repositories.item_repository import ItemRepository
from app.certification_core.repositories.runtime_repository import (
    ItemExceptionApprovalRepository,
)
from app.certification_core.services.runtime_service import (
    ControlledExceptionService,
    ExamEligibilityGateService,
    SourceTraceabilityService,
    AuthoringService,
)
from app.certification_core.schemas.runtime_schemas import (
    ControlledItemCreate,
    ExceptionRequestCreate,
    ExceptionApprovalFirst,
    ExceptionApprovalSecond,
    ExceptionRevocation,
    ExamEligibilityRequest,
)
from app.certification_core.audit.service import AuditService


# ============================================================================
# Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def domain_pack(db: AsyncSession) -> DomainPack:
    pack = DomainPack(
        domain_pack_id="test-exception-domain",
        name="Test Exception Domain",
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
        framework_id="test-exception-fw",
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
        competency_id="test-exception-comp",
        framework_id=competency_framework.id,
        name="Exception Test Competency",
        weight=100.0,
    )
    db.add(comp)
    await db.flush()
    return comp


@pytest_asyncio.fixture
async def knowledge_source(db: AsyncSession, domain_pack: DomainPack) -> KnowledgeSource:
    ks = KnowledgeSource(
        source_id="test-exception-ks",
        title="Exception Test KS",
        version="1.0",
        content_hash="exc123hash",
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
        rubric_id="test-exception-rubric",
        version="1.0",
        domain_pack_id=domain_pack.id,
        status="active",
        created_by="test_admin",
        total_weight=100.0,
    )
    db.add(r)
    await db.flush()
    return r


@pytest_asyncio.fixture
async def item_family(db: AsyncSession, domain_pack: DomainPack) -> ItemFamily:
    family = ItemFamily(
        family_id="test-exception-family",
        domain_pack_id=domain_pack.id,
        name="Exception Test Family",
        status="active",
        created_by="test_author",
        allowed_item_types=["multiple_choice"],
    )
    db.add(family)
    await db.flush()
    return family


async def _create_item_with_source(
    db: AsyncSession,
    domain_pack: DomainPack,
    rubric: CertRubric,
    knowledge_source: KnowledgeSource,
    created_by: str = "test_author",
    status: str = "calibrated",
    item_id: str = None,
) -> Item:
    """Create an item with source binding for exception testing."""
    item_repo = ItemRepository(db)
    item = Item(
        item_id=item_id or f"exc-item-{uuid.uuid4().hex[:8]}",
        domain_pack_id=domain_pack.id,
        version=1,
        item_type="multiple_choice",
        prompt={"text": "Exception test question?"},
        answer_key={"correct": "A"},
        rubric_id=rubric.rubric_id,
        competency_ids=["test-exception-comp"],
        difficulty_target="medium",
        locale="en-US",
        status=status,
        created_by=created_by,
    )
    db.add(item)
    await db.flush()

    # Create source binding
    binding = ItemSourceBinding(
        id=str(uuid.uuid4()),
        binding_id=f"bnd-{uuid.uuid4().hex[:12]}",
        item_id=item.id,
        source_registry_id=knowledge_source.id,
        source_version_id=knowledge_source.version,
        source_hash=knowledge_source.content_hash,
        source_title=knowledge_source.title,
        domain_pack_id=domain_pack.id,
        source_status_at_binding="active",
        binding_actor="test_author",
    )
    db.add(binding)
    await db.flush()
    return item


# ============================================================================
# NEGATIVE TESTS
# ============================================================================

class TestExceptionNegative:
    """All exception contract violations must be blocked."""

    @pytest.mark.asyncio
    async def test_missing_reason_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Exception request without reason is blocked."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        # Test service-level validation directly (Pydantic catches empty string)
        result = await svc.request_exception(
            ExceptionRequestCreate(
                item_id=item.item_id,
                reason=" ",  # Whitespace-only reason should fail service check
                requested_by="platform_admin_1",
                requester_role="platform_admin",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            ),
            "platform_admin",
        )
        assert not result["success"], "Should block missing reason"
        assert result.get("code") in ("REASON_REQUIRED",)

    @pytest.mark.asyncio
    async def test_missing_expiration_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Exception request without expiration is blocked."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        # Pydantic schema requires expires_at, so this should fail at schema level
        with pytest.raises(Exception):
            ExceptionRequestCreate(
                item_id=item.item_id,
                reason="Critical item needed for upcoming exam",
                requested_by="platform_admin_1",
                requester_role="platform_admin",
                expires_at=None,
            )

    @pytest.mark.asyncio
    async def test_expiration_in_past_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Exception with past expiration is blocked."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        data = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item needed",
            requested_by="platform_admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        result = await svc.request_exception(data, "platform_admin")
        assert not result["success"], "Should block past expiration"
        assert result.get("code") == "EXPIRATION_PAST"

    @pytest.mark.asyncio
    async def test_requester_cannot_second_approve(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Requester trying to second-approve own exception is blocked."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        # Request exception
        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"]
        exc = result["exception"]

        # First approve (as same person is allowed)
        first = ExceptionApprovalFirst(reviewer_id="admin_1", reviewer_role="platform_admin")
        result2 = await svc.first_approve(exc.exception_id, first, "platform_admin")
        assert result2["success"]

        # Second approve — requester cannot second-approve
        second = ExceptionApprovalSecond(
            reviewer_id="admin_1", reviewer_role="domain_owner",
            decision="approve",
        )
        result3 = await svc.second_approve(exc.exception_id, second, "domain_owner")
        assert not result3["success"], "Requester cannot second-approve"
        assert result3.get("code") == "SELF_APPROVAL_BLOCKED"

    @pytest.mark.asyncio
    async def test_author_cannot_approve_exception(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Item author cannot approve exception for their own item."""
        item = await _create_item_with_source(
            db, domain_pack, rubric, knowledge_source,
            created_by="item_author_1",
        )
        svc = ControlledExceptionService(db)

        # Request (platform admin, not author)
        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"]
        exc = result["exception"]

        # First approve
        first = ExceptionApprovalFirst(reviewer_id="reviewer_1", reviewer_role="domain_owner")
        await svc.first_approve(exc.exception_id, first, "domain_owner")

        # Author tries to second-approve
        second = ExceptionApprovalSecond(
            reviewer_id="item_author_1", reviewer_role="domain_owner",
            decision="approve",
        )
        result2 = await svc.second_approve(exc.exception_id, second, "domain_owner")
        assert not result2["success"], "Author cannot approve exception"
        assert result2.get("code") == "AUTHOR_APPROVAL_BLOCKED"

    @pytest.mark.asyncio
    async def test_no_second_reviewer_blocks_full_approval(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Exception without second approval stays pending."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"]
        exc = result["exception"]

        # Only first-approve — should remain pending/first_approved
        first = ExceptionApprovalFirst(reviewer_id="reviewer_1", reviewer_role="domain_owner")
        await svc.first_approve(exc.exception_id, first, "domain_owner")

        # Verify not fully approved
        assert exc.status == "first_approved", "Should not be fully approved yet"

    @pytest.mark.asyncio
    async def test_expired_exception_rejected(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Expired exception cannot be used for exam eligibility."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        # Create exception with very short expiration
        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"]
        exc = result["exception"]

        # Fully approve
        first = ExceptionApprovalFirst(reviewer_id="reviewer_1", reviewer_role="domain_owner")
        await svc.first_approve(exc.exception_id, first, "domain_owner")

        second = ExceptionApprovalSecond(
            reviewer_id="reviewer_2", reviewer_role="psychometric_reviewer",
            decision="approve",
        )
        await svc.second_approve(exc.exception_id, second, "psychometric_reviewer")
        assert exc.status == "approved"

        # Manually expire the exception
        exc.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        await db.flush()

        # Try to use for gate
        gate = ExamEligibilityGateService(db)
        result2 = await gate.evaluate_and_grant_exam_eligibility(
            item_id=item.item_id,
            evaluated_by="admin_1",
            evaluator_role="platform_admin",
            controlled_exception_id=exc.exception_id,
        )
        assert not result2["eligible"], "Expired exception should be rejected"

    @pytest.mark.asyncio
    async def test_revoked_exception_rejected(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Revoked exception cannot be used for exam eligibility."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"]
        exc = result["exception"]

        # Approve
        first = ExceptionApprovalFirst(reviewer_id="reviewer_1", reviewer_role="domain_owner")
        await svc.first_approve(exc.exception_id, first, "domain_owner")
        second = ExceptionApprovalSecond(
            reviewer_id="reviewer_2", reviewer_role="psychometric_reviewer",
            decision="approve",
        )
        await svc.second_approve(exc.exception_id, second, "psychometric_reviewer")

        # Revoke
        revoke = ExceptionRevocation(revoked_by="admin_2", reason="No longer needed")
        await svc.revoke_exception(exc.exception_id, revoke, "platform_admin")

        # Try to use
        gate = ExamEligibilityGateService(db)
        result2 = await gate.evaluate_and_grant_exam_eligibility(
            item_id=item.item_id,
            evaluated_by="admin_1",
            evaluator_role="platform_admin",
            controlled_exception_id=exc.exception_id,
        )
        assert not result2["eligible"], "Revoked exception should be rejected"

    @pytest.mark.asyncio
    async def test_suspended_item_blocks_exception(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Exception cannot be granted for suspended item."""
        item = await _create_item_with_source(
            db, domain_pack, rubric, knowledge_source,
            status="suspended",
        )
        svc = ControlledExceptionService(db)

        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert not result["success"], "Suspended item should block exception request"
        assert result.get("code") == "ITEM_SUSPENDED"

    @pytest.mark.asyncio
    async def test_retired_item_blocks_exception(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Exception cannot be granted for retired item."""
        item = await _create_item_with_source(
            db, domain_pack, rubric, knowledge_source,
            status="retired",
        )
        svc = ControlledExceptionService(db)

        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert not result["success"], "Retired item should block exception request"
        assert result.get("code") == "ITEM_RETIRED"

    @pytest.mark.asyncio
    async def test_wrong_role_cannot_request(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Non-platform_admin role cannot request exception."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="domain_owner_1",
            requester_role="domain_owner",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "domain_owner")
        assert not result["success"], "Non-admin should not be able to request exception"

    @pytest.mark.asyncio
    async def test_single_person_exception_blocked(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """First approver cannot also second-approve."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"]
        exc = result["exception"]

        # First approve (as reviewer_1)
        first = ExceptionApprovalFirst(reviewer_id="reviewer_1", reviewer_role="domain_owner")
        await svc.first_approve(exc.exception_id, first, "domain_owner")

        # Same person tries to second-approve
        second = ExceptionApprovalSecond(
            reviewer_id="reviewer_1", reviewer_role="psychometric_reviewer",
            decision="approve",
        )
        result2 = await svc.second_approve(exc.exception_id, second, "psychometric_reviewer")
        assert not result2["success"], "Single person exception blocked"
        assert result2.get("code") == "SINGLE_PERSON_EXCEPTION_BLOCKED"


# ============================================================================
# POSITIVE TEST — Full happy path
# ============================================================================

class TestExceptionPositive:
    """Full controlled exception workflow must succeed with audit."""

    @pytest.mark.asyncio
    async def test_full_exception_workflow(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Complete workflow: request → first approve → second approve → exam eligible → audit."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        # --------------------------------------------------------------- #
        # 1. Request exception (platform_admin)
        # --------------------------------------------------------------- #
        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Critical item required for upcoming certification exam window",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"], f"Exception request failed: {result}"
        exc = result["exception"]
        assert exc.status == "pending"
        assert exc.reason == req.reason
        assert exc.audit_correlation_id is not None

        # --------------------------------------------------------------- #
        # 2. First approval
        # --------------------------------------------------------------- #
        first = ExceptionApprovalFirst(reviewer_id="reviewer_1", reviewer_role="domain_owner")
        result2 = await svc.first_approve(exc.exception_id, first, "domain_owner")
        assert result2["success"], f"First approval failed: {result2}"
        assert exc.status == "first_approved"
        assert exc.first_approver == "reviewer_1"

        # --------------------------------------------------------------- #
        # 3. Second approval (independent reviewer)
        # --------------------------------------------------------------- #
        second = ExceptionApprovalSecond(
            reviewer_id="reviewer_2",
            reviewer_role="psychometric_reviewer",
            decision="approve",
        )
        result3 = await svc.second_approve(exc.exception_id, second, "psychometric_reviewer")
        assert result3["success"], f"Second approval failed: {result3}"
        assert exc.status == "approved"
        assert exc.second_reviewer == "reviewer_2"

        # --------------------------------------------------------------- #
        # 4. Grant exam eligibility via gate service
        # --------------------------------------------------------------- #
        gate = ExamEligibilityGateService(db)
        result4 = await gate.evaluate_and_grant_exam_eligibility(
            item_id=item.item_id,
            evaluated_by="admin_1",
            evaluator_role="platform_admin",
            controlled_exception_id=exc.exception_id,
        )
        assert result4["eligible"], f"Exam eligibility failed: {result4}"
        assert result4["exception_id"] == exc.exception_id

        # Refresh item
        item_repo = ItemRepository(db)
        refreshed = await item_repo.get_by_item_id(item.item_id)
        assert refreshed.status == "exam_eligible"

        # --------------------------------------------------------------- #
        # 5. Verify audit trail
        # --------------------------------------------------------------- #
        audit = AuditService(db)
        events, total = await audit.query(entity_type="item", entity_id=item.item_id)

        # Collect audit actions
        actions = [e.action for e in events]
        assert "exception_requested" in actions, f"Missing exception_requested: {actions}"
        assert "exception_first_approved" in actions, f"Missing exception_first_approved: {actions}"
        assert "exception_second_approved" in actions, f"Missing exception_second_approved: {actions}"
        assert "exam_eligibility_granted" in actions, f"Missing exam_eligibility_granted: {actions}"

        # Verify no sensitive data in audit
        for event in events:
            if event.reason:
                assert "answer_key" not in event.reason.lower()
                assert "secret" not in event.reason.lower()
                assert "password" not in event.reason.lower()

    @pytest.mark.asyncio
    async def test_exception_audit_contains_correlation(
        self, db: AsyncSession, domain_pack: DomainPack,
        rubric: CertRubric, knowledge_source: KnowledgeSource,
    ):
        """Exception audit events include correlation ID."""
        item = await _create_item_with_source(db, domain_pack, rubric, knowledge_source)
        svc = ControlledExceptionService(db)

        req = ExceptionRequestCreate(
            item_id=item.item_id,
            reason="Audit trail verification",
            requested_by="admin_1",
            requester_role="platform_admin",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        result = await svc.request_exception(req, "platform_admin")
        assert result["success"]
        exc = result["exception"]
        assert exc.audit_correlation_id is not None
        assert exc.audit_correlation_id.startswith("aud-")
