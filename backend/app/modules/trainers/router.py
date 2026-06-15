"""Router for the Trainers module."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import NotFoundError
from app.core.security import require_email_verified
from app.db.session import get_db
from app.modules.trainers.schemas import TrainerDetailResponse, EnrollResponse
from app.modules.trainers.service import get_trainer_by_slug, enroll_user

router = APIRouter()


@router.get(
    "/trainers/{trainer_slug}",
    response_model=TrainerDetailResponse,
)
async def get_trainer(
    trainer_slug: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> TrainerDetailResponse:
    """Return full trainer detail, scenario count, and enrollment status."""
    # Feature flag: hide QA interview trainer unless enabled
    if (
        trainer_slug == "qa-engineer-interview-trainer"
        and not settings.ff_trainer_qa_interview_visible
    ):
        raise NotFoundError("Trainer", trainer_slug)

    trainer_data = await get_trainer_by_slug(db, trainer_slug, user_id)
    if not trainer_data:
        raise NotFoundError("Trainer", trainer_slug)

    return TrainerDetailResponse(**trainer_data)


@router.post(
    "/trainers/{trainer_slug}/enroll",
    response_model=EnrollResponse,
    status_code=201,
)
async def enroll_in_trainer(
    trainer_slug: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_email_verified),
) -> EnrollResponse:
    """Enroll the current user in a trainer. Idempotent."""
    trainer_data = await get_trainer_by_slug(db, trainer_slug)
    if not trainer_data:
        raise NotFoundError("Trainer", trainer_slug)

    enrollment, created = await enroll_user(db, user_id, trainer_data["id"])

    return EnrollResponse(
        enrollment_id=enrollment.id,
        status="enrolled" if created else "already_enrolled",
        message=(
            "Enrolled successfully"
            if created
            else "Already enrolled in this trainer"
        ),
    )
