"""Database repository for quest engine operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.db.models import QuestSession, QuestStepResult

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# QuestSession CRUD
# ---------------------------------------------------------------------------


async def create_quest_session(
    db: AsyncSession,
    user_id: str,
    quest_id: str,
    trainer_slug: str,
    locale: str = "ru-RU",
    initial_state: Optional[dict[str, Any]] = None,
) -> QuestSession:
    """Create a new quest session."""
    state = initial_state or {}
    session = QuestSession(
        user_id=user_id,
        quest_id=quest_id,
        trainer_slug=trainer_slug,
        locale=locale,
        status="in_progress",
        risk=state.get("risk", 0),
        time_remaining=state.get("time_remaining", 100),
        team_trust=state.get("team_trust", 100),
        client_trust=state.get("client_trust", 100),
        evidence_quality=state.get("evidence_quality", 0),
        decision_quality=state.get("decision_quality", 0),
        flags={},
        completed_step_ids=[],
        visited_branch_ids=[],
    )
    db.add(session)
    await db.flush()
    logger.info("Quest session created", quest_session_id=session.id, quest_id=quest_id)
    return session


async def get_quest_session(
    db: AsyncSession,
    session_id: str,
) -> Optional[QuestSession]:
    """Fetch a quest session by ID with step results."""
    stmt = (
        select(QuestSession)
        .where(QuestSession.id == session_id)
        .options(selectinload(QuestSession.step_results))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_active_quest_session(
    db: AsyncSession,
    user_id: str,
    quest_id: str,
) -> Optional[QuestSession]:
    """Fetch the active (in_progress) session for a user+quest."""
    stmt = (
        select(QuestSession)
        .where(
            QuestSession.user_id == user_id,
            QuestSession.quest_id == quest_id,
            QuestSession.status == "in_progress",
        )
        .options(selectinload(QuestSession.step_results))
        .order_by(QuestSession.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_quest_session(
    db: AsyncSession,
    session_id: str,
    **kwargs,
) -> Optional[QuestSession]:
    """Update quest session fields."""
    session = await get_quest_session(db, session_id)
    if not session:
        return None
    for key, value in kwargs.items():
        if hasattr(session, key) and value is not None:
            setattr(session, key, value)
    await db.flush()
    return session


async def complete_quest_session(
    db: AsyncSession,
    session_id: str,
    outcome_id: str,
    debrief_data: Optional[dict] = None,
) -> Optional[QuestSession]:
    """Mark a quest session as completed with outcome."""
    session = await get_quest_session(db, session_id)
    if not session:
        return None
    session.status = "completed"
    session.selected_outcome_id = outcome_id
    if debrief_data:
        session.debrief_data = debrief_data
    session.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return session


# ---------------------------------------------------------------------------
# QuestStepResult CRUD
# ---------------------------------------------------------------------------


async def create_step_result(
    db: AsyncSession,
    quest_session_id: str,
    step_id: str,
    step_type: Optional[str] = None,
) -> QuestStepResult:
    """Create a step result record."""
    result = QuestStepResult(
        quest_session_id=quest_session_id,
        step_id=step_id,
        step_type=step_type,
        status="pending",
    )
    db.add(result)
    await db.flush()
    return result


async def get_step_result(
    db: AsyncSession,
    quest_session_id: str,
    step_id: str,
) -> Optional[QuestStepResult]:
    """Fetch step result for a given step in a session."""
    stmt = select(QuestStepResult).where(
        QuestStepResult.quest_session_id == quest_session_id,
        QuestStepResult.step_id == step_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def save_step_answer(
    db: AsyncSession,
    quest_session_id: str,
    step_id: str,
    answer: Any,
    step_type: Optional[str] = None,
) -> QuestStepResult:
    """Save or update a step answer."""
    existing = await get_step_result(db, quest_session_id, step_id)
    if existing:
        existing.answer = answer if isinstance(answer, dict) else {"value": answer}
        existing.status = "answered"
        if step_type:
            existing.step_type = step_type
        await db.flush()
        return existing

    result = QuestStepResult(
        quest_session_id=quest_session_id,
        step_id=step_id,
        step_type=step_type,
        answer=answer if isinstance(answer, dict) else {"value": answer},
        status="answered",
    )
    db.add(result)
    await db.flush()
    return result


async def update_step_evaluation(
    db: AsyncSession,
    quest_session_id: str,
    step_id: str,
    evaluation_result: dict[str, Any],
) -> Optional[QuestStepResult]:
    """Update step result with evaluation data."""
    result = await get_step_result(db, quest_session_id, step_id)
    if not result:
        logger.warning("Step result not found for update", step_id=step_id)
        return None

    score = evaluation_result.get("score")
    max_score = evaluation_result.get("max_score", 100)
    correct = evaluation_result.get("correct")
    feedback_key = evaluation_result.get("feedback_key")
    feedback_data = evaluation_result.get("feedback_data")
    consequence_updates = evaluation_result.get("consequence_updates")
    evaluation_mode = evaluation_result.get("evaluation_mode", "deterministic")
    timed_out = evaluation_result.get("timeout", False)

    result.status = "completed" if not timed_out else "timed_out"
    result.evaluation_mode = evaluation_mode
    result.score = score
    result.max_score = max_score
    result.correct = correct
    result.feedback_key = feedback_key
    result.feedback_data = feedback_data
    result.consequence_updates = consequence_updates
    result.timed_out = timed_out
    result.provider = evaluation_result.get("provider")
    result.provider_model = evaluation_result.get("provider_model")
    result.ai_latency_ms = evaluation_result.get("latency_ms")
    result.ai_cost_usd = evaluation_result.get("cost")
    result.correlation_id = evaluation_result.get("correlation_id")

    await db.flush()
    return result


async def update_step_status(
    db: AsyncSession,
    quest_session_id: str,
    step_id: str,
    status: str,
) -> Optional[QuestStepResult]:
    """Update step result status."""
    result = await get_step_result(db, quest_session_id, step_id)
    if not result:
        return None
    result.status = status
    await db.flush()
    return result


async def increment_retry_count(
    db: AsyncSession,
    quest_session_id: str,
    step_id: str,
) -> Optional[QuestStepResult]:
    """Increment retry count for a step."""
    result = await get_step_result(db, quest_session_id, step_id)
    if not result:
        return None
    result.retry_count = (result.retry_count or 0) + 1
    await db.flush()
    return result
