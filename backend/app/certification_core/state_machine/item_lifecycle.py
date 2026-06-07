"""Item lifecycle state machine — canonical states, allowed/forbidden transitions, role gates.

Canonical states (matching doc 06 with full set):
  draft, generated, automated_validation_failed, automated_validation_passed,
  expert_review_required, approved_for_pilot, pilot, calibration_review,
  calibrated, exam_eligible, under_review, suspended, retired, archived
"""

from __future__ import annotations

from typing import Optional

# ---------------------------------------------------------------------------
# Canonical States (matching certification doc 06)
# ---------------------------------------------------------------------------

ITEM_LIFECYCLE_STATES = [
    "draft",
    "generated",
    "automated_validation_failed",
    "automated_validation_passed",
    "expert_review_required",
    "approved_for_pilot",
    "pilot",
    "calibration_review",
    "calibrated",
    "exam_eligible",
    "under_review",
    "suspended",
    "retired",
    "archived",
]

# ---------------------------------------------------------------------------
# Allowed transitions: (from_status, to_status) -> True
# ---------------------------------------------------------------------------

ALLOWED_TRANSITIONS: dict[tuple[str, str], bool] = {
    # Draft transitions
    ("draft", "draft"): True,
    ("draft", "generated"): True,
    ("draft", "expert_review_required"): True,
    ("draft", "retired"): True,
    # Generated transitions
    ("generated", "draft"): True,
    ("generated", "automated_validation_failed"): True,
    ("generated", "automated_validation_passed"): True,
    ("generated", "retired"): True,
    # Auto-validation failed
    ("automated_validation_failed", "draft"): True,
    ("automated_validation_failed", "generated"): True,
    ("automated_validation_failed", "retired"): True,
    # Auto-validation passed
    ("automated_validation_passed", "expert_review_required"): True,
    ("automated_validation_passed", "retired"): True,
    # Expert review required
    ("expert_review_required", "draft"): True,
    ("expert_review_required", "automated_validation_passed"): True,
    ("expert_review_required", "approved_for_pilot"): True,
    ("expert_review_required", "under_review"): True,
    ("expert_review_required", "retired"): True,
    # Approved for pilot
    ("approved_for_pilot", "expert_review_required"): True,
    ("approved_for_pilot", "pilot"): True,
    ("approved_for_pilot", "retired"): True,
    # Pilot
    ("pilot", "approved_for_pilot"): True,
    ("pilot", "calibration_review"): True,
    ("pilot", "under_review"): True,
    ("pilot", "suspended"): True,
    ("pilot", "retired"): True,
    # Calibration review
    ("calibration_review", "pilot"): True,
    ("calibration_review", "calibrated"): True,
    ("calibration_review", "under_review"): True,
    ("calibration_review", "retired"): True,
    # Calibrated
    ("calibrated", "calibration_review"): True,
    ("calibrated", "exam_eligible"): True,
    ("calibrated", "under_review"): True,
    ("calibrated", "suspended"): True,
    ("calibrated", "retired"): True,
    # Exam eligible
    ("exam_eligible", "under_review"): True,
    ("exam_eligible", "suspended"): True,
    ("exam_eligible", "retired"): True,
    # Under review
    ("under_review", "expert_review_required"): True,
    ("under_review", "approved_for_pilot"): True,
    ("under_review", "pilot"): True,
    ("under_review", "calibrated"): True,
    ("under_review", "suspended"): True,
    ("under_review", "retired"): True,
    # Suspended
    ("suspended", "under_review"): True,
    ("suspended", "draft"): True,
    ("suspended", "retired"): True,
    # Retired (terminal except archived)
    ("retired", "archived"): True,
    # Archived (terminal)
    ("archived", "archived"): True,
}

# ---------------------------------------------------------------------------
# Forbidden transitions — explicitly documented (task requirement)
# ---------------------------------------------------------------------------

FORBIDDEN_TRANSITIONS: list[dict] = [
    {"from": "draft", "to": "exam_eligible", "reason": "Direct draft-to-exam-eligible bypasses all validation gates"},
    {"from": "generated", "to": "exam_eligible", "reason": "Generated items must pass validation, expert review, pilot and calibration"},
    {"from": "generated", "to": "approved_for_pilot", "reason": "Generated items must pass automated validation first"},
    {"from": "draft", "to": "approved_for_pilot", "reason": "Draft items must undergo validation and review"},
    {"from": "approved_for_pilot", "to": "exam_eligible", "reason": "Items must complete pilot and calibration before exam eligibility"},
    {"from": "pilot", "to": "exam_eligible", "reason": "Items must complete calibration before exam eligibility"},
    {"from": "suspended", "to": "exam_eligible", "reason": "Suspended items require full corrective review before exam eligibility"},
    {"from": "retired", "to": "exam_eligible", "reason": "Retired items cannot become exam eligible"},
    {"from": "retired", "to": "pilot", "reason": "Retired items cannot re-enter active lifecycle stages"},
]

# ---------------------------------------------------------------------------
# Role gates: some transitions require specific roles
# ---------------------------------------------------------------------------

ROLE_GATES: dict[tuple[str, str], str] = {
    ("automated_validation_passed", "expert_review_required"): "content_author",
    ("expert_review_required", "approved_for_pilot"): "expert_reviewer",
    ("approved_for_pilot", "pilot"): "domain_owner",
    ("pilot", "calibration_review"): "psychometric_reviewer",
    ("calibration_review", "calibrated"): "psychometric_reviewer",
    ("calibrated", "exam_eligible"): "domain_owner",
    ("exam_eligible", "suspended"): "expert_reviewer",
    ("suspended", "under_review"): "domain_owner",
    ("suspended", "draft"): "domain_owner",
    ("*", "retired"): "domain_owner",
}

# ---------------------------------------------------------------------------
# Role-based self-approval prevention
# ---------------------------------------------------------------------------

# Roles that cannot self-approve expert gates for their own items
SELF_APPROVAL_RESTRICTED_ROLES = ["content_author", "domain_owner"]

# No LLM actor may self-approve expert gates
LLM_ACTOR_PREFIX = "llm:"

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_transition_allowed(from_status: str, to_status: str) -> bool:
    """Check if a transition is explicitly allowed."""
    return ALLOWED_TRANSITIONS.get((from_status, to_status), False)


def get_allowed_transitions(from_status: str) -> list[str]:
    """Get all allowed target states from a given status."""
    return [to for (f, to), allowed in ALLOWED_TRANSITIONS.items() if f == from_status and allowed]


def get_required_role(from_status: str, to_status: str) -> Optional[str]:
    """Get the role required for a specific transition, if any."""
    gate = ROLE_GATES.get((from_status, to_status))
    if gate:
        return gate
    # Check wildcard for "retired"
    if to_status == "retired":
        wildcard = ROLE_GATES.get(("*", "retired"))
        if wildcard:
            return wildcard
    return None


def validate_transition(
    from_status: str,
    to_status: str,
    actor_role: str,
    actor_id: str,
) -> dict:
    """Validate a lifecycle transition. Returns a dict with 'allowed' and 'message'."""
    # Check if states exist
    if from_status not in ITEM_LIFECYCLE_STATES:
        return {"allowed": False, "message": f"Unknown from_status: {from_status}"}
    if to_status not in ITEM_LIFECYCLE_STATES:
        return {"allowed": False, "message": f"Unknown to_status: {to_status}"}

    # Check explicit forbidden transitions
    for forbidden in FORBIDDEN_TRANSITIONS:
        if forbidden["from"] == from_status and forbidden["to"] == to_status:
            return {
                "allowed": False,
                "message": f"Forbidden transition: {forbidden['reason']}",
            }

    # Check if transition is allowed
    if not is_transition_allowed(from_status, to_status):
        return {"allowed": False, "message": f"Transition from '{from_status}' to '{to_status}' is not defined"}

    # Check role gate
    required_role = get_required_role(from_status, to_status)
    if required_role and actor_role != required_role:
        return {
            "allowed": False,
            "message": f"Role '{actor_role}' cannot perform this transition. Required role: '{required_role}'",
        }

    # Check LLM self-approval prevention
    if actor_id.startswith(LLM_ACTOR_PREFIX) and required_role in ("expert_reviewer", "domain_owner"):
        return {
            "allowed": False,
            "message": "LLM actors cannot self-approve expert or domain-owner gates",
        }

    return {"allowed": True, "message": "Transition allowed"}
