"""Quest step evaluator — deterministic for closed types, AI rubric for open types.

DETERMINISTIC EVALUATION:
- single_choice: exact match against correct option
- multiple_choice: compare selected vs correct sets with partial scoring
- ordering: compare item order against correct order (permutation distance)
- matching: compare left-right pairs against correct mappings
- evidence_select: check selected vs relevant items

AI RUBRIC EVALUATION (free_text / dialogue):
- Delegates to the existing AIGatewayService
- Wraps with timeout handling
- Preserves answer on timeout/failure
- No blind retry
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Deterministic Evaluation
# ---------------------------------------------------------------------------

EVALUATION_TIMEOUT_SECONDS = 45


def evaluate_deterministic(
    step_type: str,
    answer: Any,
    interaction: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate a closed-type step answer deterministically.

    Args:
        step_type: One of single_choice, multiple_choice, ordering, matching, evidence_select
        answer: The user's submitted answer
        interaction: The step interaction payload (contains correct answers)

    Returns:
        Dict with keys: correct, score, max_score, feedback_key, consequence_updates
    """
    if step_type == "single_choice":
        return _eval_single_choice(answer, interaction)
    elif step_type == "multiple_choice":
        return _eval_multiple_choice(answer, interaction)
    elif step_type == "ordering":
        return _eval_ordering(answer, interaction)
    elif step_type == "matching":
        return _eval_matching(answer, interaction)
    elif step_type == "evidence_select":
        return _eval_evidence_select(answer, interaction)
    elif step_type == "decision":
        return _eval_decision(answer, interaction)
    elif step_type == "branching":
        return _eval_branching(answer, interaction)
    elif step_type == "dialogue":
        # Dialogue with allow_free_text=True requires AI rubric.
        # Dialogue with allow_free_text=False and predefined options
        # can be evaluated deterministically like a decision step.
        allow_free_text = interaction.get("allow_free_text", False)
        if allow_free_text:
            raise ValueError(f"Dialogue with free text requires AI rubric evaluation, not deterministic")
        return _eval_dialogue_deterministic(answer, interaction)
    elif step_type == "free_text":
        raise ValueError(f"Step type {step_type} requires AI rubric evaluation, not deterministic")
    else:
        raise ValueError(f"Unknown step type: {step_type}")


def _eval_single_choice(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a single choice answer."""
    options = interaction.get("options", [])
    correct_ids = {o["id"] for o in options if o.get("is_correct")}

    if not correct_ids:
        return {
            "correct": False,
            "score": 0,
            "max_score": 100,
            "feedback_key": "quest.result_no_correct_defined",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    selected = str(answer) if answer else ""
    is_correct = selected in correct_ids

    return {
        "correct": is_correct,
        "score": 100 if is_correct else 0,
        "max_score": 100,
        "feedback_key": "quest.result_correct" if is_correct else "quest.result_incorrect",
        "evaluation_mode": "deterministic",
        "provider_call_executed": False,
    }


def _eval_multiple_choice(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate multiple choice answer with partial scoring."""
    choices = interaction.get("choices", interaction.get("options", []))
    correct_ids = {c["id"] for c in choices if c.get("is_correct")}
    max_score = 100

    if not correct_ids:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_no_correct_defined",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    selected_ids = set(answer) if isinstance(answer, list) else {answer} if answer else set()

    if not selected_ids:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_no_answer",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    correct_hits = len(selected_ids & correct_ids)
    total_correct = len(correct_ids)

    if selected_ids == correct_ids:
        # Perfect match
        return {
            "correct": True,
            "score": max_score,
            "max_score": max_score,
            "feedback_key": "quest.result_correct",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }
    elif correct_hits > 0:
        # Partial
        score = int((correct_hits / total_correct) * max_score)
        return {
            "correct": False,
            "score": score,
            "max_score": max_score,
            "feedback_key": "quest.result_partial",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }
    else:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_incorrect",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }


def _eval_ordering(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate ordering answer by comparing item positions."""
    items = interaction.get("items", [])
    max_score = 100

    if not items:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_no_items",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    correct_item_ids = sorted(items, key=lambda x: x.get("correct_order", 0))
    correct_order = [it["id"] for it in correct_item_ids]

    user_order = answer if isinstance(answer, list) else []

    if not user_order:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_no_answer",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    # Count items in correct positions
    correct_count = sum(1 for i, item_id in enumerate(user_order)
                        if i < len(correct_order) and item_id == correct_order[i])

    if user_order == correct_order:
        return {
            "correct": True,
            "score": max_score,
            "max_score": max_score,
            "feedback_key": "quest.result_ordering_correct",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }
    elif correct_count > 0:
        score = int((correct_count / len(correct_order)) * max_score)
        return {
            "correct": False,
            "score": score,
            "max_score": max_score,
            "feedback_key": "quest.result_ordering_partial",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }
    else:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_ordering_incorrect",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }


def _eval_matching(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate matching by comparing pair mappings."""
    correct_mappings = interaction.get("correct_mappings", {})
    max_score = 100

    if not correct_mappings:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_no_mappings",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    user_mappings = answer if isinstance(answer, dict) else {}

    correct_count = sum(1 for left_id, right_id in user_mappings.items()
                        if left_id in correct_mappings and str(right_id) == str(correct_mappings[left_id]))
    total_pairs = len(correct_mappings)

    if correct_count == total_pairs:
        return {
            "correct": True,
            "score": max_score,
            "max_score": max_score,
            "feedback_key": "quest.result_matching_correct",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }
    elif correct_count > 0:
        score = int((correct_count / total_pairs) * max_score)
        return {
            "correct": False,
            "score": score,
            "max_score": max_score,
            "feedback_key": "quest.result_matching_partial",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }
    else:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_matching_incorrect",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }


def _eval_evidence_select(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate evidence selection by checking relevant items."""
    evidence_items = interaction.get("evidence_items", [])
    max_score = 100

    if not evidence_items:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_no_evidence",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    relevant_ids = {it["id"] for it in evidence_items if it.get("is_relevant")}
    selected_ids = set(answer) if isinstance(answer, list) else {answer} if answer else set()

    if not selected_ids:
        return {
            "correct": False,
            "score": 0,
            "max_score": max_score,
            "feedback_key": "quest.result_no_answer",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    if selected_ids == relevant_ids:
        return {
            "correct": True,
            "score": max_score,
            "max_score": max_score,
            "feedback_key": "quest.result_evidence_correct",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    # Partial scoring: precision + recall
    true_positives = len(selected_ids & relevant_ids)
    false_positives = len(selected_ids - relevant_ids)
    false_negatives = len(relevant_ids - selected_ids)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    score = int(f1 * max_score)

    return {
        "correct": score >= 80,
        "score": score,
        "max_score": max_score,
        "feedback_key": "quest.result_evidence_correct" if score >= 80 else "quest.result_evidence_partial",
        "evaluation_mode": "deterministic",
        "provider_call_executed": False,
    }


def _eval_decision(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate decision step — always passes (consequences tracked separately)."""
    options = interaction.get("options", [])
    selected = str(answer) if answer else ""

    # Find if there's a "correct" option for points
    correct_ids = {o["id"] for o in options if o.get("is_correct")}

    return {
        "correct": selected in correct_ids if correct_ids else True,
        "score": 100 if (selected in correct_ids or not correct_ids) else 0,
        "max_score": 100,
        "feedback_key": "quest.result_decision_made",
        "evaluation_mode": "deterministic",
        "provider_call_executed": False,
    }


def _eval_dialogue_deterministic(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate dialogue with predefined options (no free text) deterministically."""
    options = interaction.get("options", [])
    selected = str(answer) if answer else ""
    correct_ids = {o["id"] for o in options if o.get("is_correct")}

    if correct_ids:
        is_correct = selected in correct_ids
        return {
            "correct": is_correct,
            "score": 100 if is_correct else 0,
            "max_score": 100,
            "feedback_key": "quest.result_correct" if is_correct else "quest.result_incorrect",
            "evaluation_mode": "deterministic",
            "provider_call_executed": False,
        }

    # No correct markers — always pass (consequences tracked separately)
    return {
        "correct": True,
        "score": 100,
        "max_score": 100,
        "feedback_key": "quest.result_decision_made",
        "evaluation_mode": "deterministic",
        "provider_call_executed": False,
    }


def _eval_branching(answer: Any, interaction: dict[str, Any]) -> dict[str, Any]:
    """Evaluate branching step — always passes (branch choice drives narrative)."""
    return {
        "correct": True,
        "score": 100,
        "max_score": 100,
        "feedback_key": "quest.result_branch_selected",
        "evaluation_mode": "deterministic",
        "provider_call_executed": False,
    }


# ---------------------------------------------------------------------------
# AI Rubric Evaluation (for free_text / dialogue)
# ---------------------------------------------------------------------------


async def evaluate_with_ai_rubric(
    answer: str,
    interaction: dict[str, Any],
    locale: str = "ru-RU",
    attempt_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> dict[str, Any]:
    """Evaluate a free-text answer using the AI Gateway with rubric.

    Args:
        answer: The user's free-text answer
        interaction: The step interaction containing AI rubric
        locale: Evaluation locale
        attempt_id: For audit tracking
        correlation_id: For tracing

    Returns:
        Dict with keys: correct, score, max_score, feedback_key, feedback_data,
                       provider, model, latency_ms, cost, correlation_id, timeout
    """
    ai_rubric = interaction.get("ai_rubric", {})
    rubric_version = ai_rubric.get("rubric_version", "1.0.0")
    criteria = ai_rubric.get("criteria", [])
    min_pass_score = ai_rubric.get("minimum_pass_score", 60)

    if not correlation_id:
        correlation_id = str(uuid.uuid4())

    start_time = datetime.now(timezone.utc)

    try:
        # Use the existing AI Gateway
        from app.ai_gateway.schemas import EvaluationGatewayRequest
        from app.ai_gateway.service import AIGatewayService

        gateway = AIGatewayService()

        # Build rubric dict from interaction
        rubric_dict = {
            "pass_score": min_pass_score,
            "critical_fail_enabled": False,
            "criteria": [
                {
                    "criterion_id": c.get("criterion_id", "unknown"),
                    "id": c.get("criterion_id", "unknown"),
                    "name": c.get("criterion_id", "unknown"),
                    "weight": c.get("weight", 1.0),
                    "evidence_required": True,
                }
                for c in criteria
            ],
        }

        gateway_request = EvaluationGatewayRequest(
            attempt_id=attempt_id or correlation_id,
            scenario_id="quest_free_text",
            user_answer=answer,
            rubric=rubric_dict,
            locale=locale,
            user_role="learner",
            ai_role="evaluator",
        )

        gateway_result = await gateway.evaluate_attempt(gateway_request)
        elapsed = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        validated = gateway_result.validated_output
        if validated is None:
            logger.warning("AI evaluation returned no validated output", correlation_id=correlation_id)
            return _timeout_or_fallback_result(answer, correlation_id, elapsed, rubric_version)

        overall_score = validated.overall_score
        passed = validated.passed
        feedback_data = {
            "overall_score": overall_score,
            "passed": passed,
            "strengths": validated.strengths or [],
            "weak_points": validated.weak_points or [],
            "critical_errors": validated.critical_errors or [],
            "criteria": [
                {
                    "criterion_id": cr.criterion_id,
                    "score": cr.score,
                    "evidence": cr.evidence,
                    "comment": cr.comment,
                    "improvement": cr.improvement,
                }
                for cr in validated.criteria or []
            ],
            "next_recommendation": validated.next_recommendation,
        }

        return {
            "correct": passed,
            "score": overall_score,
            "max_score": 100,
            "feedback_key": "quest.result_ai_evaluated" if passed else "quest.result_ai_needs_improvement",
            "feedback_data": feedback_data,
            "evaluation_mode": "ai_rubric",
            "provider": gateway_result.provider or "deepseek",
            "provider_model": gateway_result.model or "deepseek-v4-flash",
            "latency_ms": elapsed,
            "cost": gateway_result.cost_usd or 0,
            "correlation_id": correlation_id,
            "timeout": False,
            "rubric_version": rubric_version,
        }

    except Exception as exc:
        elapsed = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        logger.error("AI evaluation failed", error=str(exc), correlation_id=correlation_id)
        return _timeout_or_fallback_result(answer, correlation_id, elapsed, rubric_version)


def _timeout_or_fallback_result(
    answer: str,
    correlation_id: str,
    latency_ms: int,
    rubric_version: str,
) -> dict[str, Any]:
    """Return a safe fallback result when AI evaluation fails or times out."""
    is_timeout = latency_ms >= EVALUATION_TIMEOUT_SECONDS * 1000

    return {
        "correct": False,
        "score": 0,
        "max_score": 100,
        "feedback_key": "quest.result_ai_timeout" if is_timeout else "quest.result_ai_failed",
        "feedback_data": {
            "overall_score": 0,
            "error": "Evaluation timed out" if is_timeout else "Evaluation failed",
            "answer_saved": True,
        },
        "evaluation_mode": "ai_rubric",
        "provider": "deepseek",
        "provider_model": "deepseek-v4-flash",
        "latency_ms": latency_ms,
        "cost": 0,
        "correlation_id": correlation_id,
        "timeout": is_timeout,
        "rubric_version": rubric_version,
    }


def get_default_consequence(interaction: dict[str, Any], choice_id: str) -> dict[str, Any]:
    """Get consequence for a given choice, falling back to default."""
    for opt in interaction.get("options", []):
        if opt.get("id") == choice_id and opt.get("consequence"):
            return opt["consequence"]
    return {}
