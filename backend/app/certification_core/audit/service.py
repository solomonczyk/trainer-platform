"""Append-only audit service — records all certification-core mutations."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.audit_models import AuditEvent


def _compute_hash(data: dict) -> str:
    """Compute a SHA-256 hash of a dictionary for before/after comparison."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class AuditService:
    """Append-only audit service. All mutation methods create immutable audit records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        reason: Optional[str] = None,
        entity_version: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
    ) -> AuditEvent:
        """Record an audit event for any entity mutation."""
        audit_event_id = f"aud-{uuid.uuid4().hex[:12]}"
        before_hash = _compute_hash(before_state) if before_state else None
        after_hash = _compute_hash(after_state) if after_state else None

        event = AuditEvent(
            audit_event_id=audit_event_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_version=entity_version,
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason,
            before_hash=before_hash,
            after_hash=after_hash,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def record_create(
        self,
        entity_type: str,
        entity_id: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        after_state: Optional[dict] = None,
        reason: Optional[str] = None,
    ) -> AuditEvent:
        """Record a 'create' event."""
        return await self.record(
            entity_type=entity_type,
            entity_id=entity_id,
            action="create",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason or "Entity created",
            after_state=after_state,
        )

    async def record_update(
        self,
        entity_type: str,
        entity_id: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        reason: Optional[str] = None,
        entity_version: Optional[str] = None,
    ) -> AuditEvent:
        """Record an 'update' event."""
        return await self.record(
            entity_type=entity_type,
            entity_id=entity_id,
            action="update",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason or "Entity updated",
            entity_version=entity_version,
            before_state=before_state,
            after_state=after_state,
        )

    async def record_transition(
        self,
        entity_type: str,
        entity_id: str,
        from_status: str,
        to_status: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> AuditEvent:
        """Record a lifecycle status transition."""
        return await self.record(
            entity_type=entity_type,
            entity_id=entity_id,
            action=f"transition:{from_status}->{to_status}",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason or f"Status transition from {from_status} to {to_status}",
        )

    async def record_delete(
        self,
        entity_type: str,
        entity_id: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        before_state: Optional[dict] = None,
        reason: Optional[str] = None,
    ) -> AuditEvent:
        """Record a soft-delete/retire event."""
        return await self.record(
            entity_type=entity_type,
            entity_id=entity_id,
            action="delete",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason or "Entity deleted/retired",
            before_state=before_state,
        )

    async def query(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditEvent], int]:
        """Query audit events with filters."""
        query = select(AuditEvent)
        count_query = select(func.count(AuditEvent.id))

        if entity_type:
            query = query.where(AuditEvent.entity_type == entity_type)
            count_query = count_query.where(AuditEvent.entity_type == entity_type)
        if entity_id:
            query = query.where(AuditEvent.entity_id == entity_id)
            count_query = count_query.where(AuditEvent.entity_id == entity_id)
        if actor_id:
            query = query.where(AuditEvent.actor_id == actor_id)
            count_query = count_query.where(AuditEvent.actor_id == actor_id)
        if action:
            query = query.where(AuditEvent.action == action)
            count_query = count_query.where(AuditEvent.action == action)
        if date_from:
            query = query.where(AuditEvent.event_timestamp >= date_from)
            count_query = count_query.where(AuditEvent.event_timestamp >= date_from)
        if date_to:
            query = query.where(AuditEvent.event_timestamp <= date_to)
            count_query = count_query.where(AuditEvent.event_timestamp <= date_to)

        query = query.order_by(AuditEvent.event_timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        count_result = await self.db.execute(count_query)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return list(items), total
