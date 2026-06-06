"""REST endpoints for admin operations.

All endpoints are protected by the ``require_admin`` dependency.
"""

from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.session import get_db
from app.modules.admin.schemas import (
    AdminAnalyticsSanityResponse,
    SeedStatusResponse,
    SystemHealthResponse,
    InlineSeedRequest,
)
from app.modules.admin.ba_phase2_seed import seed_ba_phase2
from app.modules.admin.ba_trainer_seed import seed_ba_trainer
from app.modules.admin.service import AdminService

router = APIRouter(tags=["Admin"])


@router.get("/seed-status", response_model=SeedStatusResponse)
async def seed_status(
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SeedStatusResponse:
    """Return row counts from all major seeded tables."""
    counts = await AdminService.get_seed_status(db)
    return SeedStatusResponse(**counts)


@router.get("/system-health", response_model=SystemHealthResponse)
async def system_health(
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SystemHealthResponse:
    """Return system health including database connectivity and module statuses."""
    health = await AdminService.get_system_health(db)
    return SystemHealthResponse(**health)


@router.get("/evaluations/failures")
async def evaluation_failures(
    limit: int = Query(default=50, ge=1, le=200),
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Return a list of failed evaluations (raw answer data excluded).

    Controlled by the ``limit`` query parameter (max 200).
    """
    return await AdminService.get_evaluation_failures(db, limit)


@router.get("/analytics/sanity", response_model=AdminAnalyticsSanityResponse)
async def analytics_sanity(
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminAnalyticsSanityResponse:
    """Return total analytics event count and a breakdown by event type."""
    sanity = await AdminService.get_analytics_sanity(db)
    return AdminAnalyticsSanityResponse(**sanity)


@router.post("/seed/ba-trainer")
async def seed_ba_trainer_endpoint(
    body: Optional[InlineSeedRequest] = Body(default=None),
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Seed the BA trainer package data into the database.

    When the server has no local file access (e.g. Railway Docker),
    pass ``trainer_data``, ``modules_data``, ``activities_data``, and
    ``locale_data`` as inline JSON in the request body.
    """
    results = await seed_ba_trainer(db, inline=body)
    return {"status": "ok", "results": results}


@router.post("/seed/ba-trainer-phase2")
async def seed_ba_trainer_phase2_endpoint(
    body: Optional[InlineSeedRequest] = Body(default=None),
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Seed BA Phase 2 scenarios and rubrics into the database.

    When the server has no local file access (e.g. Railway Docker),
    pass ``scenarios_data`` and ``rubrics_data`` as inline JSON
    in the request body.
    """
    results = await seed_ba_phase2(db, inline=body)
    return {"status": "ok", "results": results}
