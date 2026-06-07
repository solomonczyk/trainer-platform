"""Domain Pack model — reusable domain pack definition tying all entities together."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, DateTime, String, Text, JSON,
    UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class DomainPack(Base, TimestampMixin):
    """A reusable domain pack definition — no BA/QA hardcoding."""

    __tablename__ = "cert_domain_packs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    domain_pack_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en-US")
    market: Mapped[str] = mapped_column(String(50), default="global")
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    competency_framework_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    blueprint_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    knowledge_source_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    item_bank_policy_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    scoring_policy_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pass_policy_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rubric_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    supported_modes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("domain_pack_id", "version", name="uq_domain_pack_version"),
        Index("idx_dp_status", "status"),
        Index("idx_dp_locale_market", "locale", "market"),
    )
