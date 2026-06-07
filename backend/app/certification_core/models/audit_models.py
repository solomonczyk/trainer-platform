"""Audit Event model — append-only audit trail for all certification-core mutations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, DateTime, String, Text, JSON, Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class AuditEvent(Base, TimestampMixin):
    """Immutable, append-only audit event for certification-core entity mutations."""

    __tablename__ = "cert_audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    audit_event_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    before_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    after_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_actor", "actor_id"),
        Index("idx_audit_timestamp", "event_timestamp"),
        Index("idx_audit_action", "action"),
    )
