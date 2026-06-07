"""Dynamic Item Bank models — item families, items, and versioned item history."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
    UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class ItemFamily(Base, TimestampMixin):
    """An item family defines the invariant skill, template schema, and variant policy."""

    __tablename__ = "cert_item_families"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    family_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    domain_pack_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    allowed_item_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    competency_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    variant_policy: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True,
    )
    locale: Mapped[str] = mapped_column(String(10), default="en-US")
    market: Mapped[str] = mapped_column(String(50), default="global")
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)

    items = relationship("Item", back_populates="family", lazy="selectin")

    __table_args__ = (
        Index("idx_if_domain_pack", "domain_pack_id"),
        Index("idx_if_status", "status"),
    )


class Item(Base, TimestampMixin):
    """A single item (question/scenario) in the dynamic item bank with full provenance."""

    __tablename__ = "cert_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    item_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    item_family_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("cert_item_families.id"), nullable=True, index=True
    )
    domain_pack_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_contract: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    answer_key: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    rubric_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    competency_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    knowledge_source_refs: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    difficulty_target: Mapped[str] = mapped_column(String(20), default="medium")
    difficulty_measured: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    discrimination_measured: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default="draft", index=True,
    )
    locale: Mapped[str] = mapped_column(String(10), default="en-US")
    market: Mapped[str] = mapped_column(String(50), default="global")
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    exposure_count: Mapped[int] = mapped_column(Integer, default=0)
    compromise_risk: Mapped[str] = mapped_column(String(20), default="low")

    family = relationship("ItemFamily", back_populates="items", lazy="selectin")
    versions = relationship(
        "ItemVersion", back_populates="item",
        cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_item_domain_pack", "domain_pack_id"),
        Index("idx_item_status", "status"),
        Index("idx_item_family", "item_family_id"),
        Index("idx_item_difficulty", "difficulty_target"),
    )


class ItemVersion(Base, TimestampMixin):
    """Immutable version snapshot of an item — created on publish or significant update."""

    __tablename__ = "cert_item_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cert_items.id"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    change_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)

    item = relationship("Item", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("item_id", "version", name="uq_item_version"),
    )
