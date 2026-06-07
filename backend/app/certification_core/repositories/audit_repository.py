"""Repository for Audit Event entities — append-only, no update or delete allowed.

All audit event creation must go through AuditService. Neither the repository
nor any generic DAO path may modify or delete existing audit records.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sa_update

from app.certification_core.models.audit_models import AuditEvent
from app.certification_core.repositories.base import CertBaseRepository


class AuditRepository(CertBaseRepository[AuditEvent]):
    """Append-only repository for reading audit events.

    Raises RuntimeError on any mutation attempt to enforce append-only policy.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditEvent)

    # ------------------------------------------------------------------ #
    # Append-only guard — all mutation methods are blocked
    # ------------------------------------------------------------------ #

    async def create(self, **kwargs) -> AuditEvent:
        """Blocked: use AuditService.record() instead."""
        raise RuntimeError(
            "AuditRepository is append-only. "
            "Use AuditService.record() to create audit events."
        )

    async def update_entity(self, entity_id: str, **kwargs) -> Optional[AuditEvent]:
        """Blocked: audit events are immutable."""
        raise RuntimeError(
            "AuditRepository is append-only. "
            "Audit events cannot be updated."
        )

    async def soft_delete(self, entity_id: str, **kwargs) -> Optional[AuditEvent]:
        """Blocked: audit events cannot be deleted."""
        raise RuntimeError(
            "AuditRepository is append-only. "
            "Audit events cannot be deleted."
        )
