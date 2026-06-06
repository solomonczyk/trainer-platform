"""Validator registry — maps activity types to deterministic validator functions."""
from __future__ import annotations

from typing import Any, Callable, Dict

from app.modules.activities.validators.single_choice import validate_single_choice
from app.modules.activities.validators.multiple_choice import validate_multiple_choice
from app.modules.activities.validators.numeric import validate_numeric
from app.modules.activities.validators.fill_blanks import validate_fill_blanks
from app.modules.activities.validators.matching import validate_matching

# Result contract
VALIDATION_RESULT_SCHEMA = {
    "status": "correct|partial|incorrect",
    "score": "0_to_100",
    "passed": "boolean",
    "feedback": "safe_structured_feedback",
    "evaluation_mode": "deterministic",
    "validation_status": "validated",
}

VALIDATORS: Dict[str, Callable] = {
    "single_choice": validate_single_choice,
    "multiple_choice": validate_multiple_choice,
    "numeric": validate_numeric,
    "fill_blanks": validate_fill_blanks,
    "matching": validate_matching,
}


def get_validator(activity_type: str):
    """Return the validator function for the given activity type."""
    validator = VALIDATORS.get(activity_type)
    if validator is None:
        raise ValueError(f"Unknown activity type: {activity_type}")
    return validator


def validate(submitted_answer: Any, payload: dict, activity_type: str) -> dict:
    """Validate a submitted answer against the correct answer in payload.

    Args:
        submitted_answer: The user's submitted answer (structure depends on type)
        payload: The activity payload containing correct answer data
        activity_type: Type of activity

    Returns:
        Dict with status, score, passed, feedback, evaluation_mode, validation_status
    """
    validator = get_validator(activity_type)
    return validator(submitted_answer, payload)
