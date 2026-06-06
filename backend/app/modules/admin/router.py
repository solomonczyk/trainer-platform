"""REST endpoints for admin operations.

All endpoints are protected by the ``require_admin`` dependency.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.session import get_db
from app.modules.admin.schemas import (
    AdminAnalyticsSanityResponse,
    SeedStatusResponse,
    SystemHealthResponse,
)
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
    admin_id: str = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Seed the BA trainer package data into the database."""
    results = await seed_ba_trainer(db)
    return {"status": "ok", "results": results}
