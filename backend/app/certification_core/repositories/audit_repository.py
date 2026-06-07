"""Repository for Audit Event entities — specialized for query-only access."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.audit_models import AuditEvent
from app.certification_core.repositories.base import CertBaseRepository


class AuditRepository(CertBaseRepository[AuditEvent]):
    """Repository for reading audit events (create is handled by AuditService)."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditEvent)
