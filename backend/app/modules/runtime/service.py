"""Business logic for scenario runtime operations."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Scenario
from app.modules.runtime import repository as runtime_repo


async def start_scenario(
    db: AsyncSession,
    user_id: str,
    scenario: Scenario,
) -> tuple:
    """Create a simulation session and an attempt for the given user and scenario.

    Returns (SimulationSession, Attempt).
    """
    session = await runtime_repo.create_session(
        db, user_id=user_id, scenario_id=scenario.id
    )
    attempt = await runtime_repo.create_attempt(
        db,
        user_id=user_id,
        scenario_id=scenario.id,
        session_id=session.id,
        trainer_product_id=scenario.trainer_product_id,
    )
    return session, attempt


async def submit_message(
    db: AsyncSession,
    session_id: str,
    user_id: str,
    content: str,
) -> object:
    """Validate the active session and persist a user message.

    Returns the created SimulationMessage.
    """
    session = await runtime_repo.get_active_session(db, session_id, user_id)
    if not session:
        raise ValueError("Active session not found or does not belong to user")

    message = await runtime_repo.create_message(
        db, session_id=session_id, role="user", content=content
    )
    return message


async def complete_session(
    db: AsyncSession,
    session_id: str,
    user_id: str,
) -> object:
    """Mark the attempt associated with a session as completed.

    Collects user messages and stores them as the attempt's answer_text
    before marking the attempt as completed.

    Returns the updated Attempt.
    """
    session = await runtime_repo.get_active_session(db, session_id, user_id)
    if not session:
        raise ValueError("Active session not found or does not belong to user")

    attempt = await runtime_repo.get_attempt_by_session(db, session_id)
    if not attempt:
        raise ValueError("No attempt found for this session")

    # Collect user messages and store as answer_text
    messages = await runtime_repo.get_messages_by_session(db, session_id)
    if messages:
        answer_text = "\n\n".join(m.content for m in messages)
        attempt.answer_text = answer_text

    now = datetime.now(timezone.utc)
    attempt = await runtime_repo.update_attempt_status(
        db, attempt_id=attempt.id, status="completed", completed_at=now
    )
    return attempt
