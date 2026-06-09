"""Canonical mapping from legacy scenario IDs to immersive quest IDs.

This mapping governs how the platform handles legacy scenario routes:
- CONVERTED: The scenario has been converted into a quest with the same ID.
  The old route renders the quest engine instead of the textarea-only UI.
- REDIRECTED: The scenario maps semantically to an existing quest.
  The old route redirects to the target quest.
- HIDE_TEMPORARILY: No suitable quest exists yet. The scenario is excluded
  from normal user navigation but remains in the repository.
- KEEP_INTERNAL: Accessible only for admin/testing/internal purposes.
"""

from __future__ import annotations

from typing import Literal

MappingMode = Literal["CONVERTED", "REDIRECTED", "HIDE_TEMPORARILY", "KEEP_INTERNAL"]

ScenarioQuestMapping = dict[
    str,
    {
        "quest_id": str,
        "mode": MappingMode,
        "trainer_slug": str,
    },
]

# ---------------------------------------------------------------------------
# QA Legacy Scenarios
# ---------------------------------------------------------------------------

QA_SCENARIO_MAPPING: dict[str, dict] = {
    "qa_bug_report_structure_v1": {
        "quest_id": "qa_bug_report_structure_v1",
        "mode": "CONVERTED",
        "trainer_slug": "qa_engineer_interview_trainer",
        "reason": "Converted to mini-quest with 5 interaction types + debrief",
    },
    "qa_test_case_vs_checklist_v1": {
        "quest_id": "qa_payment_defect_release",
        "mode": "REDIRECTED",
        "trainer_slug": "qa_engineer_interview_trainer",
        "reason": "Maps to existing QA quest about test design and release decisions",
    },
    "qa_login_form_testing_v1": {
        "quest_id": "qa_payment_defect_release",
        "mode": "REDIRECTED",
        "trainer_slug": "qa_engineer_interview_trainer",
        "reason": "Maps to existing QA quest covering evidence collection and analysis",
    },
    "qa_regression_vs_retest_v1": {
        "quest_id": None,
        "mode": "HIDE_TEMPORARILY",
        "trainer_slug": "qa_engineer_interview_trainer",
        "reason": "No suitable quest equivalent yet; hid from primary navigation",
    },
    "qa_self_presentation_v1": {
        "quest_id": None,
        "mode": "HIDE_TEMPORARILY",
        "trainer_slug": "qa_engineer_interview_trainer",
        "reason": "Generic self-presentation; no quest equivalent yet",
    },
}

# ---------------------------------------------------------------------------
# BA Legacy Scenarios (Phase 2)
# ---------------------------------------------------------------------------

BA_SCENARIO_MAPPING: dict[str, dict] = {
    "ba_phase2_stakeholder_requirements": {
        "quest_id": "ba_payment_requirements_conflict",
        "mode": "REDIRECTED",
        "trainer_slug": "business_analyst_interview_trainer",
        "reason": "Maps to existing BA quest about stakeholder requirements",
    },
    "ba_phase2_process_analysis": {
        "quest_id": None,
        "mode": "HIDE_TEMPORARILY",
        "trainer_slug": "business_analyst_interview_trainer",
        "reason": "No quest equivalent yet; hid from primary navigation",
    },
    "ba_phase2_documentation_artifacts": {
        "quest_id": None,
        "mode": "HIDE_TEMPORARILY",
        "trainer_slug": "business_analyst_interview_trainer",
        "reason": "No quest equivalent yet; hid from primary navigation",
    },
    "ba_phase2_conflict_resolution": {
        "quest_id": "ba_payment_requirements_conflict",
        "mode": "REDIRECTED",
        "trainer_slug": "business_analyst_interview_trainer",
        "reason": "Maps to existing BA quest about conflict resolution",
    },
    "ba_phase2_traceability_impact": {
        "quest_id": None,
        "mode": "HIDE_TEMPORARILY",
        "trainer_slug": "business_analyst_interview_trainer",
        "reason": "No quest equivalent yet; hid from primary navigation",
    },
    "ba_phase2_real_case_analysis": {
        "quest_id": None,
        "mode": "HIDE_TEMPORARILY",
        "trainer_slug": "business_analyst_interview_trainer",
        "reason": "No quest equivalent yet; hid from primary navigation",
    },
}

# ---------------------------------------------------------------------------
# Combined registry
# ---------------------------------------------------------------------------

SCENARIO_QUEST_MAPPING: dict[str, dict] = {}
SCENARIO_QUEST_MAPPING.update(QA_SCENARIO_MAPPING)
SCENARIO_QUEST_MAPPING.update(BA_SCENARIO_MAPPING)


def get_scenario_mapping(scenario_id: str) -> dict | None:
    """Get the mapping for a legacy scenario ID, or None if unmapped."""
    return SCENARIO_QUEST_MAPPING.get(scenario_id)


def get_quest_id_for_scenario(scenario_id: str) -> str | None:
    """Get the target quest ID for a legacy scenario, or None if hidden/unmapped."""
    mapping = get_scenario_mapping(scenario_id)
    if mapping is None:
        return None
    if mapping["mode"] == "HIDE_TEMPORARILY":
        return None
    return mapping["quest_id"]


def is_scenario_hidden(scenario_id: str) -> bool:
    """Check if a legacy scenario should be hidden from normal navigation."""
    mapping = get_scenario_mapping(scenario_id)
    if mapping is None:
        return False
    return mapping["mode"] in ("HIDE_TEMPORARILY",)


def is_scenario_converted(scenario_id: str) -> bool:
    """Check if a legacy scenario has been converted to a quest."""
    mapping = get_scenario_mapping(scenario_id)
    if mapping is None:
        return False
    return mapping["mode"] == "CONVERTED"


def get_trainer_slug_for_scenario(scenario_id: str) -> str | None:
    """Get the trainer slug for a legacy scenario."""
    mapping = get_scenario_mapping(scenario_id)
    if mapping is None:
        return None
    return mapping["trainer_slug"]
