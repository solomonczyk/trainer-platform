"""Quest engine service — orchestrates quest lifecycle, state machine, and evaluation."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.modules.quests import (
    QuestAnswerResponse,
    QuestDefinition,
    QuestOutcomeResponse,
    QuestProgressResponse,
    QuestStartResponse,
    QuestStep,
    QuestStepResponse,
)
from app.modules.quests.evaluator import (
    EVALUATION_TIMEOUT_SECONDS,
    evaluate_deterministic,
    evaluate_with_ai_rubric,
    get_default_consequence,
)
from app.modules.quests.quest_data import QUEST_REGISTRY
from app.modules.quests import repository as repo

logger = get_logger(__name__)


def get_quest_definition(quest_id: str) -> Optional[QuestDefinition]:
    """Get quest definition from registry."""
    return QUEST_REGISTRY.get(quest_id)


def list_available_quests() -> dict[str, dict[str, Any]]:
    """List all available quests with metadata."""
    return {
        qid: {
            "quest_id": q.quest_id,
            "trainer_slug": q.trainer_slug,
            "title_key": q.title_key,
            "summary_key": q.summary_key,
            "role_key": q.learner_role_key,
            "estimated_minutes": q.estimated_minutes,
            "steps_count": len(q.steps),
            "interaction_types": list({s.step_type for s in q.steps}),
            "outcomes_count": len(q.outcomes),
            "characters_count": len(q.characters),
            "tags": q.tags,
        }
        for qid, q in QUEST_REGISTRY.items()
    }


def _find_step(quest: QuestDefinition, step_id: str) -> Optional[QuestStep]:
    """Find a step by ID in the quest."""
    for s in quest.steps:
        if s.step_id == step_id:
            return s
    return None


def _get_first_step(quest: QuestDefinition) -> Optional[QuestStep]:
    """Get the first step of a quest."""
    return quest.steps[0] if quest.steps else None


def _get_narrative_state(session) -> dict[str, Any]:
    """Extract narrative state from a quest session."""
    return {
        "risk": session.risk or 0,
        "time_remaining": session.time_remaining or 0,
        "team_trust": session.team_trust or 0,
        "client_trust": session.client_trust or 0,
        "evidence_quality": session.evidence_quality or 0,
        "decision_quality": session.decision_quality or 0,
        "flags": session.flags or {},
    }


def _apply_consequence(
    session,
    consequence: dict[str, Any],
) -> dict[str, Any]:
    """Apply a consequence update to the session state."""
    session.risk = max(0, min(100, (session.risk or 0) + consequence.get("risk", 0)))
    session.time_remaining = max(0, min(100, (session.time_remaining or 0) + consequence.get("time_remaining", 0)))
    session.team_trust = max(0, min(100, (session.team_trust or 0) + consequence.get("team_trust", 0)))
    session.client_trust = max(0, min(100, (session.client_trust or 0) + consequence.get("client_trust", 0)))
    session.evidence_quality = max(0, min(100, (session.evidence_quality or 0) + consequence.get("evidence_quality", 0)))
    session.decision_quality = max(0, min(100, (session.decision_quality or 0) + consequence.get("decision_quality", 0)))

    # Update flags
    flags = session.flags or {}
    for k, v in consequence.get("flags", {}).items():
        flags[k] = v
    session.flags = flags

    return _get_narrative_state(session)


def _select_outcome(quest: QuestDefinition, session) -> str:
    """Select the best-matching outcome based on session state."""
    state = _get_narrative_state(session)
    decision_quality = state.get("decision_quality", 0)
    team_trust = state.get("team_trust", 0)
    client_trust = state.get("client_trust", 0)
    evidence_quality = state.get("evidence_quality", 0)

    # Sort outcomes by specificity (most specific first)
    sorted_outcomes = sorted(
        quest.outcomes,
        key=lambda o: (
            -(o.min_decision_quality or 0) - (o.min_team_trust or 0) - (o.min_client_trust or 0) - (o.min_evidence_quality or 0)
        ),
    )

    for outcome in sorted_outcomes:
        if outcome.is_default:
            continue
        if (decision_quality >= (outcome.min_decision_quality or 0)
                and team_trust >= (outcome.min_team_trust or 0)
                and client_trust >= (outcome.min_client_trust or 0)
                and evidence_quality >= (outcome.min_evidence_quality or 0)):
            return outcome.outcome_id

    # Fall back to default
    default = next((o for o in quest.outcomes if o.is_default), None)
    return default.outcome_id if default else quest.outcomes[-1].outcome_id


def _build_debrief(
    quest: QuestDefinition,
    session,
    outcome_id: str,
) -> dict[str, Any]:
    """Build a personalized debrief based on actual quest path."""
    state = _get_narrative_state(session)
    outcome = next((o for o in quest.outcomes if o.outcome_id == outcome_id), None)

    debrief = {
        "outcome": outcome_id,
        "outcome_title_key": outcome.title_key if outcome else "",
        "outcome_summary_key": outcome.summary_key if outcome else "",
        "summary": f"Quest completed with outcome: {outcome_id}",
        "strengths": [],
        "mistakes": [],
        "missed_risks": [],
        "decision_consequences": [],
        "professional_recommendations": [],
        "practical_takeaways": [],
        "skill_results": [],
        "recommended_next_quest": quest.tags[0] if quest.tags else "",
    }

    # Build strengths from session state
    if state.get("decision_quality", 0) >= 70:
        debrief["strengths"].append("quest.debrief.strength_decision_quality")
    if state.get("evidence_quality", 0) >= 70:
        debrief["strengths"].append("quest.debrief.strength_evidence_quality")
    if state.get("team_trust", 0) >= 70:
        debrief["strengths"].append("quest.debrief.strength_team_trust")
    if state.get("client_trust", 0) >= 70:
        debrief["strengths"].append("quest.debrief.strength_client_trust")

    # Build mistakes from low scores
    if state.get("decision_quality", 0) < 40:
        debrief["mistakes"].append("quest.debrief.mistake_decision_quality")
    if state.get("evidence_quality", 0) < 40:
        debrief["mistakes"].append("quest.debrief.mistake_evidence_quality")
    if state.get("risk", 0) > 60:
        debrief["missed_risks"].append("quest.debrief.risk_high")
    if state.get("time_remaining", 100) < 30:
        debrief["missed_risks"].append("quest.debrief.time_low")

    # Build decision consequences
    completed_step_ids = session.completed_step_ids or []
    for step_id in completed_step_ids:
        step = _find_step(quest, step_id)
        if step:
            debrief["decision_consequences"].append({
                "step_id": step_id,
                "prompt_key": step.prompt_key,
                "type": step.step_type,
            })

    # Build practical takeaways
    for skill_binding in quest.debrief_contract.skill_dimensions:
        debrief["skill_results"].append({
            "skill_id": skill_binding,
            "level": "practiced" if state.get("decision_quality", 0) > 40 else "observed",
        })

    return debrief


def _get_answers_map(session) -> dict[str, Any]:
    """Build a map of step_id -> answer from step results."""
    answers = {}
    for sr in (session.step_results or []):
        if sr.answer:
            ans = sr.answer
            if isinstance(ans, dict) and "value" in ans:
                answers[sr.step_id] = ans["value"]
            else:
                answers[sr.step_id] = ans
    return answers


def _get_step_results_map(session) -> dict[str, Any]:
    """Build a map of step_id -> result data from step results."""
    results = {}
    for sr in (session.step_results or []):
        results[sr.step_id] = {
            "status": sr.status,
            "score": sr.score,
            "max_score": sr.max_score,
            "correct": sr.correct,
            "feedback_key": sr.feedback_key,
            "feedback_data": sr.feedback_data,
            "evaluation_mode": sr.evaluation_mode,
            "timed_out": sr.timed_out,
        }
    return results


def _determine_next_step(
    quest: QuestDefinition,
    session,
    step: QuestStep,
    answer: Any = None,
) -> Optional[str]:
    """Determine the next step ID based on step rules and user answer."""
    rules = step.next_step_rules
    default = rules.default or ""

    # Check by_choice rules
    if rules.by_choice and answer:
        selected_id = None
        if isinstance(answer, dict):
            selected_id = answer.get("value", answer.get("choice_id"))
        elif isinstance(answer, str):
            selected_id = answer
        if selected_id and selected_id in rules.by_choice:
            return rules.by_choice[selected_id]

    # Check by_flag rules
    flags = session.flags or {}
    for flag, next_id in rules.by_flag.items():
        if flags.get(flag):
            return next_id

    return default


# ---------------------------------------------------------------------------
# Public Service API
# ---------------------------------------------------------------------------


async def start_quest(
    db: AsyncSession,
    user_id: str,
    quest_id: str,
    locale: str = "ru-RU",
) -> QuestStartResponse:
    """Start a new quest session."""
    quest = get_quest_definition(quest_id)
    if not quest:
        raise ValueError(f"Quest '{quest_id}' not found")

    # Check for existing active session
    existing = await repo.get_active_quest_session(db, user_id, quest_id)
    if existing:
        # Resume existing session
        first_step = _find_step(quest, existing.current_step_id) or _get_first_step(quest)
        return QuestStartResponse(
            session_id=existing.id,
            quest=quest,
            current_step=first_step,
            narrative_state=_get_narrative_state(existing),
            status="resumed",
        )

    # Create new session
    session = await repo.create_quest_session(
        db,
        user_id=user_id,
        quest_id=quest_id,
        trainer_slug=quest.trainer_slug,
        locale=locale,
        initial_state=quest.initial_state,
    )

    # Set first step
    first_step = _get_first_step(quest)
    if first_step:
        session.current_step_id = first_step.step_id
        await repo.update_quest_session(db, session.id, current_step_id=first_step.step_id)
        # Create step result record
        await repo.create_step_result(db, session.id, first_step.step_id, first_step.step_type)

    return QuestStartResponse(
        session_id=session.id,
        quest=quest,
        current_step=first_step,
        narrative_state=_get_narrative_state(session),
        status="started",
    )


async def get_current_step(
    db: AsyncSession,
    session_id: str,
) -> QuestStepResponse:
    """Get the current step for a quest session."""
    session = await repo.get_quest_session(db, session_id)
    if not session:
        raise ValueError("Session not found")

    quest = get_quest_definition(session.quest_id)
    if not quest:
        raise ValueError("Quest not found")

    step = _find_step(quest, session.current_step_id)
    if not step:
        # Get first step
        step = _get_first_step(quest)
        if step:
            session.current_step_id = step.step_id
            await repo.update_quest_session(db, session_id, current_step_id=step.step_id)

    step_result = await repo.get_step_result(db, session_id, session.current_step_id)
    step_result_data = None
    if step_result and step_result.status != "pending":
        step_result_data = {
            "status": step_result.status,
            "score": step_result.score,
            "max_score": step_result.max_score,
            "correct": step_result.correct,
            "feedback_key": step_result.feedback_key,
        }

    return QuestStepResponse(
        session_id=session_id,
        step=step,
        narrative_state=_get_narrative_state(session),
        completed_step_ids=session.completed_step_ids or [],
        answers=_get_answers_map(session),
        step_result=step_result_data,
    )


async def submit_and_evaluate_step(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    step_id: str,
    answer: Any,
    locale: str = "ru-RU",
    idempotency_key: Optional[str] = None,
) -> QuestAnswerResponse:
    """Submit an answer for a step, evaluate it, apply consequences, advance."""
    session = await repo.get_quest_session(db, session_id)
    if not session:
        raise ValueError("Session not found")

    if session.user_id != user_id:
        raise ValueError("Session does not belong to this user")

    if session.status != "in_progress":
        raise ValueError("Quest session is not active")

    quest = get_quest_definition(session.quest_id)
    if not quest:
        raise ValueError("Quest not found")

    step = _find_step(quest, step_id)
    if not step:
        raise ValueError(f"Step '{step_id}' not found")

    # Validate step ID matches current step
    if session.current_step_id != step_id:
        raise ValueError(f"Step '{step_id}' is not the current step (current: {session.current_step_id})")

    # Check for idempotency
    if idempotency_key:
        existing = await repo.get_step_result(db, session_id, step_id)
        if existing and existing.status == "completed" and existing.idempotency_key == idempotency_key:
            # Return cached result
            return QuestAnswerResponse(
                step_id=step_id,
                status=existing.status,
                score=existing.score,
                max_score=existing.max_score,
                correct=existing.correct,
                feedback_key=existing.feedback_key,
                narrative_state=_get_narrative_state(session),
                next_step_id=session.current_step_id,
            )

    # Save answer
    await repo.save_step_answer(db, session_id, step_id, answer, step.step_type)

    # Check retry policy
    step_result = await repo.get_step_result(db, session_id, step_id)
    if step_result:
        retry_count = step_result.retry_count or 0
        if retry_count >= 3:
            raise ValueError("Maximum retry attempts reached for this step")

    # Extract raw value from dict-wrapped answer (API format: {"value": ...})
    raw_answer = answer.get("value") if isinstance(answer, dict) else answer

    # Evaluate
    if step.evaluation_mode == "deterministic":
        evaluation = evaluate_deterministic(
            step.step_type,
            raw_answer,
            step.interaction.model_dump() if hasattr(step.interaction, "model_dump") else dict(step.interaction),
        )
        # Apply step-level consequences
        step_consequence = step.consequences.model_dump() if hasattr(step.consequences, "model_dump") else dict(step.consequences)

        # Apply choice-specific consequences
        if step.step_type in ("single_choice", "decision", "branching", "dialogue"):
            choice_id = raw_answer if raw_answer is not None else str(raw_answer)
            choice_consequence = get_default_consequence(
                step.interaction.model_dump() if hasattr(step.interaction, "model_dump") else dict(step.interaction),
                choice_id,
            )
            if choice_consequence:
                step_consequence.update(choice_consequence)

        evaluation["consequence_updates"] = step_consequence

        # Store idempotency
        if idempotency_key and step_result:
            step_result.idempotency_key = idempotency_key

        await repo.update_step_evaluation(db, session_id, step_id, evaluation)

    elif step.evaluation_mode in ("ai_rubric", "hybrid"):
        # Update to evaluating status
        await repo.update_step_status(db, session_id, step_id, "evaluating")

        correlation_id = str(uuid.uuid4())
        answer_text = answer.get("value") if isinstance(answer, dict) else str(answer)

        # Run AI evaluation with timeout
        try:
            evaluation = await asyncio.wait_for(
                evaluate_with_ai_rubric(
                    answer=answer_text,
                    interaction=step.interaction.model_dump() if hasattr(step.interaction, "model_dump") else dict(step.interaction),
                    locale=locale,
                    attempt_id=session_id,
                    correlation_id=correlation_id,
                ),
                timeout=EVALUATION_TIMEOUT_SECONDS,
            )
            evaluation["consequence_updates"] = {}
            if idempotency_key and step_result:
                step_result.idempotency_key = idempotency_key
            await repo.update_step_evaluation(db, session_id, step_id, evaluation)
        except asyncio.TimeoutError:
            evaluation = {
                "correct": False,
                "score": 0,
                "max_score": 100,
                "feedback_key": "quest.result_ai_timeout",
                "feedback_data": {"error": "Evaluation timed out", "answer_saved": True},
                "evaluation_mode": "ai_rubric",
                "timeout": True,
                "correlation_id": correlation_id,
                "consequence_updates": {},
            }
            await repo.update_step_evaluation(db, session_id, step_id, evaluation)
    else:
        raise ValueError(f"Unknown evaluation mode: {step.evaluation_mode}")

    # Apply consequences to session state
    consequence = evaluation.get("consequence_updates", {})
    _apply_consequence(session, consequence)

    # Mark step as completed
    completed_ids = list(session.completed_step_ids or [])
    if step_id not in completed_ids:
        completed_ids.append(step_id)
    session.completed_step_ids = completed_ids

    # Determine next step
    next_step_id = _determine_next_step(quest, session, step, answer)

    # Check for terminal
    if next_step_id == "__terminal__":
        # Quest is complete - calculate outcome
        outcome_id = _select_outcome(quest, session)
        debrief_data = _build_debrief(quest, session, outcome_id)
        await repo.complete_quest_session(db, session_id, outcome_id, debrief_data)
        return QuestAnswerResponse(
            step_id=step_id,
            status="completed",
            score=evaluation.get("score"),
            max_score=evaluation.get("max_score", 100),
            correct=evaluation.get("correct"),
            feedback_key=evaluation.get("feedback_key"),
            feedback_data=evaluation.get("feedback_data"),
            consequence_updates=consequence,
            narrative_state=_get_narrative_state(session),
            next_step_id="__terminal__",
            evaluation_mode=evaluation.get("evaluation_mode"),
            timed_out=evaluation.get("timeout", False),
            correlation_id=evaluation.get("correlation_id"),
        )

    # Set next step
    session.current_step_id = next_step_id
    await repo.update_quest_session(db, session_id, current_step_id=next_step_id)

    # Create step result for next step
    next_step = _find_step(quest, next_step_id)
    if next_step:
        await repo.create_step_result(db, session_id, next_step_id, next_step.step_type)

    return QuestAnswerResponse(
        step_id=step_id,
        status="completed",
        score=evaluation.get("score"),
        max_score=evaluation.get("max_score", 100),
        correct=evaluation.get("correct"),
        feedback_key=evaluation.get("feedback_key"),
        feedback_data=evaluation.get("feedback_data"),
        consequence_updates=consequence,
        narrative_state=_get_narrative_state(session),
        next_step=next_step,
        next_step_id=next_step_id,
        evaluation_mode=evaluation.get("evaluation_mode"),
        timed_out=evaluation.get("timeout", False),
        correlation_id=evaluation.get("correlation_id"),
    )


async def retry_step_evaluation(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    step_id: str,
    locale: str = "ru-RU",
    idempotency_key: Optional[str] = None,
) -> QuestAnswerResponse:
    """Explicitly retry AI evaluation for a failed/timed-out step."""
    session = await repo.get_quest_session(db, session_id)
    if not session:
        raise ValueError("Session not found")

    if session.user_id != user_id:
        raise ValueError("Session does not belong to this user")

    step_result = await repo.get_step_result(db, session_id, step_id)
    if not step_result:
        raise ValueError("No step result found for retry")

    # Check that step is in retryable state
    if step_result.status not in ("timed_out", "failed"):
        raise ValueError("Step is not in a retryable state")

    # Check retry limit
    if (step_result.retry_count or 0) >= 3:
        raise ValueError("Maximum retry attempts reached")

    # Increment retry count
    await repo.increment_retry_count(db, session_id, step_id)

    # Check idempotency
    if idempotency_key and step_result.idempotency_key == idempotency_key:
        raise ValueError("Duplicate retry blocked by idempotency key")

    # Get the saved answer
    saved_answer = step_result.answer
    if not saved_answer:
        raise ValueError("No saved answer to retry")

    # Re-evaluate with AI
    await repo.update_step_status(db, session_id, step_id, "evaluating")

    answer_text = saved_answer.get("value") if isinstance(saved_answer, dict) else str(saved_answer)
    correlation_id = str(uuid.uuid4())
    quest = get_quest_definition(session.quest_id)
    step = _find_step(quest, step_id) if quest else None

    try:
        evaluation = await asyncio.wait_for(
            evaluate_with_ai_rubric(
                answer=answer_text,
                interaction=step.interaction.model_dump() if step and hasattr(step.interaction, "model_dump") else {},
                locale=locale,
                attempt_id=session_id,
                correlation_id=correlation_id,
            ),
            timeout=EVALUATION_TIMEOUT_SECONDS,
        )
        evaluation["consequence_updates"] = {}
        step_result.idempotency_key = idempotency_key
        await repo.update_step_evaluation(db, session_id, step_id, evaluation)
    except asyncio.TimeoutError:
        evaluation = {
            "correct": False,
            "score": 0,
            "max_score": 100,
            "feedback_key": "quest.result_ai_timeout",
            "feedback_data": {"error": "Evaluation timed out on retry", "answer_saved": True},
            "evaluation_mode": "ai_rubric",
            "timeout": True,
            "correlation_id": correlation_id,
            "consequence_updates": {},
        }
        await repo.update_step_evaluation(db, session_id, step_id, evaluation)

    return QuestAnswerResponse(
        step_id=step_id,
        status="completed" if not evaluation.get("timeout") else "timed_out",
        score=evaluation.get("score"),
        max_score=evaluation.get("max_score", 100),
        correct=evaluation.get("correct"),
        feedback_key=evaluation.get("feedback_key"),
        feedback_data=evaluation.get("feedback_data"),
        narrative_state=_get_narrative_state(session),
        next_step_id=session.current_step_id,
        evaluation_mode=evaluation.get("evaluation_mode"),
        timed_out=evaluation.get("timeout", False),
        correlation_id=evaluation.get("correlation_id"),
    )


async def complete_quest(
    db: AsyncSession,
    session_id: str,
    user_id: str,
) -> QuestOutcomeResponse:
    """Complete the quest session and return outcome + debrief."""
    session = await repo.get_quest_session(db, session_id)
    if not session:
        raise ValueError("Session not found")

    if session.user_id != user_id:
        raise ValueError("Session does not belong to this user")

    quest = get_quest_definition(session.quest_id)
    if not quest:
        raise ValueError("Quest not found")

    outcome_id = _select_outcome(quest, session)
    debrief_data = _build_debrief(quest, session, outcome_id)
    await repo.complete_quest_session(db, session_id, outcome_id, debrief_data)

    outcome = next((o for o in quest.outcomes if o.outcome_id == outcome_id), None)
    return QuestOutcomeResponse(
        session_id=session_id,
        outcome_id=outcome_id,
        outcome_title_key=outcome.title_key if outcome else "",
        outcome_summary_key=outcome.summary_key if outcome else "",
        narrative_state=_get_narrative_state(session),
        debrief=debrief_data,
        status="completed",
    )


async def get_quest_progress(
    db: AsyncSession,
    session_id: str,
    user_id: str,
) -> QuestProgressResponse:
    """Get progress for an existing session (for resume after refresh)."""
    session = await repo.get_quest_session(db, session_id)
    if not session:
        return QuestProgressResponse(session_found=False)

    if session.user_id != user_id:
        return QuestProgressResponse(session_found=False)

    quest = get_quest_definition(session.quest_id)
    if not quest:
        return QuestProgressResponse(session_found=False)

    if session.status == "completed":
        # Return final outcome + debrief
        outcome = next(
            (o for o in quest.outcomes if o.outcome_id == session.selected_outcome_id),
            None,
        )
        return QuestProgressResponse(
            session_found=True,
            session_id=session_id,
            quest=quest,
            narrative_state=_get_narrative_state(session),
            completed_step_ids=session.completed_step_ids or [],
            answers=_get_answers_map(session),
            step_results=_get_step_results_map(session),
            status="completed",
            outcome={
                "outcome_id": session.selected_outcome_id,
                "title_key": outcome.title_key if outcome else "",
                "summary_key": outcome.summary_key if outcome else "",
            },
            debrief=session.debrief_data,
        )

    # In-progress
    step = _find_step(quest, session.current_step_id)
    return QuestProgressResponse(
        session_found=True,
        session_id=session_id,
        quest=quest,
        current_step=step,
        narrative_state=_get_narrative_state(session),
        completed_step_ids=session.completed_step_ids or [],
        answers=_get_answers_map(session),
        step_results=_get_step_results_map(session),
        status=session.status,
    )
