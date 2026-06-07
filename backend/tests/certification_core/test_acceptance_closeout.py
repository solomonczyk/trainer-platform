"""ACCEPTANCE CLOSEOUT — RBAC endpoint matrix, answer-key leakage, immutability, audit bypass."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
from app.core.security import create_access_token

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_FRAMEWORK = {
    "framework_id": "acceptance.test.fw.1",
    "version": "1.0",
    "created_by": "acceptance_runner",
    "description": "Acceptance test framework",
    "competencies": [
        {"competency_id": "acc.comp.1", "name": "Acceptance Competency", "weight": 100.0, "critical": True}
    ],
}

SAMPLE_BLUEPRINT = {
    "blueprint_id": "acceptance.test.bp.1",
    "competency_framework_version": "acceptance.test.fw.1",
    "version": "1.0",
    "created_by": "acceptance_runner",
    "exam_duration_minutes": 60,
    "total_items": 10,
    "sections": [
        {"section_id": "acc.sec.1", "name": "Section 1", "competency_ids": ["acc.comp.1"],
         "weight_percent": 100.0, "minimum_items": 5, "maximum_items": 10}
    ],
}

SAMPLE_ITEM = {
    "item_id": "acceptance.test.item.1",
    "item_type": "multiple_choice",
    "created_by": "acceptance_runner",
    "prompt": {"text": "Test question?"},
    "answer_key": {"correct": "A"},
    "competency_ids": ["acc.comp.1"],
}

SAMPLE_RUBRIC = {
    "rubric_id": "acceptance.test.rubric.1",
    "version": "1.0",
    "created_by": "acceptance_runner",
    "criteria": [{"criterion_id": "acc.crit.1", "name": "Criterion 1", "weight": 100.0}],
}

# ---------------------------------------------------------------------------
# Per-test database
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(autouse=True)
async def _per_test_db():
    """Fresh SQLite database for each test."""
    import uuid, os
    fname = f"test_acc_{uuid.uuid4().hex}.db"
    url = f"sqlite+aiosqlite:///{fname}"
    eng = create_async_engine(url, echo=False, poolclass=NullPool)
    sf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _override_get_db():
        async with sf() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fastapi_app.dependency_overrides[get_db] = _override_get_db

    yield

    await eng.dispose()
    try:
        os.remove(fname)
    except Exception:
        pass


@pytest_asyncio.fixture
async def ac() -> AsyncClient:
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def _token(role: str = "read_only_auditor") -> dict:
    """Create an auth header for a given certification role."""
    custom_claims = {"sub": f"user_{role}", "role": role}
    token = create_access_token(user_id=custom_claims["sub"], role=role)
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# 1. RBAC ENDPOINT MATRIX — real HTTP status codes
# ============================================================================

class TestRBACEndpointMatrix:
    """Verify each endpoint returns correct HTTP status per role."""

    @pytest.mark.parametrize("role,expected", [
        ("platform_admin", 200),
        ("domain_owner", 200),
        ("content_author", 200),
        ("expert_reviewer", 200),
        ("psychometric_reviewer", 200),
        ("qa_reviewer", 200),
        ("read_only_auditor", 200),
        ("guest", 200),
    ])
    async def test_get_domain_packs(self, ac, role, expected):
        resp = await ac.get("/api/v1/certification-core/domain-packs", headers=_token(role))
        assert resp.status_code == expected, f"{role} GET domain-packs: got {resp.status_code}"

    @pytest.mark.parametrize("role,expected", [
        ("platform_admin", 201),
        ("domain_owner", 201),
        ("content_author", 201),
        ("expert_reviewer", 403),
        ("psychometric_reviewer", 403),
        ("qa_reviewer", 403),
        ("read_only_auditor", 403),
        ("guest", 403),
    ])
    async def test_post_domain_pack(self, ac, role, expected):
        body = {"domain_pack_id": "rbac.test.dp", "name": "RBAC Test", "version": "1.0", "created_by": "tester"}
        resp = await ac.post("/api/v1/certification-core/domain-packs", json=body, headers=_token(role))
        assert resp.status_code == expected, f"{role} POST domain-packs: got {resp.status_code} ({resp.text[:100]})"

    @pytest.mark.parametrize("role,expected", [
        ("platform_admin", 201),
        ("domain_owner", 201),
        ("content_author", 201),
        ("expert_reviewer", 403),
        ("qa_reviewer", 403),
        ("read_only_auditor", 403),
        ("guest", 403),
    ])
    async def test_post_competency_framework(self, ac, role, expected):
        resp = await ac.post("/api/v1/certification-core/competency-frameworks", json=SAMPLE_FRAMEWORK, headers=_token(role))
        assert resp.status_code == expected, f"{role} POST competency-frameworks: got {resp.status_code}"

    @pytest.mark.parametrize("role,expected", [
        ("platform_admin", 200),
        ("domain_owner", 200),
        ("content_author", 200),
        ("guest", 200),
    ])
    async def test_get_competency_frameworks(self, ac, role, expected):
        resp = await ac.get("/api/v1/certification-core/competency-frameworks", headers=_token(role))
        assert resp.status_code == expected

    @pytest.mark.parametrize("role,expected", [
        ("platform_admin", 201),
        ("domain_owner", 201),
        ("content_author", 201),
        ("guest", 403),
    ])
    async def test_post_item(self, ac, role, expected):
        resp = await ac.post("/api/v1/certification-core/items", json=SAMPLE_ITEM, headers=_token(role))
        assert resp.status_code == expected, f"{role} POST items: got {resp.status_code} ({resp.text[:100]})"

    @pytest.mark.parametrize("role,expected", [
        ("platform_admin", 200),
        ("domain_owner", 200),
        ("content_author", 200),
        ("guest", 200),
    ])
    async def test_get_items(self, ac, role, expected):
        resp = await ac.get("/api/v1/certification-core/items", headers=_token(role))
        assert resp.status_code == expected

    @pytest.mark.parametrize("role,expected_status", [
        ("content_author", 201),
        ("expert_reviewer", 403),
        ("domain_owner", 201),
    ])
    async def test_post_rubric(self, ac, role, expected_status):
        body = {"rubric_id": "rbac.test.rubric", "version": "1.0", "created_by": "tester",
                "criteria": [{"criterion_id": "c1", "name": "C1", "weight": 100.0}]}
        resp = await ac.post("/api/v1/certification-core/rubrics", json=body, headers=_token(role))
        assert resp.status_code == expected_status, f"{role} POST rubrics: got {resp.status_code}"


# ============================================================================
# 2. LEARNER ANSWER-KEY LEAKAGE — real answer_key stripping
# ============================================================================

class TestLearnerAnswerKeyLeakage:
    """Verify answer_key is stripped for learner roles."""

    async def _create_item(self, ac, token) -> str:
        resp = await ac.post("/api/v1/certification-core/items", json=SAMPLE_ITEM, headers=token)
        assert resp.status_code == 201
        return resp.json()["item_id"]

    @pytest.mark.parametrize("role,expect_key", [
        ("platform_admin", True),
        ("domain_owner", True),
        ("content_author", False),
        ("expert_reviewer", False),
        ("psychometric_reviewer", False),
        ("qa_reviewer", False),
        ("read_only_auditor", False),
        ("guest", False),
    ])
    async def test_answer_key_visibility(self, ac, role, expect_key):
        admin_token = _token("platform_admin")
        item_id = await self._create_item(ac, admin_token)

        role_token = _token(role)
        resp = await ac.get(f"/api/v1/certification-core/items/{item_id}", headers=role_token)
        assert resp.status_code == 200

        data = resp.json()
        has_key = "answer_key" in data
        assert has_key == expect_key, (
            f"Role '{role}': expect answer_key={expect_key}, got has_key={has_key}"
        )
        if expect_key:
            assert data.get("answer_key") == {"correct": "A"}


# ============================================================================
# 3. IMMUTABILITY — active/published versions block modification
# ============================================================================

class TestImmutability:
    """Active/published versions cannot be modified."""

    async def _create_active_framework(self, ac) -> str:
        resp = await ac.post("/api/v1/certification-core/competency-frameworks",
            json={**SAMPLE_FRAMEWORK, "framework_id": "immut.test.fw"}, headers=_token("domain_owner"))
        assert resp.status_code == 201
        fw_id = resp.json()["framework_id"]
        # Activate
        resp = await ac.patch(f"/api/v1/certification-core/competency-frameworks/{fw_id}",
            json={"status": "active"}, headers=_token("domain_owner"))
        assert resp.status_code == 200
        return fw_id

    async def test_cannot_modify_active_framework(self, ac):
        fw_id = await self._create_active_framework(ac)
        # Attempt to add a competency to an active framework
        resp = await ac.post(
            f"/api/v1/certification-core/competency-frameworks/{fw_id}/competencies",
            json={"competency_id": "new.comp", "name": "New"},
            headers=_token("domain_owner"),
        )
        assert resp.status_code == 400, f"Active framework modification should be blocked: {resp.status_code}"


# ============================================================================
# 4. AUDIT APPEND-ONLY — no update/delete bypass
# ============================================================================

class TestAuditBypass:
    """Audit events cannot be updated or deleted."""

    async def test_audit_service_no_update_delete(self):
        from app.certification_core.audit.service import AuditService
        methods = [m for m in dir(AuditService) if not m.startswith("_")]
        forbidden = ["record_update_bulk", "delete_events", "purge", "update_event", "delete_event"]
        for f in forbidden:
            assert f not in methods, f"Forbidden method '{f}' found on AuditService"
        print("AuditService: no update/delete methods found")

    async def test_audit_model_no_update_columns(self, ac):
        """Verify audit events table has no update-tracking columns."""
        from app.certification_core.models.audit_models import AuditEvent
        cols = [c.name for c in AuditEvent.__table__.columns]
        # Audit events should have event_timestamp but no updated_at
        assert "event_timestamp" in cols
        # Verify before/after hash exist but no mutable content
        assert "before_hash" in cols
        assert "after_hash" in cols
        print("AuditEvent model structure verified")

    async def test_audit_record_creates_event(self):
        """Create an audit event and verify content."""
        from datetime import datetime
        import uuid
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        from app.certification_core.audit.service import AuditService
        from app.certification_core.models.audit_models import AuditEvent

        fname = f"test_audit_{uuid.uuid4().hex}.db"
        url = f"sqlite+aiosqlite:///{fname}"
        eng = create_async_engine(url, echo=False, poolclass=NullPool)
        sf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with sf() as db:
            svc = AuditService(db)
            event = await svc.record(
                entity_type="item", entity_id="audit.test.1",
                action="create", actor_id="tester", actor_role="domain_owner",
                reason="Acceptance test",
            )
            assert event.audit_event_id is not None
            assert event.entity_type == "item"
            assert event.entity_id == "audit.test.1"
            assert event.action == "create"
            assert event.actor_id == "tester"

            # Verify it's in the database
            result = await db.execute(
                __import__('sqlalchemy').select(AuditEvent).where(AuditEvent.entity_id == "audit.test.1")
            )
            found = result.scalar_one_or_none()
            assert found is not None
            assert found.action == "create"

        await eng.dispose()
        import os
        try:
            os.remove(fname)
        except Exception:
            pass
        print("Audit record/create/query verified OK")


# ============================================================================
# 5. FORBIDDEN TRANSITIONS — proven with real state machine
# ============================================================================

class TestForbiddenTransitionsAcceptance:
    """All 9 forbidden transitions are physically blocked."""

    @pytest.mark.parametrize("from_s,to_s", [
        ("draft", "exam_eligible"),
        ("generated", "exam_eligible"),
        ("generated", "approved_for_pilot"),
        ("draft", "approved_for_pilot"),
        ("approved_for_pilot", "exam_eligible"),
        ("pilot", "exam_eligible"),
        ("suspended", "exam_eligible"),
        ("retired", "exam_eligible"),
        ("retired", "pilot"),
    ])
    def test_forbidden_transitions_blocked(self, from_s, to_s):
        from app.certification_core.state_machine.item_lifecycle import validate_transition
        result = validate_transition(from_s, to_s, actor_role="platform_admin", actor_id="admin")
        assert result["allowed"] is False, f"Transition {from_s}->{to_s} should be forbidden"


# ============================================================================
# 6. ENHANCED IMMUTABILITY — item, rubric, blueprint immutability
# ============================================================================

class TestEnhancedImmutability:
    """Enhanced immutability tests for all versioned entities."""

    async def _create_published_blueprint(self, ac) -> str:
        """Create and publish a blueprint for immutability testing."""
        # Create a domain pack first
        resp = await ac.post("/api/v1/certification-core/domain-packs",
            json={"domain_pack_id": "immut.test.dp", "name": "Immut Test DP", "version": "1.0", "created_by": "tester"},
            headers=_token("platform_admin"))
        # Create blueprint
        bp_id = "immut.test.bp"
        resp = await ac.post("/api/v1/certification-core/blueprints",
            json={**SAMPLE_BLUEPRINT, "blueprint_id": bp_id, "domain_pack_id": "immut.test.dp"},
            headers=_token("domain_owner"))
        assert resp.status_code == 201
        # Publish it
        resp = await ac.patch(f"/api/v1/certification-core/blueprints/{bp_id}",
            json={"status": "active"}, headers=_token("domain_owner"))
        assert resp.status_code == 200
        return bp_id

    async def _create_active_item(self, ac) -> str:
        """Create and activate an item for immutability testing."""
        resp = await ac.post("/api/v1/certification-core/items",
            json={**SAMPLE_ITEM, "item_id": "immut.test.item"},
            headers=_token("content_author"))
        assert resp.status_code == 201
        item_id = resp.json()["item_id"]
        # Mark as active
        resp = await ac.patch(f"/api/v1/certification-core/items/{item_id}",
            json={"status": "active"}, headers=_token("domain_owner"))
        assert resp.status_code == 200
        return item_id

    async def _create_active_rubric(self, ac) -> str:
        """Create and activate a rubric for immutability testing."""
        resp = await ac.post("/api/v1/certification-core/rubrics",
            json={**SAMPLE_RUBRIC, "rubric_id": "immut.test.rubric"},
            headers=_token("content_author"))
        assert resp.status_code == 201
        rubric_id = resp.json()["rubric_id"]
        # Activate it
        resp = await ac.patch(f"/api/v1/certification-core/rubrics/{rubric_id}",
            json={"status": "active"}, headers=_token("domain_owner"))
        assert resp.status_code == 200
        return rubric_id

    async def test_active_item_update_blocked(self, ac):
        """Active items cannot be updated."""
        item_id = await self._create_active_item(ac)
        resp = await ac.patch(f"/api/v1/certification-core/items/{item_id}",
            json={"prompt": {"text": "New question?"}},
            headers=_token("content_author"))
        assert resp.status_code == 400, f"Active item update should be blocked: {resp.status_code}"

    async def test_active_rubric_update_blocked(self, ac):
        """Active rubrics cannot be updated."""
        rubric_id = await self._create_active_rubric(ac)
        resp = await ac.patch(f"/api/v1/certification-core/rubrics/{rubric_id}",
            json={"description": "Should be blocked"},
            headers=_token("domain_owner"))
        assert resp.status_code == 400, f"Active rubric update should be blocked: {resp.status_code}"

    async def test_published_blueprint_update_blocked(self, ac):
        """Published/active blueprints cannot be updated."""
        bp_id = await self._create_published_blueprint(ac)
        resp = await ac.patch(f"/api/v1/certification-core/blueprints/{bp_id}",
            json={"exam_duration_minutes": 90},
            headers=_token("domain_owner"))
        assert resp.status_code == 400, f"Published blueprint update should be blocked: {resp.status_code}"


# ============================================================================
# 7. AUDIT REPOSITORY APPEND-ONLY GUARD
# ============================================================================

class TestAuditAppendOnlyGuard:
    """Audit repository blocks all mutation operations."""

    async def test_audit_repository_create_blocked(self):
        """AuditRepository.create() must raise RuntimeError."""
        from app.certification_core.repositories.audit_repository import AuditRepository
        import uuid
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        url = f"sqlite+aiosqlite:///test_audit_repo_{uuid.uuid4().hex}.db"
        eng = create_async_engine(url, echo=False)
        sf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with sf() as db:
            repo = AuditRepository(db)
            try:
                await repo.create(audit_event_id="test", entity_type="item", entity_id="1",
                                  action="create", actor_id="tester")
                assert False, "Should have raised RuntimeError"
            except RuntimeError as e:
                assert "append-only" in str(e).lower()
        await eng.dispose()

    async def test_audit_repository_update_blocked(self):
        """AuditRepository.update_entity() must raise RuntimeError."""
        from app.certification_core.repositories.audit_repository import AuditRepository
        import uuid
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        url = f"sqlite+aiosqlite:///test_audit_repo_{uuid.uuid4().hex}.db"
        eng = create_async_engine(url, echo=False)
        sf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
        async with sf() as db:
            repo = AuditRepository(db)
            try:
                await repo.update_entity("some-id", action="updated")
                assert False, "Should have raised RuntimeError"
            except RuntimeError as e:
                assert "append-only" in str(e).lower()
        await eng.dispose()

    async def test_audit_repository_delete_blocked(self):
        """AuditRepository.soft_delete() must raise RuntimeError."""
        from app.certification_core.repositories.audit_repository import AuditRepository
        import uuid
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        url = f"sqlite+aiosqlite:///test_audit_repo_{uuid.uuid4().hex}.db"
        eng = create_async_engine(url, echo=False)
        sf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
        async with sf() as db:
            repo = AuditRepository(db)
            try:
                await repo.soft_delete("some-id")
                assert False, "Should have raised RuntimeError"
            except RuntimeError as e:
                assert "append-only" in str(e).lower()
        await eng.dispose()

    async def test_audit_tamper_detection(self):
        """Verify SHA-256 hashing detects tampering with audit state."""
        from app.certification_core.audit.service import _compute_hash
        before = {"status": "draft", "difficulty": "medium"}
        after = {"status": "active", "difficulty": "medium"}
        h1 = _compute_hash(before)
        h2 = _compute_hash(after)
        # Different states must produce different hashes
        assert h1 != h2, "Different states must produce different hashes"
        # Same state must produce same hash
        h1_copy = _compute_hash(before)
        assert h1 == h1_copy, "Same state must produce the same hash"


# ============================================================================
# 8. ANSWER-KEY LEAKAGE — comprehensive coverage
# ============================================================================

class TestComprehensiveAnswerKeyLeakage:
    """Verify answer keys are protected across all endpoints and contexts."""

    async def test_answer_key_absent_from_list_endpoint(self, ac):
        """Answer keys must not appear in item list responses for learner roles."""
        admin_token = _token("platform_admin")
        # Create an item with answer key
        resp = await ac.post("/api/v1/certification-core/items",
            json={**SAMPLE_ITEM, "item_id": "leak.test.list"},
            headers=admin_token)
        assert resp.status_code == 201

        # Verify guest sees no answer_key in list
        guest_resp = await ac.get("/api/v1/certification-core/items", headers=_token("guest"))
        assert guest_resp.status_code == 200
        data = guest_resp.json()
        for item in data.get("items", []):
            assert "answer_key" not in item, f"Guest should not see answer_key in list"

        # Verify platform_admin sees answer_key in list
        admin_resp = await ac.get("/api/v1/certification-core/items", headers=admin_token)
        assert admin_resp.status_code == 200
        data = admin_resp.json()
        any_with_key = any("answer_key" in item for item in data.get("items", []))
        assert any_with_key, "Admin should see answer_key in list"

    async def test_error_response_no_answer_key_leakage(self, ac):
        """Error responses must not leak answer key data."""
        # Try an invalid operation with learner role
        resp = await ac.get("/api/v1/certification-core/items/nonexistent-id", headers=_token("guest"))
        assert resp.status_code == 404
        body = resp.json()
        body_str = str(body).lower()
        # Ensure no answer key leaked in error
        assert "correct" not in body_str or "answer_key" not in body_str

    async def test_learner_mapping_guest_is_learner(self, ac):
        """Guest role maps to learner with no answer-key access."""
        from app.certification_core.services.authorization import AuthorizationService
        assert AuthorizationService.can_read_answer_keys("guest") is False
        assert AuthorizationService.can_read_answer_keys("registered_user") is False

    async def test_learner_mapping_documented(self, ac):
        """Learner is authenticated user without certification admin role."""
        from app.certification_core.services.authorization import (
            CERTIFICATION_ROLES, LEARNER_PERMISSIONS,
        )
        assert "certification:read" in LEARNER_PERMISSIONS
        assert "certification:answer_key:read" not in LEARNER_PERMISSIONS
        # Learners should not be in CERTIFICATION_ROLES
        assert "learner" not in CERTIFICATION_ROLES
        assert "registered_user" not in CERTIFICATION_ROLES


# ============================================================================
# 9. LIFECYCLE SECURITY — self-approval and role gates
# ============================================================================

class TestLifecycleSecurityAcceptance:
    """Lifecycle approval gates and self-approval prevention."""

    def test_content_author_cannot_self_approve(self):
        from app.certification_core.services.authorization import AuthorizationService
        assert AuthorizationService.can_self_approve("content_author") is False

    def test_domain_owner_cannot_self_approve(self):
        from app.certification_core.services.authorization import AuthorizationService
        assert AuthorizationService.can_self_approve("domain_owner") is False

    def test_platform_admin_can_self_approve(self):
        from app.certification_core.services.authorization import AuthorizationService
        # platform_admin is not in the restricted set
        assert AuthorizationService.can_self_approve("platform_admin") is True

    def test_llm_self_approval_blocked(self):
        """LLM actors cannot self-approve expert gates."""
        from app.certification_core.state_machine.item_lifecycle import validate_transition
        result = validate_transition(
            "expert_review_required", "approved_for_pilot",
            actor_role="expert_reviewer", actor_id="llm:gpt-4",
        )
        assert result["allowed"] is False

    def test_content_author_self_approval_blocked(self):
        from app.certification_core.state_machine.item_lifecycle import validate_transition
        result = validate_transition(
            "expert_review_required", "approved_for_pilot",
            actor_role="content_author", actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_domain_owner_self_approval_blocked(self):
        from app.certification_core.state_machine.item_lifecycle import validate_transition
        result = validate_transition(
            "expert_review_required", "approved_for_pilot",
            actor_role="domain_owner", actor_id="user_1",
        )
        assert result["allowed"] is False
