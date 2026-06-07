"""Exam Blueprint models — versioned blueprints with sections, weights, and difficulty distributions."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
    UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class ExamBlueprint(Base, TimestampMixin):
    """A versioned exam blueprint defining assessment structure, sections and pass policy."""

    __tablename__ = "cert_exam_blueprints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    blueprint_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    domain_pack_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    competency_framework_version: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True,
    )
    exam_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    pass_policy_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sections = relationship(
        "BlueprintSection", back_populates="blueprint",
        cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("blueprint_id", "version", name="uq_blueprint_version"),
        Index("idx_bp_domain_pack", "domain_pack_id"),
        Index("idx_bp_status", "status"),
    )


class BlueprintSection(Base, TimestampMixin):
    """A section within an exam blueprint — maps to competencies with weight and difficulty."""

    __tablename__ = "cert_blueprint_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    blueprint_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_exam_blueprints.id"), nullable=False
    )
    section_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    competency_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=False)
    weight_percent: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_items: Mapped[int] = mapped_column(Integer, default=0)
    maximum_items: Mapped[int] = mapped_column(Integer, default=0)
    difficulty_distribution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    cognitive_distribution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    critical_section: Mapped[bool] = mapped_column(default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    blueprint = relationship("ExamBlueprint", back_populates="sections")

    __table_args__ = (
        UniqueConstraint("blueprint_id", "section_id", name="uq_blueprint_section"),
        Index("idx_bp_section_blueprint", "blueprint_id"),
    )
