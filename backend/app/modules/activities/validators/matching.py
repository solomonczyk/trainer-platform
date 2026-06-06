"""Matching validator — exact pair mapping comparison, order-independent."""
from __future__ import annotations


def validate_matching(submitted_answer: dict | list, payload: dict) -> dict:
    """Validate a matching answer.

    Args:
        submitted_answer: Dict mapping left_item -> right_item, or list of {"left": ..., "right": ...} pairs
        payload: Must contain "pairs" list of {"left": ..., "right": ...}

    Returns:
        Validation result dict. Order-independent comparison.
        Duplicate/unknown keys are rejected.
    """
    pairs = payload.get("pairs")
    if not pairs:
        return _error_result("No correct pairs defined")

    # Build correct mapping
    correct_mapping = {}
    for p in pairs:
        left = str(p.get("left", "")).strip()
        right = str(p.get("right", "")).strip()
        correct_mapping[left] = right

    # Normalize submitted answer
    if isinstance(submitted_answer, list):
        submitted_mapping = {}
        for item in submitted_answer:
            left = str(item.get("left", "")).strip()
            right = str(item.get("right", "")).strip()
            submitted_mapping[left] = right
    elif isinstance(submitted_answer, dict):
        submitted_mapping = {str(k).strip(): str(v).strip() for k, v in submitted_answer.items()}
    else:
        return _incorrect_result("Invalid answer format")

    if not submitted_mapping:
        return _incorrect_result("No answer provided")

    # Check for unknown keys
    unknown_keys = set(submitted_mapping.keys()) - set(correct_mapping.keys())
    if unknown_keys:
        return {
            "status": "incorrect",
            "score": 0,
            "passed": False,
            "feedback": {
                "error": "Unknown items in answer",
                "unknown_keys": list(unknown_keys),
            },
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }

    # Compare each pair
    correct_count = 0
    total_pairs = len(correct_mapping)
    results = []

    for left, expected_right in correct_mapping.items():
        user_right = submitted_mapping.get(left, "")
        is_correct = user_right.strip() == expected_right.strip()
        if is_correct:
            correct_count += 1
        results.append({
            "left": left,
            "submitted_right": user_right if not is_correct else None,
            "expected_right": expected_right if not is_correct else None,
            "is_correct": is_correct,
        })

    all_correct = correct_count == total_pairs

    if all_correct:
        return {
            "status": "correct",
            "score": 100,
            "passed": True,
            "feedback": {"pair_results": results},
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }
    elif correct_count > 0:
        score = int((correct_count / total_pairs) * 100)
        return {
            "status": "partial",
            "score": score,
            "passed": False,
            "feedback": {"pair_results": results},
            "evaluation_mode": "deterministic",
            "validation_status": "validated",
        }
    else:
        return {
            "status": "incorrect",
            "score": 0,
            "passed": False,
            "feedback": {"pair_results": results},
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
