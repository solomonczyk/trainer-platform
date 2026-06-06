"""Single choice validator — exact option comparison."""
from __future__ import annotations


def validate_single_choice(submitted_answer: str, payload: dict) -> dict:
    """Validate a single choice answer.

    Args:
        submitted_answer: The selected option string
        payload: Must contain "correct" key with the correct option string

    Returns:
        Validation result dict
    """
    correct = payload.get("correct")
    if correct is None:
        return _error_result("No correct answer defined")

    if not isinstance(submitted_answer, str) or not submitted_answer.strip():
        return _incorrect_result("No answer provided")

    is_correct = submitted_answer.strip() == correct.strip()

    if is_correct:
        return {
            "status": "correct",
            "score": 100,
            "passed": True,
            "feedback": {"selected": submitted_answer, "correct": correct},
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }
    else:
        return {
            "status": "incorrect",
            "score": 0,
            "passed": False,
            "feedback": {"selected": submitted_answer, "correct": correct},
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
