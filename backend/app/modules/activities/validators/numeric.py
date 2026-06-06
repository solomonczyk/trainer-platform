"""Numeric validator — exact or tolerance-based comparison."""
from __future__ import annotations


def validate_numeric(submitted_answer, payload: dict) -> dict:
    """Validate a numeric answer.

    Args:
        submitted_answer: Number (int or float) or string representing a number
        payload: Must contain "correct" (number) and optional "tolerance" (number)

    Returns:
        Validation result dict
    """
    correct = payload.get("correct")
    if correct is None:
        return _error_result("No correct answer defined")

    tolerance = payload.get("tolerance", 0)

    try:
        submitted = float(submitted_answer)
        correct_val = float(correct)
        tolerance_val = float(tolerance)
    except (TypeError, ValueError):
        return _error_result("Invalid numeric format")

    if abs(submitted - correct_val) <= tolerance_val:
        return {
            "status": "correct",
            "score": 100,
            "passed": True,
            "feedback": {
                "submitted": submitted,
                "correct": correct_val,
                "tolerance": tolerance_val,
            },
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }
    else:
        return {
            "status": "incorrect",
            "score": 0,
            "passed": False,
            "feedback": {
                "submitted": submitted,
                "correct": correct_val,
                "tolerance": tolerance_val,
            },
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
