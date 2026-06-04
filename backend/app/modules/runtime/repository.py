"""Database access layer for runtime (session / attempt / message) models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Attempt, SimulationMessage, SimulationSession


async def create_session(
    db: AsyncSession, user_id: str, scenario_id: str
) -> SimulationSession:
    """Create a new simulation session."""
    session = SimulationSession(
        user_id=user_id,
        scenario_id=scenario_id,
        status="active",
    )
    db.add(session)
    await db.flush()
    return session


async def create_attempt(
    db: AsyncSession,
    user_id: str,
    scenario_id: str,
    session_id: str,
    trainer_product_id: str,
) -> Attempt:
    """Create a new attempt linked to a session."""
    attempt = Attempt(
        user_id=user_id,
        scenario_id=scenario_id,
        session_id=session_id,
        trainer_product_id=trainer_product_id,
        status="in_progress",
    )
    db.add(attempt)
    await db.flush()
    return attempt


async def create_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    message_type: str = "answer",
) -> SimulationMessage:
    """Persist a simulation message."""
    message = SimulationMessage(
        session_id=session_id,
        role=role,
        content=content,
        message_type=message_type,
    )
    db.add(message)
    await db.flush()
    return message


async def get_messages_by_session(
    db: AsyncSession, session_id: str
) -> list[SimulationMessage]:
    """Return all user messages for a session, ordered by creation time."""
    result = await db.execute(
        select(SimulationMessage)
        .where(
            SimulationMessage.session_id == session_id,
            SimulationMessage.role == "user",
        )
        .order_by(SimulationMessage.created_at.asc())
    )
    return list(result.scalars().all())


async def get_active_session(
    db: AsyncSession, session_id: str, user_id: str
) -> Optional[SimulationSession]:
    """Return an active session that belongs to the given user."""
    result = await db.execute(
        select(SimulationSession).where(
            SimulationSession.id == session_id,
            SimulationSession.user_id == user_id,
            SimulationSession.status == "active",
        )
    )
    return result.scalar_one_or_none()


async def get_attempt_by_session(
    db: AsyncSession, session_id: str
) -> Optional[Attempt]:
    """Return the attempt associated with a session."""
    result = await db.execute(
        select(Attempt).where(Attempt.session_id == session_id)
    )
    return result.scalar_one_or_none()


async def update_attempt_status(
    db: AsyncSession,
    attempt_id: str,
    status: str,
    completed_at: Optional[datetime] = None,
) -> Attempt:
    """Update attempt status and optionally set completed_at."""
    values: dict = {"status": status}
    if completed_at is not None:
        values["completed_at"] = completed_at

    await db.execute(
        update(Attempt).where(Attempt.id == attempt_id).values(**values)
    )
    await db.flush()

    # Re-fetch to return the updated object
    result = await db.execute(select(Attempt).where(Attempt.id == attempt_id))
    updated = result.scalar_one()
    return updated
