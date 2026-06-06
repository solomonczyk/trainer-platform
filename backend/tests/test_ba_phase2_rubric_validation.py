"""Phase 2 rubric validation and AI evaluation schema tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

PACKAGE_DIR = Path(__file__).resolve().parent.parent.parent / "trainer_packages" / "business_analyst_interview_trainer"


class TestPhase2RubricValidation:
    """Validate all Phase 2 rubrics for structural correctness."""

    @pytest.fixture(scope="class")
    def rubrics_data(self):
        path = PACKAGE_DIR / "phase2_rubrics.json"
        assert path.exists(), f"Rubric file not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_rubric_pack_has_id(self, rubrics_data):
        assert "rubric_pack_id" in rubrics_data
        assert rubrics_data["rubric_pack_id"] == "ba_phase2_rubric_pack_v1"

    def test_all_rubrics_have_required_fields(self, rubrics_data):
        for rubric in rubrics_data.get("rubrics", []):
            assert "rubric_id" in rubric, "Rubric missing rubric_id"
            assert rubric["rubric_id"].startswith("ba_phase2_"), \
                f"Rubric ID {rubric['rubric_id']} should start with ba_phase2_"
            assert "pass_score" in rubric
            assert rubric["pass_score"] >= 0 and rubric["pass_score"] <= 100
            assert "criteria" in rubric
            assert len(rubric["criteria"]) >= 3, \
                f"Rubric {rubric['rubric_id']} has fewer than 3 criteria"

    def test_criteria_have_valid_structure(self, rubrics_data):
        for rubric in rubrics_data.get("rubrics", []):
            total_weight = 0
            for criterion in rubric["criteria"]:
                assert "criterion_id" in criterion
                assert "name" in criterion
                assert "description" in criterion
                assert "weight" in criterion
                assert criterion["weight"] > 0
                total_weight += criterion["weight"]
                assert "levels" in criterion
                assert len(criterion["levels"]) == 5, \
                    f"Criterion {criterion['criterion_id']} should have exactly 5 levels"
                for level in criterion["levels"]:
                    assert "score" in level
                    assert "label" in level
                    assert level["score"] in (0, 25, 50, 75, 100), \
                        f"Level score {level['score']} not in valid range"
            # Weights should sum to 100
            assert total_weight == 100, \
                f"Rubric {rubric['rubric_id']} weights sum to {total_weight}, expected 100"

    def test_all_scenarios_have_rubrics(self):
        """Every Phase 2 scenario should reference an existing rubric."""
        scenarios_path = PACKAGE_DIR / "phase2_scenarios.json"
        assert scenarios_path.exists()
        with open(scenarios_path, "r", encoding="utf-8") as f:
            scenarios = json.load(f)

        rubrics_path = PACKAGE_DIR / "phase2_rubrics.json"
        with open(rubrics_path, "r", encoding="utf-8") as f:
            rubrics_data = json.load(f)

        rubric_ids = {r["rubric_id"] for r in rubrics_data.get("rubrics", [])}
        for scenario in scenarios:
            assert "rubric_id" in scenario, \
                f"Scenario {scenario.get('scenario_id')} missing rubric_id"
            assert scenario["rubric_id"] in rubric_ids, \
                f"Scenario {scenario['scenario_id']} references unknown rubric {scenario['rubric_id']}"

    def test_all_scenarios_have_required_fields(self):
        """Every Phase 2 scenario should have the required fields."""
        scenarios_path = PACKAGE_DIR / "phase2_scenarios.json"
        assert scenarios_path.exists()
        with open(scenarios_path, "r", encoding="utf-8") as f:
            scenarios = json.load(f)

        required_fields = [
            "scenario_id", "module_id", "title_key", "locale",
            "business_context", "learner_role", "task",
            "deliverable_type", "constraints", "rubric_id",
            "max_score", "passing_score", "max_attempts", "estimated_minutes",
        ]

        for scenario in scenarios:
            for field in required_fields:
                assert field in scenario, \
                    f"Scenario {scenario.get('scenario_id', 'unknown')} missing field: {field}"
            assert scenario["learner_role"] == "business_analyst"
            assert scenario["passing_score"] >= 50
            assert scenario["max_attempts"] >= 1
            assert scenario["max_score"] == 100


class TestPhase2ScenarioContent:
    """Validate Phase 2 scenario content quality."""

    @pytest.fixture(scope="class")
    def scenarios(self):
        path = PACKAGE_DIR / "phase2_scenarios.json"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_six_scenarios(self, scenarios):
        assert len(scenarios) == 6, f"Expected 6 scenarios, got {len(scenarios)}"

    def test_all_scenarios_have_different_ids(self, scenarios):
        ids = [s["scenario_id"] for s in scenarios]
        assert len(ids) == len(set(ids)), "Duplicate scenario IDs found"

    def test_all_scenarios_have_business_context(self, scenarios):
        for s in scenarios:
            assert len(s["business_context"]) >= 50, \
                f"Scenario {s['scenario_id']} has very short business context"
            assert len(s["task"]) >= 100, \
                f"Scenario {s['scenario_id']} has very short task"

    def test_all_scenarios_have_constraints(self, scenarios):
        for s in scenarios:
            assert len(s["constraints"]) >= 3, \
                f"Scenario {s['scenario_id']} has fewer than 3 constraints"

    def test_all_scenarios_have_reference_requirements(self, scenarios):
        for s in scenarios:
            assert len(s["reference_requirements"]) >= 3, \
                f"Scenario {s['scenario_id']} has fewer than 3 reference requirements"

    def test_all_scenarios_have_different_deliverable_types(self, scenarios):
        """Each scenario should have a meaningful deliverable type."""
        valid_types = {
            "stakeholder_analysis", "process_analysis",
            "requirements_specification", "conflict_analysis",
            "impact_analysis", "solution_architecture",
        }
        for s in scenarios:
            assert s["deliverable_type"] in valid_types, \
                f"Scenario {s['scenario_id']} has unknown deliverable_type: {s['deliverable_type']}"
