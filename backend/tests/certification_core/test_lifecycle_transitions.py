"""Tests for item lifecycle state machine — allowed and forbidden transitions."""

from __future__ import annotations

import pytest
from app.certification_core.state_machine.item_lifecycle import (
    ITEM_LIFECYCLE_STATES,
    ALLOWED_TRANSITIONS,
    FORBIDDEN_TRANSITIONS,
    is_transition_allowed,
    get_allowed_transitions,
    validate_transition,
    ROLE_GATES,
)


class TestLifecycleStates:
    """Item lifecycle state definition tests."""

    def test_all_states_defined(self):
        assert len(ITEM_LIFECYCLE_STATES) >= 12
        required = ["draft", "generated", "exam_eligible", "retired", "archived"]
        for state in required:
            assert state in ITEM_LIFECYCLE_STATES, f"Required state '{state}' missing"

    def test_allowed_transitions_defined(self):
        assert len(ALLOWED_TRANSITIONS) > 0


class TestAllowedTransitions:
    """Tests for allowed lifecycle transitions."""

    def test_draft_can_go_to_generated(self):
        assert is_transition_allowed("draft", "generated") is True

    def test_draft_can_go_to_expert_review(self):
        assert is_transition_allowed("draft", "expert_review_required") is True

    def test_calibrated_can_go_to_exam_eligible(self):
        assert is_transition_allowed("calibrated", "exam_eligible") is True

    def test_exam_eligible_can_go_to_suspended(self):
        assert is_transition_allowed("exam_eligible", "suspended") is True

    def test_retired_can_go_to_archived(self):
        assert is_transition_allowed("retired", "archived") is True

    def test_approved_for_pilot_can_go_to_pilot(self):
        assert is_transition_allowed("approved_for_pilot", "pilot") is True

    def test_pilot_can_go_to_calibration_review(self):
        assert is_transition_allowed("pilot", "calibration_review") is True

    def test_calibration_review_can_go_to_calibrated(self):
        assert is_transition_allowed("calibration_review", "calibrated") is True

    def test_under_review_can_go_to_suspended(self):
        assert is_transition_allowed("under_review", "suspended") is True

    def test_suspended_can_go_to_under_review(self):
        assert is_transition_allowed("suspended", "under_review") is True

    def test_suspended_can_go_to_draft(self):
        assert is_transition_allowed("suspended", "draft") is True


class TestForbiddenTransitions:
    """Tests for explicitly forbidden transitions (task requirement)."""

    def test_draft_to_exam_eligible_forbidden(self):
        """Direct draft-to-exam-eligible MUST be blocked."""
        result = validate_transition(
            from_status="draft",
            to_status="exam_eligible",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_generated_to_exam_eligible_forbidden(self):
        """Generated items MUST NOT go directly to exam eligible."""
        result = validate_transition(
            from_status="generated",
            to_status="exam_eligible",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_generated_to_approved_for_pilot_forbidden(self):
        """Generated items must pass automated validation first."""
        result = validate_transition(
            from_status="generated",
            to_status="approved_for_pilot",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_draft_to_approved_for_pilot_forbidden(self):
        result = validate_transition(
            from_status="draft",
            to_status="approved_for_pilot",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_approved_for_pilot_to_exam_eligible_forbidden(self):
        result = validate_transition(
            from_status="approved_for_pilot",
            to_status="exam_eligible",
            actor_role="domain_owner",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_pilot_to_exam_eligible_forbidden(self):
        result = validate_transition(
            from_status="pilot",
            to_status="exam_eligible",
            actor_role="domain_owner",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_suspended_to_exam_eligible_forbidden(self):
        result = validate_transition(
            from_status="suspended",
            to_status="exam_eligible",
            actor_role="domain_owner",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_retired_to_exam_eligible_forbidden(self):
        result = validate_transition(
            from_status="retired",
            to_status="exam_eligible",
            actor_role="domain_owner",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_retired_to_pilot_forbidden(self):
        result = validate_transition(
            from_status="retired",
            to_status="pilot",
            actor_role="domain_owner",
            actor_id="user_1",
        )
        assert result["allowed"] is False


class TestRoleGates:
    """Tests for role-based transition gates."""

    def test_expert_review_to_approved_needs_expert_role(self):
        result = validate_transition(
            from_status="expert_review_required",
            to_status="approved_for_pilot",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_expert_review_to_approved_with_expert_role(self):
        result = validate_transition(
            from_status="expert_review_required",
            to_status="approved_for_pilot",
            actor_role="expert_reviewer",
            actor_id="user_1",
        )
        assert result["allowed"] is True

    def test_calibrated_to_exam_eligible_needs_domain_owner(self):
        result = validate_transition(
            from_status="calibrated",
            to_status="exam_eligible",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_calibrated_to_exam_eligible_with_domain_owner(self):
        result = validate_transition(
            from_status="calibrated",
            to_status="exam_eligible",
            actor_role="domain_owner",
            actor_id="user_1",
        )
        assert result["allowed"] is True


class TestLLMSelfApprovalBlocked:
    """LLM actors cannot self-approve expert gates."""

    def test_llm_cannot_approve_expert_gate(self):
        result = validate_transition(
            from_status="expert_review_required",
            to_status="approved_for_pilot",
            actor_role="expert_reviewer",
            actor_id="llm:gpt-4",
        )
        assert result["allowed"] is False
        assert "LLM actors" in result["message"]

    def test_llm_cannot_approve_domain_owner_gate(self):
        result = validate_transition(
            from_status="calibrated",
            to_status="exam_eligible",
            actor_role="domain_owner",
            actor_id="llm:gpt-4",
        )
        assert result["allowed"] is False

    def test_human_can_approve_expert_gate(self):
        result = validate_transition(
            from_status="expert_review_required",
            to_status="approved_for_pilot",
            actor_role="expert_reviewer",
            actor_id="human_expert_1",
        )
        assert result["allowed"] is True


class TestUnknownStates:
    """Tests for unknown state handling."""

    def test_unknown_from_status(self):
        result = validate_transition(
            from_status="nonexistent",
            to_status="draft",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False

    def test_unknown_to_status(self):
        result = validate_transition(
            from_status="draft",
            to_status="nonexistent",
            actor_role="content_author",
            actor_id="user_1",
        )
        assert result["allowed"] is False


class TestGetAllowedTransitions:
    """Tests for the helper that lists allowed transitions from a state."""

    def test_get_allowed_from_draft(self):
        allowed = get_allowed_transitions("draft")
        assert "generated" in allowed
        assert "expert_review_required" in allowed
        assert "retired" in allowed

    def test_get_allowed_from_retired(self):
        allowed = get_allowed_transitions("retired")
        assert "archived" in allowed

    def test_empty_for_unknown(self):
        allowed = get_allowed_transitions("unknown_state")
        assert allowed == []


class TestForbiddenTransitionsDocumented:
    """All required forbidden transitions are documented."""

    def test_all_forbidden_have_from_and_to(self):
        for fb in FORBIDDEN_TRANSITIONS:
            assert "from" in fb
            assert "to" in fb
            assert "reason" in fb

    def test_forbidden_transition_is_rejected(self):
        for fb in FORBIDDEN_TRANSITIONS:
            result = validate_transition(
                from_status=fb["from"],
                to_status=fb["to"],
                actor_role="platform_admin",
                actor_id="admin_1",
            )
            assert result["allowed"] is False, (
                f"Transition {fb['from']} -> {fb['to']} should be forbidden"
            )
