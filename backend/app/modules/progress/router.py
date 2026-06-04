"""REST endpoints for user progress."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.security import get_current_user_id_required
from app.db.session import get_db
from app.modules.progress.schemas import (
    AllProgressResponse,
    ProgressSummaryResponse,
)
from app.modules.progress.service import ProgressService

router = APIRouter(prefix="/me", tags=["Progress"])


@router.get("/progress", response_model=AllProgressResponse)
async def list_progress(
    user_id: str = Depends(get_current_user_id_required),
    db: AsyncSession = Depends(get_db),
) -> AllProgressResponse:
    """List progress summaries for all trainers the current user has attempted."""
    progress_list = await ProgressService.get_all_progress(db, user_id)
    return AllProgressResponse(progress_list=progress_list)


@router.get("/progress/{trainer_slug}", response_model=ProgressSummaryResponse)
async def get_progress_for_trainer(
    trainer_slug: str,
    user_id: str = Depends(get_current_user_id_required),
    db: AsyncSession = Depends(get_db),
) -> ProgressSummaryResponse:
    """Return progress for a single trainer identified by its slug."""
    progress = await ProgressService.get_trainer_progress(db, user_id, trainer_slug)
    if progress is None:
        raise NotFoundError("Progress", trainer_slug)
    return ProgressSummaryResponse(**progress)
