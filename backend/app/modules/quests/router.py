"""REST API router for quest engine endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError, ConflictError
from app.core.logging import get_logger
from app.core.security import get_current_user_id_required, require_email_verified
from app.db.session import get_db
from app.modules.quests import (
    QuestAnswerRequest,
    QuestAnswerResponse,
    QuestOutcomeResponse,
    QuestProgressResponse,
    QuestStartRequest,
    QuestStartResponse,
    QuestStepResponse,
)
from app.modules.quests.service import (
    complete_quest,
    get_current_step,
    get_quest_progress,
    list_available_quests,
    retry_step_evaluation,
    start_quest,
    submit_and_evaluate_step,
)

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/quests",
    summary="List all available quests",
    description="Returns metadata for all registered quests.",
)
async def list_quests():
    """List available quests with their metadata."""
    return {"quests": list_available_quests()}


@router.post(
    "/quests/{quest_id}/start",
    response_model=QuestStartResponse,
    summary="Start or resume a quest",
)
async def start_quest_endpoint(
    quest_id: str,
    body: QuestStartRequest = QuestStartRequest(),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> QuestStartResponse:
    """Start or resume an immersive quest session."""
    try:
        result = await start_quest(db, user_id, quest_id, body.locale)
        return result
    except ValueError as exc:
        raise NotFoundError(str(exc))


@router.get(
    "/quests/sessions/{session_id}/step",
    response_model=QuestStepResponse,
    summary="Get current step for a quest session",
)
async def get_current_step_endpoint(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> QuestStepResponse:
    """Get the current step with narrative state."""
    try:
        result = await get_current_step(db, session_id)
        return result
    except ValueError as exc:
        raise NotFoundError(str(exc))


@router.post(
    "/quests/sessions/{session_id}/answer",
    response_model=QuestAnswerResponse,
    summary="Submit answer and evaluate for a quest step",
)
async def submit_answer_endpoint(
    session_id: str,
    body: QuestAnswerRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> QuestAnswerResponse:
    """Submit an answer for the current step. Evaluates deterministically or via AI rubric."""
    try:
        result = await submit_and_evaluate_step(
            db,
            session_id=session_id,
            user_id=user_id,
            step_id=body.step_id,
            answer=body.answer,
            locale=body.locale or "ru-RU",
            idempotency_key=body.idempotency_key,
        )
        return result
    except ValueError as exc:
        raise ValidationError(str(exc))


@router.post(
    "/quests/sessions/{session_id}/retry",
    response_model=QuestAnswerResponse,
    summary="Retry evaluation for a failed/timed-out step",
)
async def retry_evaluation_endpoint(
    session_id: str,
    body: QuestAnswerRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> QuestAnswerResponse:
    """Explicitly retry AI evaluation for a failed or timed-out step."""
    try:
        result = await retry_step_evaluation(
            db,
            session_id=session_id,
            user_id=user_id,
            step_id=body.step_id,
            locale=body.locale or "ru-RU",
            idempotency_key=body.idempotency_key,
        )
        return result
    except ValueError as exc:
        raise ValidationError(str(exc))


@router.post(
    "/quests/sessions/{session_id}/complete",
    response_model=QuestOutcomeResponse,
    summary="Complete quest and return outcome + debrief",
)
async def complete_quest_endpoint(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> QuestOutcomeResponse:
    """Complete the quest and receive outcome and educational debrief."""
    try:
        result = await complete_quest(db, session_id, user_id)
        return result
    except ValueError as exc:
        raise NotFoundError(str(exc))


@router.get(
    "/quests/sessions/{session_id}/progress",
    response_model=QuestProgressResponse,
    summary="Get quest progress (for refresh resume)",
)
async def get_quest_progress_endpoint(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> QuestProgressResponse:
    """Get progress for an existing quest session (supports refresh resume)."""
    result = await get_quest_progress(db, session_id, user_id)
    if not result.session_found:
        raise NotFoundError("Session not found")
    return result
