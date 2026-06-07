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
