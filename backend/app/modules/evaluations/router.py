"""FastAPI router for the evaluations module.

Endpoints:

* ``POST /api/v1/attempts/{attempt_id}/evaluate`` — trigger AI evaluation
* ``GET /api/v1/attempts/{attempt_id}/evaluation`` — retrieve evaluation result
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ForbiddenError
from app.core.logging import get_logger
from app.core.security import get_current_user_id_required, require_email_verified
from app.db.session import get_db
from app.modules.evaluations.schemas import (
    EvaluationErrorResponse,
    EvaluationResponse,
    EvaluationTriggerResponse,
    EvaluateRequest,
)
from app.modules.evaluations.service import EvaluationService

logger = get_logger(__name__)

router = APIRouter()


def _check_evaluation_feature_flag() -> None:
    """Raise ForbiddenError if the AI evaluation feature flag is disabled."""
    if not settings.ff_ai_evaluation_enabled:
        raise ForbiddenError("AI evaluation is currently disabled")


@router.post(
    "/attempts/{attempt_id}/evaluate",
    response_model=EvaluationResponse,
    responses={
        403: {"model": EvaluationErrorResponse},
        404: {"model": EvaluationErrorResponse},
        422: {"model": EvaluationErrorResponse},
    },
    summary="Trigger AI evaluation for an attempt",
    description=(
        "Triggers an AI-based evaluation of a user's attempt. "
        "The evaluation processes the user's answer against the scenario rubric "
        "and returns the evaluation result after completion."
    ),
)
async def trigger_evaluation(
    attempt_id: str,
    body: EvaluateRequest = EvaluateRequest(),
    db: AsyncSession = Depends(get_db),
) -> EvaluationResponse:
    """Trigger evaluation of the specified attempt."""
    _check_evaluation_feature_flag()

    service = EvaluationService()
    evaluation = await service.evaluate_attempt(
        db=db,
        attempt_id=attempt_id,
        locale=body.locale,
    )

    logger.info(
        "Evaluation completed",
        attempt_id=attempt_id,
        overall_score=evaluation.overall_score,
        passed=evaluation.passed,
    )

    return evaluation


@router.get(
    "/attempts/{attempt_id}/evaluation",
    response_model=EvaluationResponse,
    responses={
        403: {"model": EvaluationErrorResponse},
        404: {"model": EvaluationErrorResponse},
    },
    summary="Get evaluation result for an attempt",
    description=(
        "Retrieves the stored evaluation result for a given attempt, "
        "including per-criterion scores, evidence, strengths, and weaknesses."
    ),
)
async def get_evaluation(
    attempt_id: str,
    user_id: str = Depends(require_email_verified),
    db: AsyncSession = Depends(get_db),
) -> EvaluationResponse:
    """Retrieve the evaluation result for an attempt."""
    _check_evaluation_feature_flag()

    service = EvaluationService()
    return await service.get_evaluation(db=db, attempt_id=attempt_id, user_id=user_id)
