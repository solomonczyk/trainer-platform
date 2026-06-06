"""Fill blanks validator — ordered blank comparison with normalization."""
from __future__ import annotations

import re


def _normalize(text: str) -> str:
    """Normalize text: strip, collapse whitespace, lowercase."""
    return re.sub(r'\s+', ' ', text.strip().lower())


def validate_fill_blanks(submitted_answer: dict, payload: dict) -> dict:
    """Validate fill-in-the-blanks answer.

    Args:
        submitted_answer: Dict mapping blank_id to filled text, e.g. {"blank_0": "value1", "blank_1": "value2"}
        payload: Must contain "correct" as ordered list of correct strings, and optionally "blanks" array
                 with blank_id definitions.

    Returns:
        Validation result dict. All blanks must match exactly (after normalization).
    """
    correct_answers = payload.get("correct")
    if not correct_answers:
        return _error_result("No correct answers defined")

    if not isinstance(submitted_answer, dict):
        return _incorrect_result("Invalid answer format")

    # Sort blanks by their index
    blanks = payload.get("blanks", [])
    if blanks:
        ordered_blanks = sorted(
            blanks,
            key=lambda b: int(re.search(r'\d+', b.get("id", "0")).group(0) if re.search(r'\d+', b.get("id", "0")) else 0)
        )
        blank_ids = [b["id"] for b in ordered_blanks]
    else:
        # Fallback: sort by blank_X numeric index
        blank_ids = sorted(submitted_answer.keys(), key=lambda k: int(re.search(r'\d+', k).group(0)) if re.search(r'\d+', k) else 0)

    # Compare each blank
    results = []
    all_correct = True
    correct_count = 0
    total_blanks = len(correct_answers)

    for i, blank_id in enumerate(blank_ids):
        if i >= len(correct_answers):
            break
        user_val = submitted_answer.get(blank_id, "")
        expected = correct_answers[i]

        if not isinstance(user_val, str):
            user_val = str(user_val)

        is_correct = _normalize(user_val) == _normalize(expected)
        results.append({
            "blank_id": blank_id,
            "submitted": user_val,
            "expected": expected if is_correct else None,
            "is_correct": is_correct,
        })
        if is_correct:
            correct_count += 1
        else:
            all_correct = False

    if all_correct and correct_count == total_blanks:
        score = 100
        status = "correct"
        passed = True
    elif correct_count > 0:
        score = int((correct_count / total_blanks) * 100)
        status = "partial"
        passed = False
    else:
        score = 0
        status = "incorrect"
        passed = False

    return {
        "status": status,
        "score": score,
        "passed": passed,
        "feedback": {
            "blank_results": results,
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
