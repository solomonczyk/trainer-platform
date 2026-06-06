"""All database models for Trainer Platform MVP."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON, Enum as SAEnum,
    UniqueConstraint, Index, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin, generate_uuid


# ---------------------------------------------------------------------------
# Auth / Users
# ---------------------------------------------------------------------------

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="registered_user")  # guest, registered_user, admin, system_service
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    enrollments = relationship("UserTrainerEnrollment", back_populates="user")
    sessions = relationship("SimulationSession", back_populates="user")
    attempts = relationship("Attempt", back_populates="user")
    progress_records = relationship("TrainerProgress", back_populates="user")
    analytics_events = relationship("AnalyticsEvent", back_populates="user")


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_locale: Mapped[str] = mapped_column(String(10), default="ru-RU")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="profile")


# ---------------------------------------------------------------------------
# Domains
# ---------------------------------------------------------------------------

class Domain(Base, TimestampMixin):
    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    trainers = relationship("TrainerProduct", back_populates="domain")


# ---------------------------------------------------------------------------
# Trainer Products
# ---------------------------------------------------------------------------

class TrainerProduct(Base, TimestampMixin):
    __tablename__ = "trainer_products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    trainer_product_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    domain_id: Mapped[str] = mapped_column(String(36), ForeignKey("domains.id"), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(50), default="interview_simulator")
    target_audience: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    default_locale: Mapped[str] = mapped_column(String(10), default="ru-RU")
    supported_locales: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="published_seed")
    owner: Mapped[str] = mapped_column(String(50), default="platform")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    domain = relationship("Domain", back_populates="trainers")
    versions = relationship("TrainerVersion", back_populates="trainer")
    localizations = relationship("TrainerLocalization", back_populates="trainer")
    enrollments = relationship("UserTrainerEnrollment", back_populates="trainer")
    progress_records = relationship("TrainerProgress", back_populates="trainer")
    scenarios = relationship("Scenario", back_populates="trainer")


class TrainerVersion(Base, TimestampMixin):
    __tablename__ = "trainer_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    release_status: Mapped[str] = mapped_column(String(50), default="mvp_seed")
    skill_map_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rubric_pack_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    scenario_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    locale_pack_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    requires_expert_review: Mapped[bool] = mapped_column(Boolean, default=False)

    trainer = relationship("TrainerProduct", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("trainer_product_id", "version", name="uq_trainer_version"),
    )


class TrainerLocalization(Base, TimestampMixin):
    __tablename__ = "trainer_localizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    locale: Mapped[str] = mapped_column(String(10), nullable=False)
    strings: Mapped[dict] = mapped_column(JSON, nullable=False)

    trainer = relationship("TrainerProduct", back_populates="localizations")

    __table_args__ = (
        UniqueConstraint("trainer_product_id", "locale", name="uq_trainer_locale"),
    )


# ---------------------------------------------------------------------------
# Tracks / Modules
# ---------------------------------------------------------------------------

class Track(Base, TimestampMixin):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class Module(Base, TimestampMixin):
    __tablename__ = "modules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    track_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tracks.id"), nullable=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

class Scenario(Base, TimestampMixin):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    scenario_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    title_key: Mapped[str] = mapped_column(String(255), nullable=False)
    goal_key: Mapped[str] = mapped_column(String(255), nullable=False)
    trainer_version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    track: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    module: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="junior_basic")
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=8)
    target_skills: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    user_role: Mapped[str] = mapped_column(String(50), default="candidate")
    ai_role: Mapped[str] = mapped_column(String(50), default="interviewer")
    rubric_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    steps: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    common_errors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    critical_errors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    hints: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="published_seed")

    trainer = relationship("TrainerProduct", back_populates="scenarios")
    attempts = relationship("Attempt", back_populates="scenario")
    rubric = relationship("Rubric", back_populates="scenario", uselist=False)


class ScenarioStep(Base, TimestampMixin):
    __tablename__ = "scenario_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("scenarios.id"), nullable=False)
    step_id: Mapped[str] = mapped_column(String(100), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_key: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        UniqueConstraint("scenario_id", "step_id", name="uq_scenario_step"),
    )


# ---------------------------------------------------------------------------
# Skills / Rubrics
# ---------------------------------------------------------------------------

class SkillMap(Base, TimestampMixin):
    __tablename__ = "skill_maps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    skill_map_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    skills: Mapped[list] = mapped_column(JSON, nullable=False)


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    skill_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    levels: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Rubric(Base, TimestampMixin):
    __tablename__ = "rubrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    rubric_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    scenario_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("scenarios.id"), nullable=True
    )
    pass_score: Mapped[int] = mapped_column(Integer, default=70)
    critical_fail_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    scenario = relationship("Scenario", back_populates="rubric")
    criteria = relationship("RubricCriterion", back_populates="rubric")


class RubricCriterion(Base, TimestampMixin):
    __tablename__ = "rubric_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    rubric_id: Mapped[str] = mapped_column(String(36), ForeignKey("rubrics.id"), nullable=False)
    criterion_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_required: Mapped[bool] = mapped_column(Boolean, default=True)

    rubric = relationship("Rubric", back_populates="criteria")

    __table_args__ = (
        UniqueConstraint("rubric_id", "criterion_id", name="uq_rubric_criterion"),
    )


class CriticalError(Base, TimestampMixin):
    __tablename__ = "critical_errors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    error_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    scenario_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


# ---------------------------------------------------------------------------
# Enrollment / Sessions / Attempts
# ---------------------------------------------------------------------------

class UserTrainerEnrollment(Base, TimestampMixin):
    __tablename__ = "user_trainer_enrollments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="enrollments")
    trainer = relationship("TrainerProduct", back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint("user_id", "trainer_product_id", name="uq_user_enrollment"),
    )


class SimulationSession(Base, TimestampMixin):
    __tablename__ = "simulation_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("scenarios.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, completed, abandoned
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("SimulationMessage", back_populates="session")


class SimulationMessage(Base, TimestampMixin):
    __tablename__ = "simulation_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("simulation_sessions.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, ai, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), default="answer")

    session = relationship("SimulationSession", back_populates="messages")


class Attempt(Base, TimestampMixin):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    scenario_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("scenarios.id"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("simulation_sessions.id"), nullable=True
    )
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="in_progress"
    )  # in_progress, completed, evaluating, evaluated, failed
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_retry: Mapped[bool] = mapped_column(Boolean, default=False)
    retry_of_attempt_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activities.id"), nullable=True)
    activity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evaluation_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    submitted_answer: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    user = relationship("User", back_populates="attempts", lazy="selectin")
    scenario = relationship("Scenario", back_populates="attempts", lazy="selectin")
    evaluation = relationship("Evaluation", back_populates="attempt", uselist=False, lazy="selectin")


# ---------------------------------------------------------------------------
# Evaluations
# ---------------------------------------------------------------------------

class Evaluation(Base, TimestampMixin):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    attempt_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("attempts.id"), unique=True, nullable=False
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    strengths: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    weak_points: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    critical_errors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    next_recommendation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_ai_output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    validation_status: Mapped[str] = mapped_column(String(50), default="validated")

    attempt = relationship("Attempt", back_populates="evaluation", lazy="selectin")
    criteria_results = relationship("EvaluationCriterionResult", back_populates="evaluation", lazy="selectin")


class EvaluationCriterionResult(Base, TimestampMixin):
    __tablename__ = "evaluation_criteria_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    evaluation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluations.id"), nullable=False
    )
    criterion_id: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evaluation = relationship("Evaluation", back_populates="criteria_results")


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

class TrainerProgress(Base, TimestampMixin):
    __tablename__ = "trainer_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    average_score: Mapped[float] = mapped_column(Float, default=0.0)
    completed_scenarios: Mapped[int] = mapped_column(Integer, default=0)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    readiness_status: Mapped[str] = mapped_column(
        String(50), default="started"
    )  # started, developing, ready, strong
    last_scenario_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="progress_records")
    trainer = relationship("TrainerProduct", back_populates="progress_records")

    __table_args__ = (
        UniqueConstraint("user_id", "trainer_product_id", name="uq_user_progress"),
    )


class SkillScore(Base, TimestampMixin):
    __tablename__ = "skill_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    trainer_product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trainer_products.id"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(50), default="not_observed")

    __table_args__ = (
        UniqueConstraint("user_id", "trainer_product_id", "skill_id", name="uq_user_skill_score"),
    )


# ---------------------------------------------------------------------------
# Analytics / AI Requests
# ---------------------------------------------------------------------------

class AnalyticsEvent(Base, TimestampMixin):
    __tablename__ = "analytics_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    trainer_slug: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    scenario_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    properties: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    user = relationship("User", back_populates="analytics_events")

    __table_args__ = (
        Index("idx_analytics_event_type", "event_type"),
        Index("idx_analytics_timestamp", "event_timestamp"),
    )


class AIRequest(Base, TimestampMixin):
    __tablename__ = "ai_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    request_type: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_template: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="completed")  # completed, failed, timeout
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempt_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    scenario_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    request_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


# ---------------------------------------------------------------------------
# Feature Flags
# ---------------------------------------------------------------------------

class FeatureFlag(Base, TimestampMixin):
    __tablename__ = "feature_flags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flag_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rollout_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# Activity / Deterministic Activity System
# ---------------------------------------------------------------------------

class Activity(Base, TimestampMixin):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    activity_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    trainer_product_id: Mapped[str] = mapped_column(String(36), ForeignKey("trainer_products.id"), nullable=False)
    module_id: Mapped[str] = mapped_column(String(100), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # single_choice, multiple_choice, numeric, fill_blanks, matching
    evaluation_mode: Mapped[str] = mapped_column(String(50), default="deterministic")
    difficulty: Mapped[str] = mapped_column(String(50), default="junior")
    title_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    explanation_key: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[str] = mapped_column(String(20), default="0.1.0")
    migration_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    trainer = relationship("TrainerProduct", backref="activities")


class DeterministicEvaluation(Base, TimestampMixin):
    __tablename__ = "deterministic_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    attempt_id: Mapped[str] = mapped_column(String(36), ForeignKey("attempts.id"), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # correct, partial, incorrect
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evaluation_mode: Mapped[str] = mapped_column(String(50), default="deterministic")
    validation_status: Mapped[str] = mapped_column(String(50), default="validated")

    attempt = relationship("Attempt", back_populates="deterministic_evaluation", uselist=False)

# Add backref to Attempt
Attempt.deterministic_evaluation = relationship(
    "DeterministicEvaluation", back_populates="attempt", uselist=False, lazy="selectin"
)
