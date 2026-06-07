"""Rubric Versioning models — versioned rubrics with weighted criteria and scoring levels."""

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


class CertRubric(Base, TimestampMixin):
    """A versioned rubric defining evaluation criteria, weights, and scoring levels."""

    __tablename__ = "cert_rubrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    rubric_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    domain_pack_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    competency_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_weight: Mapped[float] = mapped_column(Float, default=100.0)
    validation_dataset_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)

    criteria = relationship(
        "CertRubricCriterion", back_populates="rubric",
        cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("rubric_id", "version", name="uq_rubric_version"),
        Index("idx_rubric_domain_pack", "domain_pack_id"),
        Index("idx_rubric_status", "status"),
    )


class CertRubricCriterion(Base, TimestampMixin):
    """A single criterion within a rubric with weight and scoring levels."""

    __tablename__ = "cert_rubric_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    rubric_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_rubrics.id"), nullable=False
    )
    criterion_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    levels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    rubric = relationship("CertRubric", back_populates="criteria")

    __table_args__ = (
        UniqueConstraint("rubric_id", "criterion_id", name="uq_rubric_criterion"),
    )
