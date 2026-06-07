"""Pydantic schemas for Dynamic Item Bank Runtime entities."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Source Binding
# ---------------------------------------------------------------------------

class SourceBindingCreate(BaseModel):
    item_id: str = Field(..., max_length=100)
    source_registry_id: str = Field(..., max_length=100)
    source_version_id: str = Field(..., max_length=50)
    source_hash: Optional[str] = None
    source_title: str = Field(..., max_length=500)
    source_uri: Optional[str] = None
    source_section_reference: Optional[str] = None
    retrieved_date: Optional[datetime] = None
    domain_pack_id: str = Field(..., max_length=100)
    binding_actor: str = Field(..., max_length=100)


class SourceBindingResponse(BaseModel):
    id: str
    binding_id: str
    item_id: str
    source_registry_id: str
    source_version_id: str
    source_hash: Optional[str] = None
    source_title: str
    source_uri: Optional[str] = None
    source_section_reference: Optional[str] = None
    retrieved_date: Optional[datetime] = None
    domain_pack_id: str
    source_status_at_binding: str
    binding_actor: str
    binding_timestamp: datetime
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Item Create (Runtime Authoring)
# ---------------------------------------------------------------------------

class ControlledItemCreate(BaseModel):
    """Extended item creation with all required runtime fields."""
    item_id: str = Field(..., max_length=100)
    item_family_id: Optional[str] = None
    domain_pack_id: str = Field(..., max_length=100)
    item_type: str = Field(..., max_length=50)
    prompt: Optional[dict] = None
    response_contract: Optional[dict] = None
    answer_key: Optional[dict] = None
    rubric_id: str = Field(..., max_length=100)
    competency_ids: list[str] = Field(..., min_length=1)
    knowledge_source_refs: list[str] = Field(..., min_length=1)
    difficulty_target: str = "medium"
    locale: str = "en-US"
    market: str = "global"
    created_by: str = Field(..., max_length=100)
    creation_method: Literal["human_authored", "llm_assisted", "imported"] = "human_authored"
    provenance: str = Field(..., max_length=500)


class ItemDraftUpdate(BaseModel):
    prompt: Optional[dict] = None
    response_contract: Optional[dict] = None
    answer_key: Optional[dict] = None
    rubric_id: Optional[str] = None
    competency_ids: Optional[list[str]] = None
    knowledge_source_refs: Optional[list[str]] = None
    difficulty_target: Optional[str] = None
    provenance: Optional[str] = None


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class ReviewCreate(BaseModel):
    item_id: str = Field(..., max_length=100)
    review_stage: str = Field(..., max_length=30)  # expert_review, qa_review, psychometric_review
    reviewer_id: str = Field(..., max_length=100)
    reviewer_role: str = Field(..., max_length=50)
    decision: str = Field(..., max_length=30)  # approve, reject, request_changes, suspend
    reason: Optional[str] = None
    reviewer_comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    review_id: str
    item_id: str
    item_version: int
    review_stage: str
    reviewer_id: str
    reviewer_role: str
    decision: str
    reason: Optional[str] = None
    reviewer_comment: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReviewQueueItem(BaseModel):
    review_id: str
    item_id: str
    item_version: int
    review_stage: str
    status: str
    domain_pack_id: Optional[str] = None
    item_type: Optional[str] = None
    created_at: Optional[datetime] = None


class ReviewQueueResponse(BaseModel):
    items: list[ReviewQueueItem]
    total: int
    skip: int = 0
    limit: int = 100


# ---------------------------------------------------------------------------
# Pool Membership
# ---------------------------------------------------------------------------

class PoolMembershipCreate(BaseModel):
    item_id: str = Field(..., max_length=100)
    pool_type: str = Field(..., max_length=20)  # pilot, exam_eligible
    entered_by: str = Field(..., max_length=100)
    controlled_exception: bool = False
    exception_reason: Optional[str] = None


class PoolMembershipResponse(BaseModel):
    id: str
    membership_id: str
    item_id: str
    pool_type: str
    status: str
    entry_date: datetime
    exit_date: Optional[datetime] = None
    exit_reason: Optional[str] = None
    exposure_count: int = 0
    response_count: int = 0
    difficulty_estimate: Optional[float] = None
    discrimination_estimate: Optional[float] = None
    incident_count: int = 0
    flags: Optional[Any] = None
    next_review_date: Optional[datetime] = None
    controlled_exception: bool = False
    exception_reason: Optional[str] = None
    entered_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PoolQueryResponse(BaseModel):
    items: list[PoolMembershipResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ---------------------------------------------------------------------------
# Exposure
# ---------------------------------------------------------------------------

class ExposureEventCreate(BaseModel):
    item_id: str = Field(..., max_length=100)
    session_id: str = Field(..., max_length=100)
    exam_type: Optional[str] = None
    domain_pack_id: Optional[str] = None
    locale: Optional[str] = None
    cohort_id: Optional[str] = None


class ExposureEventResponse(BaseModel):
    id: str
    event_id: str
    item_id: str
    session_id: str
    exam_type: Optional[str] = None
    domain_pack_id: Optional[str] = None
    locale: Optional[str] = None
    cohort_id: Optional[str] = None
    exposure_timestamp: datetime
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExposureCounterResponse(BaseModel):
    item_id: str
    total_exposures: int
    rolling_window_exposures: int
    last_exposure_timestamp: Optional[datetime] = None
    exposure_threshold: int
    cooldown_until: Optional[datetime] = None
    overexposed: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------

class RotationPolicyCreate(BaseModel):
    policy_id: str = Field(..., max_length=100)
    domain_pack_id: Optional[str] = None
    item_id: Optional[str] = None
    max_total_exposures: int = 100
    rolling_window_days: int = 30
    min_cool_down_days: int = 7
    min_pool_size: int = 5
    enabled: bool = True


class RotationEligibilityResponse(BaseModel):
    item_id: str
    eligible: bool
    temporarily_cooling_down: bool = False
    exposure_limit_reached: bool = False
    suspended: bool = False
    retired: bool = False
    insufficient_pool: bool = False
    reason: Optional[str] = None


class RotationPolicyResponse(BaseModel):
    id: str
    policy_id: str
    domain_pack_id: Optional[str] = None
    item_id: Optional[str] = None
    max_total_exposures: int
    rolling_window_days: int
    min_cool_down_days: int
    min_pool_size: int
    enabled: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Suspension / Retirement
# ---------------------------------------------------------------------------

class GovernanceActionCreate(BaseModel):
    item_id: str = Field(..., max_length=100)
    actor_id: str = Field(..., max_length=100)
    actor_role: str = Field(..., max_length=50)
    reason: str = Field(..., max_length=1000)
    suspension_reason: Optional[str] = None  # source_invalidated, answer_key_defect, ambiguity, bias, legal, overexposure, psychometric_concern, reviewer_incident, operator_decision


class SupersessionCreate(BaseModel):
    predecessor_item_id: str = Field(..., max_length=100)
    successor_item_id: str = Field(..., max_length=100)
    reason: Optional[str] = None
    created_by: str = Field(..., max_length=100)


class SupersessionResponse(BaseModel):
    id: str
    supersession_id: str
    predecessor_item_id: str
    successor_item_id: str
    reason: Optional[str] = None
    supersession_date: datetime
    created_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------

class GovernanceSummaryResponse(BaseModel):
    total_drafts: int = 0
    submitted_items: int = 0
    awaiting_expert_review: int = 0
    awaiting_qa_review: int = 0
    pilot_ready_items: int = 0
    pilot_active_items: int = 0
    exam_eligible_items: int = 0
    suspended_items: int = 0
    retired_items: int = 0
    source_invalid_items: int = 0
    overexposed_items: int = 0
    items_without_active_rubric: int = 0
    review_sla_breaches: int = 0
    unresolved_incidents: int = 0
    domain_pack_id: Optional[str] = None
    locale: Optional[str] = None


class GovernanceIncidentResponse(BaseModel):
    id: str
    incident_id: str
    item_id: str
    incident_type: str
    severity: str
    status: str
    description: Optional[str] = None
    reported_by: str
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GovernanceIncidentListResponse(BaseModel):
    items: list[GovernanceIncidentResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------

class TraceabilityResponse(BaseModel):
    bindings: list[SourceBindingResponse]
    total: int


class TraceabilitySummary(BaseModel):
    item_id: str
    source_count: int
    all_sources_valid: bool
    oldest_binding: Optional[datetime] = None
    latest_binding: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Exception Approval
# ---------------------------------------------------------------------------

class ExceptionApprovalCreate(BaseModel):
    item_id: str = Field(..., max_length=100)
    exception_type: str = Field(..., max_length=50)
    reason: str = Field(..., max_length=1000)
    granted_by: str = Field(..., max_length=100)
    granted_by_role: str = Field(..., max_length=50)
    second_reviewer: Optional[str] = None
    expires_at: datetime


class ExceptionApprovalResponse(BaseModel):
    id: str
    exception_id: str
    item_id: str
    exception_type: str
    reason: str
    granted_by: str
    granted_by_role: str
    second_reviewer: Optional[str] = None
    expires_at: datetime
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
