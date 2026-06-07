"""Competency Framework and Competency models — hierarchical, versioned, locale/market-bound."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
    UniqueConstraint, Index, CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class CompetencyFramework(Base, TimestampMixin):
    """A versioned competency framework, bound to a domain pack, locale and market."""

    __tablename__ = "cert_competency_frameworks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    framework_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    domain_pack_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True,
    )
    locale: Mapped[str] = mapped_column(String(10), default="en-US")
    market: Mapped[str] = mapped_column(String(50), default="global")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)

    competencies = relationship(
        "Competency", back_populates="framework",
        cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("framework_id", "version", name="uq_competency_framework_version"),
        Index("idx_comp_fw_domain_pack", "domain_pack_id"),
        Index("idx_comp_fw_status", "status"),
    )


class Competency(Base, TimestampMixin):
    """A single competency node within a framework. Supports hierarchy via parent_id."""

    __tablename__ = "cert_competencies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    competency_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    framework_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_competency_frameworks.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("cert_competencies.id"), nullable=True
    )
    cognitive_levels: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    critical: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    framework = relationship("CompetencyFramework", back_populates="competencies")
    children = relationship("Competency", backref="parent", remote_side=[id], lazy="selectin")

    __table_args__ = (
        UniqueConstraint("competency_id", "framework_id", name="uq_competency_per_framework"),
        Index("idx_comp_framework", "framework_id"),
        Index("idx_comp_parent", "parent_id"),
    )
