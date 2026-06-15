"""REST endpoints for deterministic activities."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.security import get_current_user_id_required, require_email_verified
from app.db.session import get_db
from app.modules.activities.schemas import (
    ActivityStartResponse,
    ActivitySubmitRequest,
    ActivitySubmitResponse,
    ModuleActivitiesResponse,
)
from app.modules.activities.service import ActivityService
from app.modules.trainers.repository import get_by_slug

router = APIRouter(tags=["Activities"])


@router.get(
    "/trainers/{trainer_slug}/modules/{module_id}/activities",
    response_model=ModuleActivitiesResponse,
    summary="List activities in a module (no correct answers exposed)",
)
async def list_module_activities(
    trainer_slug: str,
    module_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> ModuleActivitiesResponse:
    """Return public activity list for a module. Correct answers are NOT included."""
    trainer = await get_by_slug(db, trainer_slug)
    if not trainer:
        raise NotFoundError("Trainer", trainer_slug)

    activities = await ActivityService.get_module_activities(
        db, trainer.id, module_id
    )

    return ModuleActivitiesResponse(
        module_id=module_id,
        activities=activities,
        total_count=len(activities),
    )


@router.get(
    "/trainers/{trainer_slug}/activities/{activity_id}/start",
    response_model=ActivityStartResponse,
    summary="Start an activity — get prompt without correct answers",
)
async def start_activity(
    trainer_slug: str,
    activity_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> ActivityStartResponse:
    """Start a specific activity and receive its prompt (no correct answers)."""
    trainer = await get_by_slug(db, trainer_slug)
    if not trainer:
        raise NotFoundError("Trainer", trainer_slug)

    return await ActivityService.start_activity(db, activity_id, user_id)


@router.post(
    "/trainers/{trainer_slug}/activities/submit",
    response_model=ActivitySubmitResponse,
    summary="Submit an activity answer for deterministic validation",
)
async def submit_activity(
    trainer_slug: str,
    body: ActivitySubmitRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> ActivitySubmitResponse:
    """Submit an answer for deterministic validation.

    The submitted answer is validated server-side against the stored correct answer.
    Frontend cannot self-award a pass — the server determines the result.
    """
    trainer = await get_by_slug(db, trainer_slug)
    if not trainer:
        raise NotFoundError("Trainer", trainer_slug)

    return await ActivityService.submit_activity(
        db=db,
        activity_id=body.activity_id,
        user_id=user_id,
        submitted_answer=body.answer,
        idempotency_key=body.idempotency_key,
    )
