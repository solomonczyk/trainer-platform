"""Focused tests for scenario-to-quest mapping (Layer 010a)."""

from __future__ import annotations

import pytest

from app.modules.scenarios.scenario_quest_mapping import (
    SCENARIO_QUEST_MAPPING,
    get_scenario_mapping,
    get_quest_id_for_scenario,
    is_scenario_hidden,
    is_scenario_converted,
    get_trainer_slug_for_scenario,
)
from app.modules.quests.quest_data import QUEST_REGISTRY


class TestScenarioMappingInventory:
    """Verify every scenario has an explicit mapping decision."""

    def test_all_qa_scenarios_mapped(self):
        """All known QA legacy scenarios must have a mapping entry."""
        qa_scenarios = [
            "qa_bug_report_structure_v1",
            "qa_test_case_vs_checklist_v1",
            "qa_login_form_testing_v1",
            "qa_regression_vs_retest_v1",
            "qa_self_presentation_v1",
        ]
        for sid in qa_scenarios:
            mapping = get_scenario_mapping(sid)
            assert mapping is not None, f"QA scenario {sid} has no mapping"
            assert mapping["mode"] in ("CONVERTED", "REDIRECTED", "HIDE_TEMPORARILY", "KEEP_INTERNAL"), \
                f"QA scenario {sid} has invalid mode"

    def test_all_ba_scenarios_mapped(self):
        """All known BA legacy Phase 2 scenarios must have a mapping entry."""
        ba_scenarios = [
            "ba_phase2_stakeholder_requirements",
            "ba_phase2_process_analysis",
            "ba_phase2_documentation_artifacts",
            "ba_phase2_conflict_resolution",
            "ba_phase2_traceability_impact",
            "ba_phase2_real_case_analysis",
        ]
        for sid in ba_scenarios:
            mapping = get_scenario_mapping(sid)
            assert mapping is not None, f"BA scenario {sid} has no mapping"
            assert mapping["mode"] in ("CONVERTED", "REDIRECTED", "HIDE_TEMPORARILY", "KEEP_INTERNAL"), \
                f"BA scenario {sid} has invalid mode"

    def test_no_unmapped_scenarios(self):
        """All entries in the inventory are accounted for."""
        # All keys must have valid mappings
        for sid, mapping in SCENARIO_QUEST_MAPPING.items():
            assert "quest_id" in mapping or mapping.get("quest_id") is None
            assert "mode" in mapping
            assert "trainer_slug" in mapping


class TestMappingQuestExistence:
    """Verify mapped quests actually exist in the registry."""

    def test_converted_quest_exists(self):
        """Scenarios marked CONVERTED must have a quest in the registry with matching ID."""
        for sid, mapping in SCENARIO_QUEST_MAPPING.items():
            if mapping["mode"] == "CONVERTED":
                qid = mapping.get("quest_id")
                assert qid is not None, f"CONVERTED scenario {sid} has no quest_id"
                assert qid in QUEST_REGISTRY, f"Quest {qid} not found in registry for {sid}"

    def test_redirected_quest_exists(self):
        """Scenarios marked REDIRECTED must have an existing target quest."""
        for sid, mapping in SCENARIO_QUEST_MAPPING.items():
            if mapping["mode"] == "REDIRECTED":
                qid = mapping.get("quest_id")
                assert qid is not None, f"REDIRECTED scenario {sid} has no quest_id"
                assert qid in QUEST_REGISTRY, f"Target quest {qid} not found for {sid}"

    def test_hidden_scenarios_no_quest_id(self):
        """HIDE_TEMPORARILY scenarios should have quest_id=None."""
        for sid, mapping in SCENARIO_QUEST_MAPPING.items():
            if mapping["mode"] == "HIDE_TEMPORARILY":
                assert mapping.get("quest_id") is None, \
                    f"HIDDEN scenario {sid} should not have a quest_id"


class TestMappingTrainerConsistency:
    """Verify trainer_slug consistency between mapping and quest."""

    def test_mapped_quest_trainer_slug_matches(self):
        """The trainer_slug in the mapping should match the quest's trainer_slug."""
        for sid, mapping in SCENARIO_QUEST_MAPPING.items():
            qid = mapping.get("quest_id")
            if qid and qid in QUEST_REGISTRY:
                quest = QUEST_REGISTRY[qid]
                mapping_trainer = mapping.get("trainer_slug")
                assert mapping_trainer == quest.trainer_slug, \
                    f"Trainer slug mismatch for {sid}: mapping={mapping_trainer}, quest={quest.trainer_slug}"


class TestMappingHelpers:
    """Test the helper functions."""

    def test_get_quest_id_for_scenario(self):
        assert get_quest_id_for_scenario("qa_bug_report_structure_v1") == "qa_bug_report_structure_v1"
        assert get_quest_id_for_scenario("qa_regression_vs_retest_v1") is None  # hidden

    def test_is_scenario_hidden(self):
        assert is_scenario_hidden("qa_regression_vs_retest_v1") is True
        assert is_scenario_hidden("qa_self_presentation_v1") is True
        assert is_scenario_hidden("qa_bug_report_structure_v1") is False
        assert is_scenario_hidden("qa_test_case_vs_checklist_v1") is False

    def test_is_scenario_converted(self):
        assert is_scenario_converted("qa_bug_report_structure_v1") is True
        assert is_scenario_converted("qa_test_case_vs_checklist_v1") is False

    def test_get_trainer_slug_for_scenario(self):
        assert get_trainer_slug_for_scenario("qa_bug_report_structure_v1") == "qa_engineer_interview_trainer"
        assert get_trainer_slug_for_scenario("ba_phase2_stakeholder_requirements") == "business_analyst_interview_trainer"

    def test_no_circular_redirects(self):
        """No REDIRECTED scenario can redirect to itself (CONVERTED is exempt)."""
        for sid, mapping in SCENARIO_QUEST_MAPPING.items():
            if mapping["mode"] != "CONVERTED":
                qid = mapping.get("quest_id")
                if qid:
                    assert qid != sid, f"Circular redirect: {sid} -> {qid}"


class TestBugReportQuestSchema:
    """Focus on the converted bug-report quest."""

    def test_bug_report_quest_exists(self):
        assert "qa_bug_report_structure_v1" in QUEST_REGISTRY

    def test_bug_report_quest_steps(self):
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        assert len(quest.steps) >= 5  # At least 5 steps

    def test_bug_report_interaction_types(self):
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        types = {s.step_type for s in quest.steps}
        assert "multiple_choice" in types
        assert "ordering" in types
        assert "single_choice" in types
        assert "evidence_select" in types
        assert "free_text" in types
        assert len(types) >= 4  # At least 4 interaction types

    def test_bug_report_free_text_only_for_artifact(self):
        """Only the last interactive step should be free_text."""
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        free_text_steps = [s for s in quest.steps if s.step_type == "free_text"]
        assert len(free_text_steps) == 1

    def test_bug_report_deterministic_steps_no_provider(self):
        """Non-free-text steps should be deterministic."""
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        for step in quest.steps:
            if step.step_type != "free_text":
                assert step.evaluation_mode == "deterministic", \
                    f"Step {step.step_id} should be deterministic"

    def test_bug_report_has_debrief(self):
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        assert quest.debrief_contract is not None
        assert len(quest.debrief_contract.sections) > 0

    def test_bug_report_has_outcomes(self):
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        assert len(quest.outcomes) >= 2

    def test_bug_report_has_characters(self):
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        assert len(quest.characters) > 0

    def test_bug_report_learning_objectives(self):
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        for step in quest.steps:
            assert len(step.learning_objectives) > 0, f"Step {step.step_id} has no learning objectives"

    def test_bug_report_skill_bindings(self):
        quest = QUEST_REGISTRY["qa_bug_report_structure_v1"]
        for step in quest.steps:
            assert len(step.skill_bindings) > 0, f"Step {step.step_id} has no skill bindings"
