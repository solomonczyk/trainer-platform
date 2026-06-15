"""REST API router for scenario runtime endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.security import get_current_user_id_required, require_email_verified
from app.db.models import Scenario, TrainerProduct, UserTrainerEnrollment
from app.db.session import get_db
from app.modules.runtime import service as runtime_service
from app.modules.runtime.schemas import (
    CompleteSessionResponse,
    StartScenarioResponse,
    SubmitMessageRequest,
    SubmitMessageResponse,
)

router = APIRouter()


@router.post(
    "/scenarios/{scenario_id}/start",
    response_model=StartScenarioResponse,
    summary="Start a scenario (creates session + attempt)",
)
async def start_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> StartScenarioResponse:
    """Start a scenario by its business scenario_id string.

    Creates a simulation session and an attempt.  Checks the feature flag
    ``ff_scenario_runtime_enabled`` and verifies the user is enrolled in the
    trainer product before allowing the operation.
    """
    # Feature flag check
    if not settings.ff_scenario_runtime_enabled:
        raise ForbiddenError("Scenario runtime is currently disabled")

    # Resolve scenario
    result = await db.execute(
        select(Scenario).where(Scenario.scenario_id == scenario_id)
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise NotFoundError(entity="Scenario", entity_id=scenario_id)

    # Resolve trainer product for enrollment check
    trainer_result = await db.execute(
        select(TrainerProduct).where(TrainerProduct.id == scenario.trainer_product_id)
    )
    trainer = trainer_result.scalar_one_or_none()
    if not trainer:
        raise NotFoundError(entity="TrainerProduct", entity_id=scenario.trainer_product_id)

    # Enrollment check
    enrollment_result = await db.execute(
        select(UserTrainerEnrollment).where(
            UserTrainerEnrollment.user_id == user_id,
            UserTrainerEnrollment.trainer_product_id == scenario.trainer_product_id,
            UserTrainerEnrollment.is_active.is_(True),
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if not enrollment:
        raise ForbiddenError(
            "User is not enrolled in the trainer product required for this scenario"
        )

    session, attempt = await runtime_service.start_scenario(db, user_id, scenario)

    return StartScenarioResponse(
        session_id=session.id,
        attempt_id=attempt.id,
        scenario={
            "scenario_id": scenario.scenario_id,
            "title_key": scenario.title_key,
            "goal_key": scenario.goal_key,
            "difficulty": scenario.difficulty,
            "estimated_duration_minutes": scenario.estimated_duration_minutes,
        },
        status="started",
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SubmitMessageResponse,
    summary="Submit an answer message to an active session",
)
async def submit_message(
    session_id: str,
    body: SubmitMessageRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> SubmitMessageResponse:
    """Save a user answer message for the given session.

    Blocks empty answers and verifies the session belongs to the current user
    and is still active.
    """
    if not settings.ff_scenario_runtime_enabled:
        raise ForbiddenError("Scenario runtime is currently disabled")

    # Validate content is not empty
    if len(body.content.strip()) == 0:
        raise ValidationError("Message content cannot be empty")

    try:
        message = await runtime_service.submit_message(
            db, session_id=session_id, user_id=user_id, content=body.content
        )
    except ValueError as exc:
        raise NotFoundError(str(exc))

    return SubmitMessageResponse(message_id=message.id, status="saved")


@router.post(
    "/sessions/{session_id}/complete",
    response_model=CompleteSessionResponse,
    summary="Complete an attempt (before AI evaluation call)",
)
async def complete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> CompleteSessionResponse:
    """Mark an attempt as completed.

    This endpoint is called *before* the AI evaluation request so the system
    knows the user has finished providing answers.
    """
    if not settings.ff_scenario_runtime_enabled:
        raise ForbiddenError("Scenario runtime is currently disabled")

    try:
        attempt = await runtime_service.complete_session(
            db, session_id=session_id, user_id=user_id
        )
    except ValueError as exc:
        raise NotFoundError(str(exc))

    return CompleteSessionResponse(
        attempt_id=attempt.id,
        status=attempt.status,
        message="Attempt marked as completed",
    )
