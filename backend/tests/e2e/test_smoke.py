#!/usr/bin/env python3
"""E2E smoke test — simulates the full user journey."""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.models import (
    User, UserProfile, Domain, TrainerProduct, Scenario, Rubric, RubricCriterion,
    SkillMap, Skill, CriticalError, FeatureFlag,
)
from app.core.security import hash_password


import uuid
TEST_DB_FILE = f"test_e2e_{uuid.uuid4().hex}.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_full_user_journey():
    """
    E2E Smoke Test — Full User Journey

    Tests the complete flow: health → register → login → domains → trainer → enroll → scenarios → start → submit → complete → evaluate → result → progress
    """
    # Setup: create tables and seed data
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as db:
        # Seed domain
        domain = Domain(slug="it", name="IT", description="IT Domain", is_active=True, sort_order=0)
        db.add(domain)
        await db.flush()

        # Seed trainer
        trainer = TrainerProduct(
            trainer_product_id="qa_engineer_interview_trainer",
            domain_id=domain.id,
            slug="qa-engineer-interview-trainer",
            name="QA Engineer Interview Trainer",
            product_type="interview_simulator",
            default_locale="ru-RU",
            supported_locales=["ru-RU", "en-US"],
            status="published_seed",
            is_published=True,
        )
        db.add(trainer)
        await db.flush()

        # Seed rubric
        rubric = Rubric(
            rubric_id="qa_bug_report_rubric_v1",
            pass_score=70,
            critical_fail_enabled=True,
        )
        db.add(rubric)
        await db.flush()
        for crit in [
            {"criterion_id": "structure", "name": "Structure", "weight": 25},
            {"criterion_id": "technical_accuracy", "name": "Technical Accuracy", "weight": 30},
            {"criterion_id": "completeness", "name": "Completeness", "weight": 25},
            {"criterion_id": "clarity", "name": "Clarity", "weight": 20},
        ]:
            db.add(RubricCriterion(rubric_id=rubric.id, **crit))

        # Seed scenario
        scenario = Scenario(
            scenario_id="qa_bug_report_structure_v1",
            trainer_product_id=trainer.id,
            title_key="scenario.qa_bug_report.title",
            goal_key="scenario.qa_bug_report.goal",
            difficulty="junior_basic",
            estimated_duration_minutes=8,
            target_skills=["bug_reporting", "technical_accuracy"],
            user_role="candidate",
            ai_role="interviewer",
            rubric_id="qa_bug_report_rubric_v1",
            steps=[{"step_id": "step_1", "order": 1, "prompt_key": "scenario.qa_bug_report.step_1.prompt"}],
            critical_errors=["qa_crit_steps_not_needed"],
            hints=["hint.qa_bug_report.direction"],
            status="published_seed",
        )
        db.add(scenario)
        await db.commit()

    transport = ASGITransport(app=app)
    journey = []

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Health
        r = await client.get("/health")
        assert r.status_code == 200, f"Health check failed: {r.text}"
        journey.append("1.health:ok")

        # Step 2: Register
        r = await client.post(
            "/api/v1/auth/register",
            json={"email": "e2e@test.com", "password": "e2etest123", "display_name": "E2E User"},
        )
        assert r.status_code in (200, 201), f"Register failed: {r.text}"
        token_data = r.json()
        token = token_data["access_token"]
        user_id = token_data["user"]["id"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        journey.append("2.register:ok")

        # Step 3: Login
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "e2e@test.com", "password": "e2etest123"},
        )
        assert r.status_code == 200, f"Login failed: {r.text}"
        journey.append("3.login:ok")

        # Step 4: Current user
        r = await client.get("/api/v1/me", headers=auth_headers)
        assert r.status_code == 200, f"Current user failed: {r.text}"
        assert r.json()["email"] == "e2e@test.com"
        journey.append("4.me:ok")

        # Step 5: List domains
        r = await client.get("/api/v1/domains")
        assert r.status_code == 200
        domains = r.json()
        assert len(domains) >= 1
        journey.append("5.domains:ok")

        # Step 6: Get domain
        r = await client.get("/api/v1/domains/it")
        assert r.status_code == 200
        journey.append("6.domain:ok")

        # Step 7: Get trainer
        r = await client.get("/api/v1/trainers/qa-engineer-interview-trainer", headers=auth_headers)
        assert r.status_code == 200, f"Get trainer failed: {r.text}"
        trainer_data = r.json()
        assert trainer_data["slug"] == "qa-engineer-interview-trainer"
        journey.append("7.trainer:ok")

        # Step 8: Enroll
        r = await client.post(
            "/api/v1/trainers/qa-engineer-interview-trainer/enroll",
            headers=auth_headers,
        )
        assert r.status_code in (200, 201), f"Enroll failed: {r.text}"
        journey.append("8.enroll:ok")

        # Step 9: List scenarios
        r = await client.get(
            "/api/v1/trainers/qa-engineer-interview-trainer/scenarios",
            headers=auth_headers,
        )
        assert r.status_code == 200
        scenarios = r.json()
        assert len(scenarios) >= 1
        journey.append("9.scenarios:ok")

        # Step 10: Start scenario
        r = await client.post(
            "/api/v1/scenarios/qa_bug_report_structure_v1/start",
            headers=auth_headers,
        )
        assert r.status_code == 200, f"Start scenario failed: {r.text}"
        start_data = r.json()
        session_id = start_data["session_id"]
        attempt_id = start_data["attempt_id"]
        journey.append("10.start:ok")

        # Step 11: Submit answer
        r = await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "I would structure a bug report with: title, steps to reproduce, actual result, expected result, environment details (OS, browser version), severity, priority, and attachments like screenshots or logs."},
            headers=auth_headers,
        )
        assert r.status_code == 200, f"Submit failed: {r.text}"
        journey.append("11.submit:ok")

        # Step 12: Complete session
        r = await client.post(
            f"/api/v1/sessions/{session_id}/complete",
            headers=auth_headers,
        )
        assert r.status_code == 200, f"Complete failed: {r.text}"
        journey.append("12.complete:ok")

        # Step 13: Evaluate attempt and get full evaluation result
        r = await client.post(
            f"/api/v1/attempts/{attempt_id}/evaluate",
            headers=auth_headers,
        )
        assert r.status_code == 200, f"Evaluate failed: {r.text}"
        eval_data = r.json()
        assert "overall_score" in eval_data
        assert "passed" in eval_data
        assert "criteria" in eval_data
        assert 0 <= eval_data["overall_score"] <= 100
        journey.append(f"13.evaluate:ok(score={eval_data['overall_score']})")

        # Step 14: Get evaluation
        r = await client.get(
            f"/api/v1/attempts/{attempt_id}/evaluation",
            headers=auth_headers,
        )
        assert r.status_code == 200
        eval_get = r.json()
        assert eval_get["overall_score"] == eval_data["overall_score"]
        journey.append("14.evaluation:ok")

        # Step 15: Check progress
        r = await client.get("/api/v1/me/progress", headers=auth_headers)
        assert r.status_code == 200
        progress_data = r.json()
        assert "progress_list" in progress_data
        journey.append("15.progress:ok")

        # Step 16: Trainer-specific progress
        r = await client.get(
            "/api/v1/me/progress/qa-engineer-interview-trainer",
            headers=auth_headers,
        )
        assert r.status_code == 200
        journey.append("16.trainer_progress:ok")

        # Step 17: Analytics event
        r = await client.post(
            "/api/v1/analytics/events",
            json={
                "event_type": "evaluation_result_viewed",
                "trainer_slug": "qa-engineer-interview-trainer",
                "scenario_id": "qa_bug_report_structure_v1",
                "properties": {"score": eval_data["overall_score"]},
            },
            headers=auth_headers,
        )
        assert r.status_code == 200
        journey.append("17.analytics:ok")

        # Step 18: Profile update
        r = await client.patch(
            "/api/v1/me",
            json={"preferred_locale": "en-US"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["preferred_locale"] == "en-US"
        journey.append("18.profile:ok")

        # Cleanup
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        # Cleanup
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()
        try:
            import os
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    print(f"\n{'='*60}")
    print(f"✅ E2E SMOKE TEST PASSED")
    print(f"{'='*60}")
    for step in journey:
        print(f"  {step}")
    print(f"{'='*60}")
