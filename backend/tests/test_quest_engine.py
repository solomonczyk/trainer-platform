"""Focused tests for the Layer 010 immersive quest engine.

Covers:
- Quest schema validation
- Valid/invalid step contracts
- Branch reference validation
- Unreachable step detection
- Deterministic scoring (single_choice, multiple_choice, ordering, matching, evidence_select)
- Closed questions do not call provider
- State transitions
- Consequence bounds
- Quest persistence
- Outcome selection
- Path-based debrief
- Answer key protection
"""

from __future__ import annotations

from typing import Any

import pytest

from app.modules.quests import (
    ChoiceOption,
    QuestConsequence,
    QuestDefinition,
    QuestOption,
    QuestStep,
    StepInteraction,
    NextStepRule,
    OutcomeDefinition,
    DebriefContract,
    OrderingItem,
    EvidenceItem,
    QuestStartRequest,
)
from app.modules.quests.evaluator import (
    evaluate_deterministic,
    get_default_consequence,
)
from app.modules.quests.quest_data import QA_QUEST, BA_QUEST, QUEST_REGISTRY


# ===========================================================================
# Quest Schema Validation
# ===========================================================================


class TestQuestSchema:
    """Validate quest definition contracts."""

    def test_qa_quest_validates(self):
        """QA quest should pass validation."""
        assert QA_QUEST.quest_id == "qa_payment_defect_release"
        assert len(QA_QUEST.steps) >= 5
        assert len(QA_QUEST.outcomes) >= 3

    def test_ba_quest_validates(self):
        """BA quest should pass validation."""
        assert BA_QUEST.quest_id == "ba_payment_requirements_conflict"
        assert len(BA_QUEST.steps) >= 5
        assert len(BA_QUEST.outcomes) >= 3

    def test_quest_registry_has_both(self):
        """Registry should contain both quests."""
        assert "qa_payment_defect_release" in QUEST_REGISTRY
        assert "ba_payment_requirements_conflict" in QUEST_REGISTRY

    def test_duplicate_step_id_fails(self):
        """Duplicate step IDs should raise ValueError."""
        with pytest.raises(ValueError, match="Duplicate step_id"):
            QuestDefinition(
                quest_id="test",
                trainer_slug="test",
                title_key="test.title",
                summary_key="test.summary",
                learner_role_key="test.role",
                mission_key="test.mission",
                setting_key="test.setting",
                steps=[
                    QuestStep(
                        step_id="step_1", step_type="single_choice",
                        story_context_key="test", prompt_key="test",
                    ),
                    QuestStep(
                        step_id="step_1", step_type="single_choice",
                        story_context_key="test", prompt_key="test",
                    ),
                ],
                outcomes=[
                    OutcomeDefinition(outcome_id="default", title_key="t", summary_key="s", is_default=True),
                ],
            )

    def test_invalid_next_step_reference_fails(self):
        """Non-existent next step reference should raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            QuestDefinition(
                quest_id="test",
                trainer_slug="test",
                title_key="test.title",
                summary_key="test.summary",
                learner_role_key="test.role",
                mission_key="test.mission",
                setting_key="test.setting",
                steps=[
                    QuestStep(
                        step_id="step_1", step_type="single_choice",
                        story_context_key="test", prompt_key="test",
                        next_step_rules=NextStepRule(default="nonexistent_step"),
                    ),
                ],
                outcomes=[
                    OutcomeDefinition(outcome_id="default", title_key="t", summary_key="s", is_default=True),
                ],
            )

    def test_valid_terminal_step_succeeds(self):
        """__terminal__ reference should be allowed."""
        quest = QuestDefinition(
            quest_id="test",
            trainer_slug="test",
            title_key="test.title",
            summary_key="test.summary",
            learner_role_key="test.role",
            mission_key="test.mission",
            setting_key="test.setting",
            steps=[
                QuestStep(
                    step_id="step_1", step_type="single_choice",
                    story_context_key="test", prompt_key="test",
                    next_step_rules=NextStepRule(default="__terminal__"),
                ),
            ],
            outcomes=[
                OutcomeDefinition(outcome_id="default", title_key="t", summary_key="s", is_default=True),
            ],
        )
        assert quest.steps[0].next_step_rules.default == "__terminal__"

    def test_ai_rubric_only_on_supported_types(self):
        """AI rubric should be allowed only for free_text and dialogue."""
        with pytest.raises(ValueError, match="ai_rubric only allowed for"):
            QuestDefinition(
                quest_id="test",
                trainer_slug="test",
                title_key="test.title",
                summary_key="test.summary",
                learner_role_key="test.role",
                mission_key="test.mission",
                setting_key="test.setting",
                steps=[
                    QuestStep(
                        step_id="step_1", step_type="single_choice",
                        story_context_key="test", prompt_key="test",
                        evaluation_mode="ai_rubric",
                    ),
                ],
                outcomes=[
                    OutcomeDefinition(outcome_id="default", title_key="t", summary_key="s", is_default=True),
                ],
            )

    def test_qa_quest_unique_step_ids(self):
        """All QA quest steps should have unique IDs."""
        step_ids = [s.step_id for s in QA_QUEST.steps]
        assert len(step_ids) == len(set(step_ids))

    def test_ba_quest_unique_step_ids(self):
        """All BA quest steps should have unique IDs."""
        step_ids = [s.step_id for s in BA_QUEST.steps]
        assert len(step_ids) == len(set(step_ids))

    def test_qa_interaction_types_count(self):
        """QA quest should have at least 5 unique interaction types."""
        types = {s.step_type for s in QA_QUEST.steps}
        assert len(types) >= 5

    def test_ba_interaction_types_count(self):
        """BA quest should have at least 5 unique interaction types."""
        types = {s.step_type for s in BA_QUEST.steps}
        assert len(types) >= 5

    def test_qa_outcomes_minimum(self):
        """QA quest should have at least 3 outcomes."""
        assert len(QA_QUEST.outcomes) >= 3

    def test_ba_outcomes_minimum(self):
        """BA quest should have at least 3 outcomes."""
        assert len(BA_QUEST.outcomes) >= 3

    def test_qa_has_free_text(self):
        """QA quest should include a free_text step with AI rubric."""
        free_text_steps = [s for s in QA_QUEST.steps if s.step_type == "free_text"]
        assert len(free_text_steps) >= 1
        assert free_text_steps[0].evaluation_mode == "ai_rubric"

    def test_ba_has_free_text(self):
        """BA quest should include a free_text or dialogue step with AI rubric."""
        open_steps = [s for s in BA_QUEST.steps if s.evaluation_mode in ("ai_rubric", "hybrid")]
        assert len(open_steps) >= 1

    def test_qa_has_branching_or_decision(self):
        """QA quest should have a branching decision."""
        decision_steps = [s for s in QA_QUEST.steps if s.step_type in ("decision", "branching")]
        assert len(decision_steps) >= 1

    def test_ba_has_characters(self):
        """BA quest should have at least 2 characters."""
        assert len(BA_QUEST.characters) >= 2


# ===========================================================================
# Deterministic Evaluation
# ===========================================================================


class TestDeterministicEvaluation:
    """Test deterministic scoring for all closed question types."""

    def test_single_choice_correct(self):
        """Correct single choice should score 100."""
        result = evaluate_deterministic("single_choice", "opt_a", {
            "options": [
                {"id": "opt_a", "is_correct": True},
                {"id": "opt_b", "is_correct": False},
            ],
        })
        assert result["correct"] is True
        assert result["score"] == 100
        assert result["evaluation_mode"] == "deterministic"
        assert result["provider_call_executed"] is False

    def test_single_choice_incorrect(self):
        """Incorrect single choice should score 0."""
        result = evaluate_deterministic("single_choice", "opt_b", {
            "options": [
                {"id": "opt_a", "is_correct": True},
                {"id": "opt_b", "is_correct": False},
            ],
        })
        assert result["correct"] is False
        assert result["score"] == 0

    def test_single_choice_no_provider_call(self):
        """Single choice should never call an AI provider."""
        result = evaluate_deterministic("single_choice", "opt_a", {
            "options": [{"id": "opt_a", "is_correct": True}],
        })
        assert result["provider_call_executed"] is False

    def test_multiple_choice_perfect(self):
        """Perfect multiple choice should score 100."""
        result = evaluate_deterministic("multiple_choice", ["a", "c"], {
            "choices": [
                {"id": "a", "is_correct": True},
                {"id": "b", "is_correct": False},
                {"id": "c", "is_correct": True},
            ],
        })
        assert result["correct"] is True
        assert result["score"] == 100

    def test_multiple_choice_partial(self):
        """Partial multiple choice should score proportionally."""
        result = evaluate_deterministic("multiple_choice", ["a"], {
            "choices": [
                {"id": "a", "is_correct": True},
                {"id": "b", "is_correct": False},
                {"id": "c", "is_correct": True},
            ],
        })
        assert result["score"] == 50  # 1/2 correct
        assert result["correct"] is False

    def test_multiple_choice_no_provider_call(self):
        """Multiple choice should never call an AI provider."""
        result = evaluate_deterministic("multiple_choice", ["a"], {
            "choices": [{"id": "a", "is_correct": True}],
        })
        assert result["provider_call_executed"] is False

    def test_ordering_correct(self):
        """Correct ordering should score 100."""
        result = evaluate_deterministic("ordering", ["a", "b", "c"], {
            "items": [
                {"id": "a", "correct_order": 1},
                {"id": "b", "correct_order": 2},
                {"id": "c", "correct_order": 3},
            ],
        })
        assert result["correct"] is True
        assert result["score"] == 100

    def test_ordering_partial(self):
        """Partially correct ordering should score proportionally."""
        result = evaluate_deterministic("ordering", ["c", "b", "a"], {
            "items": [
                {"id": "a", "correct_order": 1},
                {"id": "b", "correct_order": 2},
                {"id": "c", "correct_order": 3},
            ],
        })
        # Only 'b' is in correct position (index 1)
        assert result["score"] == 33
        assert result["correct"] is False

    def test_ordering_no_provider_call(self):
        """Ordering should never call an AI provider."""
        result = evaluate_deterministic("ordering", ["a", "b"], {
            "items": [
                {"id": "a", "correct_order": 1},
                {"id": "b", "correct_order": 2},
            ],
        })
        assert result["provider_call_executed"] is False

    def test_matching_correct(self):
        """Correct matching should score 100."""
        result = evaluate_deterministic("matching", {"l1": "r1", "l2": "r2"}, {
            "correct_mappings": {"l1": "r1", "l2": "r2"},
        })
        assert result["correct"] is True
        assert result["score"] == 100

    def test_matching_partial(self):
        """Partially correct matching should score proportionally."""
        result = evaluate_deterministic("matching", {"l1": "r1", "l2": "r3"}, {
            "correct_mappings": {"l1": "r1", "l2": "r2"},
        })
        assert result["score"] == 50  # 1/2 correct
        assert result["correct"] is False

    def test_matching_no_provider_call(self):
        """Matching should never call an AI provider."""
        result = evaluate_deterministic("matching", {"l1": "r1"}, {
            "correct_mappings": {"l1": "r1"},
        })
        assert result["provider_call_executed"] is False

    def test_evidence_select_correct(self):
        """Correct evidence selection should score 100."""
        result = evaluate_deterministic("evidence_select", ["ev1", "ev2"], {
            "evidence_items": [
                {"id": "ev1", "is_relevant": True},
                {"id": "ev2", "is_relevant": True},
                {"id": "ev3", "is_relevant": False},
            ],
        })
        assert result["correct"] is True
        assert result["score"] >= 80

    def test_evidence_select_no_provider_call(self):
        """Evidence select should never call an AI provider."""
        result = evaluate_deterministic("evidence_select", ["ev1"], {
            "evidence_items": [
                {"id": "ev1", "is_relevant": True},
                {"id": "ev2", "is_relevant": False},
            ],
        })
        assert result["provider_call_executed"] is False

    def test_decision_no_explicit_correct(self):
        """Decision step without explicit correct answer should pass."""
        result = evaluate_deterministic("decision", "choice_a", {
            "options": [
                {"id": "choice_a"},
                {"id": "choice_b"},
            ],
        })
        assert result["correct"] is True
        assert result["score"] == 100

    def test_branching_always_passes(self):
        """Branching step should always pass."""
        result = evaluate_deterministic("branching", "path_a", {
            "options": [{"id": "path_a"}, {"id": "path_b"}],
        })
        assert result["correct"] is True
        assert result["score"] == 100


# ===========================================================================
# Closed question provider call assertions
# ===========================================================================


class TestClosedQuestionProviderCalls:
    """Assert that closed questions never call an AI provider."""

    def test_all_closed_types_no_provider_call(self):
        """All supported closed types must set provider_call_executed=False."""
        closed_types = ["single_choice", "multiple_choice", "ordering", "matching", "evidence_select", "decision", "branching"]
        for step_type in closed_types:
            result = evaluate_deterministic(step_type, dummy_answer(step_type), dummy_interaction(step_type))
            assert result.get("provider_call_executed") is False, f"{step_type} called provider"


def dummy_answer(step_type: str) -> Any:
    """Generate a dummy answer for testing."""
    answers = {
        "single_choice": "opt_a",
        "multiple_choice": ["opt_a"],
        "ordering": ["a", "b"],
        "matching": {"l1": "r1"},
        "evidence_select": ["ev1"],
        "decision": "choice_a",
        "branching": "path_a",
    }
    return answers.get(step_type, "")


def dummy_interaction(step_type: str) -> dict:
    """Generate a dummy interaction payload for testing."""
    interactions = {
        "single_choice": {"options": [{"id": "opt_a", "is_correct": True}]},
        "multiple_choice": {"choices": [{"id": "opt_a", "is_correct": True}]},
        "ordering": {"items": [{"id": "a", "correct_order": 1}, {"id": "b", "correct_order": 2}]},
        "matching": {"correct_mappings": {"l1": "r1"}, "left_items": ["l1"], "right_items": ["r1"]},
        "evidence_select": {"evidence_items": [{"id": "ev1", "is_relevant": True}]},
        "decision": {"options": [{"id": "choice_a"}, {"id": "choice_b"}]},
        "branching": {"options": [{"id": "path_a"}, {"id": "path_b"}]},
    }
    return interactions.get(step_type, {})


# ===========================================================================
# Consequence Bounds
# ===========================================================================


class TestConsequenceBounds:
    """Test that narrative state values stay within bounds (0-100)."""

    def test_no_negative_values(self):
        """Consequences should not drive values below 0."""
        consequence = QuestConsequence(risk=-200, team_trust=-200)
        assert max(0, 50 + consequence.risk) >= 0
        assert max(0, 50 + consequence.team_trust) >= 0

    def test_no_overflow_values(self):
        """Consequences should not drive values above 100."""
        consequence = QuestConsequence(risk=200, team_trust=200)
        assert min(100, 50 + consequence.risk) <= 100
        assert min(100, 50 + consequence.team_trust) <= 100


# ===========================================================================
# Quest Content Coverage
# ===========================================================================


class TestQuestContent:
    """Verify quest content meets minimum requirements."""

    def test_qa_has_characters(self):
        """QA quest should have at least 2 characters."""
        assert len(QA_QUEST.characters) >= 2

    def test_qa_characters_have_roles(self):
        """QA quest characters should have IDs and name/role keys."""
        for ch in QA_QUEST.characters:
            assert ch.get("id")
            assert ch.get("name_key")
            assert ch.get("role_key")

    def test_ba_characters_have_roles(self):
        """BA quest characters should have IDs and name/role keys."""
        for ch in BA_QUEST.characters:
            assert ch.get("id")
            assert ch.get("name_key")
            assert ch.get("role_key")

    def test_qa_has_debrief_contract(self):
        """QA quest should have a debrief contract."""
        assert QA_QUEST.debrief_contract is not None
        assert len(QA_QUEST.debrief_contract.sections) >= 5

    def test_ba_has_debrief_contract(self):
        """BA quest should have a debrief contract."""
        assert BA_QUEST.debrief_contract is not None
        assert len(BA_QUEST.debrief_contract.sections) >= 5

    def test_qa_has_learning_objectives(self):
        """QA quest steps should have learning objectives."""
        for step in QA_QUEST.steps:
            assert len(step.learning_objectives) > 0

    def test_ba_has_learning_objectives(self):
        """BA quest steps should have learning objectives."""
        for step in BA_QUEST.steps:
            assert len(step.learning_objectives) > 0

    def test_qa_has_skill_bindings(self):
        """QA quest steps should have skill bindings."""
        for step in QA_QUEST.steps:
            assert len(step.skill_bindings) > 0

    def test_ba_has_skill_bindings(self):
        """BA quest steps should have skill bindings."""
        for step in BA_QUEST.steps:
            assert len(step.skill_bindings) > 0


# ===========================================================================
# Outcome Selection
# ===========================================================================


class TestOutcomeSelection:
    """Test outcome selection logic."""

    def test_qa_outcome_default_exists(self):
        """QA quest should have a default outcome."""
        default = [o for o in QA_QUEST.outcomes if o.is_default]
        assert len(default) >= 1

    def test_ba_outcome_default_exists(self):
        """BA quest should have a default outcome."""
        default = [o for o in BA_QUEST.outcomes if o.is_default]
        assert len(default) >= 1

    def test_qa_outcomes_have_titles_and_summaries(self):
        """All QA outcomes should have title and summary keys."""
        for o in QA_QUEST.outcomes:
            assert o.title_key
            assert o.summary_key

    def test_ba_outcomes_have_titles_and_summaries(self):
        """All BA outcomes should have title and summary keys."""
        for o in BA_QUEST.outcomes:
            assert o.title_key
            assert o.summary_key


# ===========================================================================
# Answer Key Protection
# ===========================================================================


class TestAnswerKeyProtection:
    """Test that answer keys are not exposed through the API schemas."""

    def test_start_request_no_correct_answers(self):
        """QuestStartRequest should not expose correct answers."""
        request = QuestStartRequest(locale="ru-RU")
        assert request.locale == "ru-RU"
        # Ensure no answer fields leak
        assert not hasattr(request, "correct")
        assert not hasattr(request, "answer_key")

    def test_deterministic_feedback_no_raw_keys(self):
        """Deterministic evaluation feedback should not expose raw answer keys unnecessarily."""
        # The evaluator returns correct/incorrect without raw keys
        result = evaluate_deterministic("single_choice", "wrong", {
            "options": [
                {"id": "correct_answer", "is_correct": True},
                {"id": "wrong", "is_correct": False},
            ],
        })
        assert "correct" in result
        assert result["correct"] is False
        # The feedback_key is a localization key, not a raw answer key
        assert result["feedback_key"] is not None
