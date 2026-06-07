"""API routes for Audit Event querying."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from app.certification_core.schemas.audit_schemas import (
    AuditEventResponse, AuditEventListResponse,
)
from app.certification_core.audit.service import AuditService
from app.certification_core.services.authorization import (
    require_certification_permission,
)
from app.db.session import get_db

router = APIRouter(prefix="/certification-core/audit", tags=["Certification-Core"])


@router.get("", response_model=AuditEventListResponse)
async def query_audit(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role: str = Depends(lambda: require_certification_permission("certification:audit:read")),
    db: AsyncSession = Depends(get_db),
):
    """Query audit events with filters. Requires audit:read permission."""
    audit = AuditService(db)
    items, total = await audit.query(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        action=action,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return AuditEventListResponse(
        items=[AuditEventResponse.model_validate(e) for e in items],
        total=total, skip=skip, limit=limit,
    )
