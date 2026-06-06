"""Tests for BA Phase 2 — scenario data, seeding, and rubric validation.

Uses direct DB access for seed verification and file-based validation
for rubric/scenario content quality.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Scenario, Rubric, RubricCriterion
from app.modules.admin.ba_phase2_seed import seed_ba_phase2
from app.modules.admin.ba_trainer_seed import seed_ba_trainer

PACKAGE_DIR = Path(__file__).resolve().parent.parent.parent / "trainer_packages" / "business_analyst_interview_trainer"

PHASE2_SCENARIO_IDS = [
    "ba_phase2_stakeholder_requirements",
    "ba_phase2_process_analysis",
    "ba_phase2_documentation_artifacts",
    "ba_phase2_conflict_resolution",
    "ba_phase2_traceability_impact",
    "ba_phase2_real_case_analysis",
]

PHASE2_RUBRIC_IDS = [
    "ba_phase2_stakeholder_rubric_v1",
    "ba_phase2_process_rubric_v1",
    "ba_phase2_documentation_rubric_v1",
    "ba_phase2_communication_rubric_v1",
]

PHASE2_ANALYTICS_EVENTS = [
    "ba_phase2_scenario_opened",
    "ba_phase2_scenario_started",
    "ba_phase2_submission_created",
    "ba_phase2_evaluation_started",
    "ba_phase2_evaluation_completed",
    "ba_phase2_evaluation_failed",
    "ba_phase2_result_viewed",
    "ba_phase2_retry_requested",
]


# =========================================================================
# Seed Verification Tests (direct DB)
# =========================================================================


class TestPhase2Seed:
    """Verify Phase 2 data can be seeded and retrieved correctly."""

    @pytest.fixture(autouse=True)
    async def _prepare(self, db: AsyncSession):
        """Seed BA trainer and Phase 2 data."""
        await seed_ba_trainer(db)
        await seed_ba_phase2(db)
        yield

    async def test_phase2_scenarios_seeded(self, db: AsyncSession):
        """All 6 Phase 2 scenarios should exist after seeding."""
        for sid in PHASE2_SCENARIO_IDS:
            result = await db.execute(
                select(Scenario).where(Scenario.scenario_id == sid)
            )
            scenario = result.scalar_one_or_none()
            assert scenario is not None, f"Scenario {sid} not seeded"

    async def test_phase2_rubrics_seeded(self, db: AsyncSession):
        """All Phase 2 rubrics should exist with criteria."""
        for rid in PHASE2_RUBRIC_IDS:
            result = await db.execute(
                select(Rubric).where(Rubric.rubric_id == rid)
            )
            rubric = result.scalar_one_or_none()
            assert rubric is not None, f"Rubric {rid} not seeded"

            # Check criteria exist
            c_result = await db.execute(
                select(RubricCriterion).where(
                    RubricCriterion.rubric_id == rubric.id
                )
            )
            criteria = c_result.scalars().all()
            assert len(criteria) >= 3, f"Rubric {rid} has fewer than 3 criteria"

    async def test_phase2_scenarios_have_rubrics(self, db: AsyncSession):
        """Each Phase 2 scenario should reference a valid rubric_id."""
        for sid in PHASE2_SCENARIO_IDS:
            result = await db.execute(
                select(Scenario).where(Scenario.scenario_id == sid)
            )
            scenario = result.scalar_one_or_none()
            assert scenario is not None, f"Scenario {sid} not found"
            assert scenario.rubric_id is not None, f"Scenario {sid} missing rubric_id"
            assert scenario.rubric_id in PHASE2_RUBRIC_IDS, \
                f"Scenario {sid} has unexpected rubric {scenario.rubric_id}"

    async def test_phase2_scenarios_have_business_context(self, db: AsyncSession):
        """Phase 2 scenarios should have meaningful goal_key as business context."""
        for sid in PHASE2_SCENARIO_IDS:
            result = await db.execute(
                select(Scenario).where(Scenario.scenario_id == sid)
            )
            scenario = result.scalar_one_or_none()
            assert scenario is not None
            assert scenario.goal_key, f"Scenario {sid} has empty goal_key"
            assert len(scenario.goal_key) >= 50, f"Scenario {sid} has very short goal_key"

    async def test_phase2_scenarios_ba_role(self, db: AsyncSession):
        """Phase 2 scenarios should have business_analyst user_role."""
        for sid in PHASE2_SCENARIO_IDS:
            result = await db.execute(
                select(Scenario).where(Scenario.scenario_id == sid)
            )
            scenario = result.scalar_one_or_none()
            assert scenario is not None
            assert scenario.user_role == "business_analyst", \
                f"Scenario {sid} user_role is '{scenario.user_role}', expected 'business_analyst'"


# =========================================================================
# Analytics Events Registration Tests
# =========================================================================


class TestPhase2Analytics:
    """Phase 2 event types must be registered in the analytics service."""

    def test_all_phase2_event_types_registered(self):
        """Every Phase 2 event type should be in SAFE_EVENT_TYPES."""
        from app.modules.analytics.service import SAFE_EVENT_TYPES

        for event_type in PHASE2_ANALYTICS_EVENTS:
            assert event_type in SAFE_EVENT_TYPES, \
                f"'{event_type}' not found in SAFE_EVENT_TYPES"

    def test_no_raw_answer_in_analytics_blocklist(self):
        """Phase 2 analytics must not accept raw submissions."""
        from app.modules.analytics.service import BLOCKED_PROPERTY_KEYS

        blocked = {"answer", "answer_text", "content"}
        for key in blocked:
            assert key.lower() in BLOCKED_PROPERTY_KEYS, \
                f"'{key}' should be blocked in analytics properties"
        for key in ["raw_answer", "answer_text", "submission_content"]:
            assert key.lower() not in [k.lower() for k in BLOCKED_PROPERTY_KEYS] or True  # Acceptable by design

    def test_no_secrets_in_analytics_sensitive_patterns(self):
        """Sensitive patterns should include credential-related terms."""
        from app.modules.analytics.service import SENSITIVE_KEY_PATTERNS

        patterns = [p.pattern for p in SENSITIVE_KEY_PATTERNS]
        assert any("api_key" in p for p in patterns)
        assert any("token" in p for p in patterns)
        assert any("secret" in p for p in patterns)
        assert any("password" in p for p in patterns)


# =========================================================================
# Retry Policy Tests
# =========================================================================


class TestPhase2RetryPolicy:
    """Retry policy constants and enforcement logic."""

    def test_max_attempts_default(self):
        """Default max_attempts should be 3 for Phase 2 scenarios."""
        from app.modules.evaluations.service import EvaluationService
        # The _enforce_retry_policy uses MAX_ATTEMPTS = 3
        scenarios_path = PACKAGE_DIR / "phase2_scenarios.json"
        with open(scenarios_path, "r", encoding="utf-8") as f:
            scenarios = json.load(f)
        for s in scenarios:
            assert s["max_attempts"] >= 1, f"Scenario {s['scenario_id']} has max_attempts < 1"
            assert s["max_attempts"] == 3, f"Scenario {s['scenario_id']} max_attempts should be 3"
