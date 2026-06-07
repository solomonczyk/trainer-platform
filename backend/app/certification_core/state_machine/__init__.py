"""Item lifecycle state machine — allowed/forbidden transitions with role-based gates."""

from app.certification_core.state_machine.item_lifecycle import (
    ITEM_LIFECYCLE_STATES,
    ALLOWED_TRANSITIONS,
    FORBIDDEN_TRANSITIONS,
    ROLE_GATES,
    is_transition_allowed,
    get_allowed_transitions,
    validate_transition,
)

__all__ = [
    "ITEM_LIFECYCLE_STATES",
    "ALLOWED_TRANSITIONS",
    "FORBIDDEN_TRANSITIONS",
    "ROLE_GATES",
    "is_transition_allowed",
    "get_allowed_transitions",
    "validate_transition",
]
