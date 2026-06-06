"""Multiple choice validator — order-independent set comparison."""
from __future__ import annotations


def validate_multiple_choice(submitted_answer: list, payload: dict) -> dict:
    """Validate a multiple choice answer.

    Args:
        submitted_answer: List of selected option strings
        payload: Must contain "correct" key with list of correct option strings

    Returns:
        Validation result dict. Partial score if some correct options selected
        and no extra options selected.
    """
    correct = payload.get("correct")
    if correct is None:
        return _error_result("No correct answer defined")

    if not isinstance(submitted_answer, list):
        return _incorrect_result("Invalid answer format")

    submitted_set = set(str(s).strip() for s in submitted_answer if s)
    correct_set = set(str(c).strip() for c in correct if c)

    if not correct_set:
        return _error_result("No correct answers defined")

    if not submitted_set:
        return _incorrect_result("No answer provided")

    # Check for extra options
    has_extra = submitted_set - correct_set

    # Count correct selections
    correct_selected = submitted_set & correct_set
    all_correct_selected = correct_selected == correct_set

    if all_correct_selected and not has_extra:
        return {
            "status": "correct",
            "score": 100,
            "passed": True,
            "feedback": {
                "selected": list(submitted_set),
                "correct": list(correct_set),
            },
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }
    elif has_extra:
        # Extra options selected — incorrect (strict)
        return {
            "status": "incorrect",
            "score": 0,
            "passed": False,
            "feedback": {
                "selected": list(submitted_set),
                "correct": list(correct_set),
                "extra_options": list(has_extra),
            },
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }
    else:
        # Partial selection — some correct, no extras
        partial_score = int((len(correct_selected) / len(correct_set)) * 100)
        return {
            "status": "partial",
            "score": partial_score,
            "passed": partial_score >= 100,
            "feedback": {
                "selected": list(submitted_set),
                "correct": list(correct_set),
                "missing": list(correct_set - submitted_set),
            },
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }


def _incorrect_result(message: str) -> dict:
    return {
        "status": "incorrect",
        "score": 0,
        "passed": False,
        "feedback": {"error": message},
        "evaluation_mode": "deterministic",
        "validation_status": "validated",
    }


def _error_result(message: str) -> dict:
    return {
        "status": "incorrect",
        "score": 0,
        "passed": False,
        "feedback": {"error": message},
        "evaluation_mode": "deterministic",
        "validation_status": "validated",
    }
