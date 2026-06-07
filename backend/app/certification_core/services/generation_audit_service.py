"""Generation audit service — generates audit events for the generation pipeline."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.audit_models import AuditEvent
from app.core.logging import get_logger

logger = get_logger(__name__)


class GenerationAuditService:
    """Audit service for generation pipeline events."""

    AUDIT_ACTIONS = {
        "generation_request_created",
        "generation_request_authorized",
        "generation_started",
        "provider_call_completed",
        "provider_call_failed",
        "candidate_normalized",
        "candidate_schema_failed",
        "candidate_validation_started",
        "candidate_validator_completed",
        "candidate_validation_failed",
        "candidate_rejected",
        "candidate_review_handoff_created",
        "generation_request_completed",
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(
        self,
        action: str,
        actor_id: str,
        actor_role: str,
        resource_type: str,
        resource_id: str,
        reason: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> AuditEvent:
        """Record an audit event."""
        if action not in self.AUDIT_ACTIONS:
            logger.warning(f"Unknown audit action: {action}")

        event = AuditEvent(
            audit_event_id=f"aud-gen-{uuid.uuid4().hex[:12]}",
            entity_type=resource_type,
            entity_id=resource_id,
            action=action,
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason or action,
            before_hash=None,
            after_hash=None,
            entity_version=None,
        )
        self.db.add(event)
        await self.db.flush()

        logger.info(
            "Generation audit event",
            action=action,
            actor=actor_id,
            resource=resource_type,
            resource_id=resource_id,
        )
        return event
