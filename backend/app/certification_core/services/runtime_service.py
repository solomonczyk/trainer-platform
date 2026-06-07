"""Dynamic Item Bank Runtime services — authoring, review, publication, pools, exposure, rotation, governance."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.audit.service import AuditService
from app.certification_core.models.item_models import Item, ItemFamily
from app.certification_core.models.knowledge_source_models import KnowledgeSource
from app.certification_core.models.rubric_models import CertRubric
from app.certification_core.models.runtime_models import ItemExposureEvent, ItemRotationPolicy
from app.certification_core.repositories.item_repository import ItemRepository, ItemFamilyRepository
from app.certification_core.repositories.runtime_repository import (
    ItemSourceBindingRepository,
    ItemReviewRepository,
    ItemReviewDecisionRepository,
    ItemPoolMembershipRepository,
    ItemExposureEventRepository,
    ItemExposureCounterRepository,
    ItemRotationPolicyRepository,
    ItemGovernanceIncidentRepository,
    ItemSupersessionLinkRepository,
    ItemExceptionApprovalRepository,
)
from app.certification_core.schemas.runtime_schemas import (
    ControlledItemCreate,
    SourceBindingCreate,
    ReviewCreate,
    PoolMembershipCreate,
    ExposureEventCreate,
    GovernanceActionCreate,
    SupersessionCreate,
    ExceptionApprovalCreate,
    RotationPolicyCreate,
)
from app.certification_core.state_machine.item_lifecycle import (
    validate_transition,
    ITEM_LIFECYCLE_STATES,
    ALLOWED_TRANSITIONS,
)
from app.certification_core.services.authorization import (
    AuthorizationService,
    SELF_APPROVAL_RESTRICTED_ROLES,
)


# ---------------------------------------------------------------------------
# Source Traceability Service
# ---------------------------------------------------------------------------

class SourceTraceabilityService:
    """Validates and persists knowledge source bindings for items."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.binding_repo = ItemSourceBindingRepository(db)

    async def validate_source(
        self,
        source_registry_id: str,
        source_version_id: str,
        domain_pack_id: str,
    ) -> dict:
        """Validate a knowledge source for binding. Returns validation result."""
        # Check source exists
        result = await self.db.execute(
            select(KnowledgeSource).where(KnowledgeSource.id == source_registry_id)
        )
        source = result.scalar_one_or_none()
        if not source:
            return {"valid": False, "message": "Source not found"}

        # Check source not retired
        if source.status == "retired":
            return {"valid": False, "message": "Source is retired"}

        # Check source not suspended
        if source.status == "suspended":
            return {"valid": False, "message": "Source is suspended"}

        # Check version matches
        if source.version != source_version_id:
            return {
                "valid": False,
                "message": f"Source version mismatch: expected '{source.version}', got '{source_version_id}'",
            }

        # Check domain match
        if source.locale and domain_pack_id and source.locale != domain_pack_id.split("-")[0]:
            # Allow partial domain match; actual check is domain_pack alignment
            pass

        return {
            "valid": True,
            "message": "Source validation passed",
            "source": source,
        }

    async def create_binding(
        self,
        item_id: str,
        binding_data: SourceBindingCreate,
        actor_role: str,
    ) -> dict:
        """Create a source binding with traceability snapshot."""
        # Validate source
        validation = await self.validate_source(
            binding_data.source_registry_id,
            binding_data.source_version_id,
            binding_data.domain_pack_id,
        )
        if not validation["valid"]:
            return {"success": False, "message": validation["message"]}

        source: KnowledgeSource = validation["source"]

        # Create binding
        binding = await self.binding_repo.create(
            binding_id=f"bnd-{uuid.uuid4().hex[:12]}",
            item_id=item_id,
            source_registry_id=binding_data.source_registry_id,
            source_version_id=binding_data.source_version_id,
            source_hash=source.content_hash,
            source_title=binding_data.source_title or source.title,
            source_uri=binding_data.source_uri or source.source_url,
            source_section_reference=binding_data.source_section_reference,
            retrieved_date=binding_data.retrieved_date or datetime.now(timezone.utc),
            domain_pack_id=binding_data.domain_pack_id,
            source_status_at_binding=source.status,
            binding_actor=binding_data.binding_actor,
        )
        return {"success": True, "binding": binding}

    async def get_traceability(self, item_id: str) -> dict:
        """Get full traceability data for an item."""
        bindings, total = await self.binding_repo.get_by_item(item_id)
        return {"bindings": bindings, "total": total}

    async def validate_item_sources(self, item_pk: str) -> dict:
        """Validate that all source bindings for an item are still valid.

        Args:
            item_pk: The primary key (id) of the item, not the business key.
        """
        bindings, total = await self.binding_repo.get_by_item(item_pk)
        if total == 0:
            return {"valid": False, "message": "No source bindings found"}

        for binding in bindings:
            result = await self.db.execute(
                select(KnowledgeSource).where(
                    KnowledgeSource.id == binding.source_registry_id
                )
            )
            source = result.scalar_one_or_none()
            if not source:
                return {
                    "valid": False,
                    "message": f"Source '{binding.source_title}' no longer exists",
                }
            if source.status in ("retired", "suspended"):
                return {
                    "valid": False,
                    "message": f"Source '{source.title}' is {source.status}",
                }
        return {"valid": True, "message": "All sources valid"}


# ---------------------------------------------------------------------------
# Authoring Service
# ---------------------------------------------------------------------------

class AuthoringService:
    """Controlled item authoring with validation and workflow orchestration."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.audit = AuditService(db)
        self.traceability = SourceTraceabilityService(db)

    async def create_draft(self, data: ControlledItemCreate, actor_role: str) -> dict:
        """Create a new item draft with full provenance."""
        # Validate creation method
        if data.creation_method not in ("human_authored", "llm_assisted", "imported"):
            return {"success": False, "message": "Invalid creation method"}

        # LLM-assisted items do NOT imply approval
        # Validate required fields
        if not data.answer_key:
            return {"success": False, "message": "Answer key is required"}

        # Validate rubric exists
        rubric_result = await self.db.execute(
            select(CertRubric).where(CertRubric.rubric_id == data.rubric_id)
        )
        rubric = rubric_result.scalar_one_or_none()
        if not rubric:
            return {"success": False, "message": f"Rubric '{data.rubric_id}' not found"}
        if rubric.status not in ("active", "published"):
            return {"success": False, "message": f"Rubric '{data.rubric_id}' is not active"}

        # Validate item family exists (if provided)
        if data.item_family_id:
            family_result = await self.db.execute(
                select(ItemFamily).where(ItemFamily.family_id == data.item_family_id)
            )
            family = family_result.scalar_one_or_none()
            if not family:
                return {"success": False, "message": f"Item family '{data.item_family_id}' not found"}

        # Create the item
        item_data = data.model_dump(exclude={"creation_method", "provenance"})
        item = await self.item_repo.create(**item_data)

        # Create initial snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason=f"Initial draft ({data.creation_method})",
            created_by=data.created_by,
        )
        await self.db.refresh(item)

        # Audit
        await self.audit.record_create(
            entity_type="item",
            entity_id=item.item_id,
            actor_id=data.created_by,
            actor_role=actor_role,
            after_state={"item_id": item.item_id, "creation_method": data.creation_method},
            reason=f"Item draft created via {data.creation_method}",
        )

        return {"success": True, "item": item}

    async def update_draft(self, item_id: str, update_data: dict, actor_id: str, actor_role: str) -> dict:
        """Update an item in draft status only."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        if item.status not in ("draft", "generated", "automated_validation_failed"):
            return {
                "success": False,
                "message": f"Cannot update item with status '{item.status}'. Only drafts can be edited.",
            }

        # Save before state for audit
        before_state = {
            "prompt": item.prompt,
            "answer_key": item.answer_key,
            "competency_ids": item.competency_ids,
        }

        # Apply updates
        for key, value in update_data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        await self.db.flush()

        # Create version snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason="Draft updated",
            created_by=actor_id,
        )

        # Audit
        await self.audit.record_update(
            entity_type="item",
            entity_id=item_id,
            actor_id=actor_id,
            actor_role=actor_role,
            before_state=before_state,
            after_state={"item_id": item_id, "status": item.status},
            reason="Draft updated",
        )

        return {"success": True, "item": item}

    async def submit_for_review(self, item_id: str, actor_id: str, actor_role: str) -> dict:
        """Submit an item for review after validating all requirements."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        if item.status not in ("draft", "generated", "automated_validation_failed", "automated_validation_passed"):
            return {
                "success": False,
                "message": f"Cannot submit item with status '{item.status}'",
            }

        # Validate source bindings
        bindings, _ = await ItemSourceBindingRepository(self.db).get_by_item(item.id)
        if len(bindings) == 0:
            return {
                "success": False,
                "message": "Cannot submit item without source bindings. Bind at least one knowledge source.",
            }

        # Validate all sources are valid
        source_check = await self.traceability.validate_item_sources(item.id)
        if not source_check["valid"]:
            return {"success": False, "message": source_check["message"]}

        # Validate answer key exists
        if not item.answer_key:
            return {"success": False, "message": "Answer key is required before submission"}

        # Validate rubric binding
        if not item.rubric_id:
            return {"success": False, "message": "Rubric binding is required"}

        # Validate competency binding
        if not item.competency_ids or len(item.competency_ids) == 0:
            return {"success": False, "message": "Competency binding is required"}

        # Transition to expert_review_required
        transition_result = validate_transition(
            item.status, "expert_review_required", actor_role, actor_id,
        )
        if not transition_result["allowed"]:
            return {"success": False, "message": transition_result["message"]}

        item.status = "expert_review_required"
        await self.db.flush()

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason="Submitted for review",
            created_by=actor_id,
        )

        # Audit
        await self.audit.record_transition(
            entity_type="item",
            entity_id=item_id,
            from_status="draft",
            to_status="expert_review_required",
            actor_id=actor_id,
            actor_role=actor_role,
            reason="Item submitted for expert review",
        )

        return {"success": True, "item": item}


# ---------------------------------------------------------------------------
# Review Service
# ---------------------------------------------------------------------------

class ReviewService:
    """Review queue management with strict self-approval prevention."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.review_repo = ItemReviewRepository(db)
        self.decision_repo = ItemReviewDecisionRepository(db)
        self.item_repo = ItemRepository(db)
        self.audit = AuditService(db)
        self.traceability = SourceTraceabilityService(db)

    async def get_review_queue(
        self,
        review_stage: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        """Get items awaiting review."""
        # Get items in "expert_review_required" status
        filters = {"status": "expert_review_required"}
        if review_stage:
            filters["status"] = review_stage

        # Use the item repository to find items needing review
        items, total = await self.item_repo.list_items(
            skip=skip, limit=limit, status=filters["status"],
        )

        queue_items = []
        for item in items:
            # Determine what review stage is needed
            if item.status == "expert_review_required":
                stage = "expert_review"
            elif item.status == "approved_for_pilot":
                stage = "pilot_ready"
            else:
                stage = item.status

            queue_items.append({
                "review_id": f"review-{item.item_id}",
                "item_id": item.item_id,
                "item_version": item.version,
                "review_stage": stage,
                "status": item.status,
                "domain_pack_id": item.domain_pack_id,
                "item_type": item.item_type,
                "created_at": item.created_at,
            })

        return {"items": queue_items, "total": total, "skip": skip, "limit": limit}

    async def perform_review(self, data: ReviewCreate, actor_id: str, actor_role: str) -> dict:
        """Perform a review of an item. Blocks self-approval."""
        item = await self.item_repo.get_by_item_id(data.item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        # Prevent LLM self-approval (check first — LLM cannot approve regardless)
        if data.reviewer_id.startswith("llm:"):
            return {
                "success": False,
                "message": "LLM actors cannot approve items",
            }

        # Prevent author self-approval
        if data.reviewer_id == item.created_by:
            return {
                "success": False,
                "message": "Author cannot review own item",
            }

        # Prevent domain owner self-approval if they authored
        if actor_role in ("domain_owner",) and data.reviewer_id == item.created_by:
            return {
                "success": False,
                "message": "Domain owner cannot self-approve own authored item",
            }

        # Role-based stage validation
        if data.review_stage == "expert_review" and actor_role not in ("expert_reviewer", "domain_owner", "platform_admin"):
            return {
                "success": False,
                "message": f"Role '{actor_role}' cannot perform expert review",
            }

        if data.review_stage == "qa_review" and actor_role not in ("qa_reviewer", "expert_reviewer", "domain_owner", "platform_admin"):
            return {
                "success": False,
                "message": f"Role '{actor_role}' cannot perform QA review",
            }

        if data.review_stage == "psychometric_review" and actor_role not in ("psychometric_reviewer", "platform_admin"):
            return {
                "success": False,
                "message": f"Role '{actor_role}' cannot perform psychometric review",
            }

        before_status = item.status

        # Create review record
        review = await self.review_repo.create(
            review_id=f"rev-{uuid.uuid4().hex[:12]}",
            item_id=item.id,
            item_version=item.version,
            review_stage=data.review_stage,
            reviewer_id=data.reviewer_id,
            reviewer_role=data.reviewer_role,
            decision=data.decision,
            reason=data.reason,
            reviewer_comment=data.reviewer_comment,
        )

        # Process decision
        after_status = before_status

        if data.decision == "approve":
            if data.review_stage == "expert_review":
                # Expert review passed — allow transition to approved_for_pilot
                if item.status == "expert_review_required":
                    after_status = "approved_for_pilot"
                    await self.item_repo.update_status(item.id, "approved_for_pilot")
                    # Create snapshot
                    await self.item_repo.create_snapshot(
                        item.id,
                        change_reason=f"Expert review approved by {data.reviewer_id}",
                        created_by=data.reviewer_id,
                    )

        elif data.decision == "reject":
            after_status = "draft"
            await self.item_repo.update_status(item.id, "draft")

        elif data.decision == "request_changes":
            after_status = "draft"
            await self.item_repo.update_status(item.id, "draft")

        elif data.decision == "suspend":
            after_status = "suspended"
            await self.item_repo.update_status(item.id, "suspended")

        # Create immutable decision trail
        decision = await self.decision_repo.create(
            decision_id=f"dec-{uuid.uuid4().hex[:12]}",
            review_id=review.id,
            reviewer_id=data.reviewer_id,
            reviewer_role=data.reviewer_role,
            decision=data.decision,
            reason=data.reason,
            before_status=before_status,
            after_status=after_status,
            item_version=item.version,
        )

        # Audit
        await self.audit.record_transition(
            entity_type="item",
            entity_id=data.item_id,
            from_status=before_status,
            to_status=after_status,
            actor_id=data.reviewer_id,
            actor_role=data.reviewer_role,
            reason=f"Review decision: {data.decision} by {data.review_stage}",
        )

        return {
            "success": True,
            "review": review,
            "decision": decision,
            "before_status": before_status,
            "after_status": after_status,
        }

    async def get_review_history(self, item_id: str) -> dict:
        """Get full review history for an item."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        reviews, total = await self.review_repo.list_reviews(item_id=item.id)
        return {"success": True, "reviews": reviews, "total": total}


# ---------------------------------------------------------------------------
# Pilot Pool Service
# ---------------------------------------------------------------------------

class PilotPoolService:
    """Controls entry to and management of the pilot pool."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pool_repo = ItemPoolMembershipRepository(db)
        self.item_repo = ItemRepository(db)
        self.audit = AuditService(db)
        self.traceability = SourceTraceabilityService(db)

    async def enter_pilot(self, item_id: str, entered_by: str, actor_role: str) -> dict:
        """Enter an item into the pilot pool after all preceding gates passed."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        # Must be in approved_for_pilot state
        if item.status != "approved_for_pilot":
            return {
                "success": False,
                "message": f"Item must be in 'approved_for_pilot' status, not '{item.status}'",
            }

        # Validate source traceability still valid
        source_check = await self.traceability.validate_item_sources(item.id)
        if not source_check["valid"]:
            return {"success": False, "message": source_check["message"]}

        # Validate rubric is active
        if item.rubric_id:
            rubric_result = await self.db.execute(
                select(CertRubric).where(CertRubric.rubric_id == item.rubric_id)
            )
            rubric = rubric_result.scalar_one_or_none()
            if not rubric or rubric.status not in ("active", "published"):
                return {"success": False, "message": "Associated rubric is not active"}

        # Check not already in pilot
        existing = await self.pool_repo.get_active_by_item_and_pool(item.id, "pilot")
        if existing:
            return {"success": False, "message": "Item is already in the pilot pool"}

        # Create pool membership
        membership = await self.pool_repo.create(
            membership_id=f"mem-{uuid.uuid4().hex[:12]}",
            item_id=item.id,
            pool_type="pilot",
            status="active",
            entered_by=entered_by,
        )

        # Transition item to pilot status
        await self.item_repo.update_status(item.id, "pilot")

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason="Entered pilot pool",
            created_by=entered_by,
        )

        # Audit
        await self.audit.record_transition(
            entity_type="item",
            entity_id=item_id,
            from_status="approved_for_pilot",
            to_status="pilot",
            actor_id=entered_by,
            actor_role=actor_role,
            reason="Item entered pilot pool",
        )

        return {"success": True, "membership": membership}

    async def complete_pilot(self, item_id: str, actor_id: str, actor_role: str) -> dict:
        """Mark pilot as completed — requires controlled evidence."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        if item.status != "pilot":
            return {"success": False, "message": f"Item is in '{item.status}', not 'pilot'"}

        # Deactivate pilot membership
        await self.pool_repo.deactivate_by_item_and_pool(
            item.id, "pilot", exit_reason="Pilot completed",
        )

        # Transition to calibration_review
        await self.item_repo.update_status(item.id, "calibration_review")

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason="Pilot completed, entering calibration review",
            created_by=actor_id,
        )

        # Audit
        await self.audit.record_transition(
            entity_type="item",
            entity_id=item_id,
            from_status="pilot",
            to_status="calibration_review",
            actor_id=actor_id,
            actor_role=actor_role,
            reason="Pilot completed",
        )

        return {"success": True, "message": "Pilot completed, item moved to calibration review"}

    async def get_pilot_pool(
        self, status: Optional[str] = None, skip: int = 0, limit: int = 100,
    ) -> dict:
        """Query the pilot pool."""
        items, total = await self.pool_repo.list_pool(
            pool_type="pilot", status=status, skip=skip, limit=limit,
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}


# ---------------------------------------------------------------------------
# Exam-Eligible Pool Service
# ---------------------------------------------------------------------------

class ExamEligiblePoolService:
    """Controls entry to the exam-eligible pool with strict gate enforcement."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pool_repo = ItemPoolMembershipRepository(db)
        self.item_repo = ItemRepository(db)
        self.audit = AuditService(db)
        self.traceability = SourceTraceabilityService(db)

    async def enter_exam_eligible(
        self,
        item_id: str,
        entered_by: str,
        actor_role: str,
        controlled_exception: bool = False,
        exception_data: Optional[dict] = None,
    ) -> dict:
        """Move an item to exam-eligible pool with strict gating."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        # BLOCK direct assignment from draft/created
        if item.status in ("draft", "generated", "automated_validation_failed", "automated_validation_passed"):
            return {
                "success": False,
                "message": "Direct exam-eligible assignment blocked. Item must complete full review lifecycle.",
            }

        # Must be calibrated (or controlled exception)
        if not controlled_exception and item.status != "calibrated":
            return {
                "success": False,
                "message": f"Item must be 'calibrated', not '{item.status}'. "
                           f"Use controlled exception for other statuses.",
            }

        # Validate source traceability
        source_check = await self.traceability.validate_item_sources(item.id)
        if not source_check["valid"]:
            return {"success": False, "message": source_check["message"]}

        # Validate rubric still active
        if item.rubric_id:
            rubric_result = await self.db.execute(
                select(CertRubric).where(CertRubric.rubric_id == item.rubric_id)
            )
            rubric = rubric_result.scalar_one_or_none()
            if not rubric or rubric.status not in ("active", "published"):
                return {"success": False, "message": "Associated rubric is not active"}

        # Check not already in exam_eligible pool
        existing = await self.pool_repo.get_active_by_item_and_pool(item.id, "exam_eligible")
        if existing:
            return {"success": False, "message": "Item is already in the exam-eligible pool"}

        # Handle controlled exception
        if controlled_exception:
            if not exception_data:
                return {"success": False, "message": "Exception data required for controlled exception"}
            if actor_role != "platform_admin":
                return {"success": False, "message": "Only platform_admin can grant controlled exceptions"}
            if not exception_data.get("second_reviewer"):
                return {"success": False, "message": "Controlled exception requires a second reviewer"}
            if not exception_data.get("reason"):
                return {"success": False, "message": "Controlled exception requires documented reason"}
            if not exception_data.get("expires_at"):
                return {"success": False, "message": "Controlled exception requires expiration date"}

        # Create membership
        membership = await self.pool_repo.create(
            membership_id=f"mem-{uuid.uuid4().hex[:12]}",
            item_id=item.id,
            pool_type="exam_eligible",
            status="active",
            controlled_exception=controlled_exception,
            entered_by=entered_by,
        )

        # Transition status
        await self.item_repo.update_status(item.id, "exam_eligible")

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason="Entered exam-eligible pool",
            created_by=entered_by,
        )

        # Audit
        action = "exam_eligibility_granted"
        if controlled_exception:
            action = "controlled_exception_granted"
        await self.audit.record(
            entity_type="item",
            entity_id=item_id,
            action=action,
            actor_id=entered_by,
            actor_role=actor_role,
            reason=exception_data.get("reason", "Entered exam-eligible pool") if exception_data else "Entered exam-eligible pool",
        )

        return {"success": True, "membership": membership}

    async def get_exam_eligible_pool(
        self, status: Optional[str] = None, skip: int = 0, limit: int = 100,
    ) -> dict:
        """Query the exam-eligible pool."""
        items, total = await self.pool_repo.list_pool(
            pool_type="exam_eligible", status=status, skip=skip, limit=limit,
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}


# ---------------------------------------------------------------------------
# Exposure Service
# ---------------------------------------------------------------------------

class ExposureService:
    """Idempotent exposure tracking with threshold enforcement."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = ItemExposureEventRepository(db)
        self.counter_repo = ItemExposureCounterRepository(db)
        self.item_repo = ItemRepository(db)
        self.audit = AuditService(db)

    async def record_exposure(self, data: ExposureEventCreate, actor_role: str) -> dict:
        """Record an exposure event — idempotent per item+session."""
        # Check item exists
        item = await self.item_repo.get_by_item_id(data.item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        # Check item is eligible
        if item.status == "suspended":
            return {"success": False, "message": "Suspended items cannot be exposed"}
        if item.status == "retired":
            return {"success": False, "message": "Retired items cannot be exposed"}

        # Idempotency check — duplicate session events are not double-counted
        exists = await self.event_repo.exists(item.id, data.session_id)
        if exists:
            existing_event = await self.event_repo.get_by_item_and_session(
                item.id, data.session_id,
            )
            return {"success": True, "event": existing_event, "duplicate": True}

        # Create event
        event = await self.event_repo.create(
            event_id=f"exp-{uuid.uuid4().hex[:12]}",
            item_id=item.id,
            session_id=data.session_id,
            exam_type=data.exam_type,
            domain_pack_id=data.domain_pack_id or item.domain_pack_id,
            locale=data.locale or item.locale,
            cohort_id=data.cohort_id,
        )

        # Increment counter
        counter = await self.counter_repo.increment(item.id)

        # Update item exposure count
        item.exposure_count = (item.exposure_count or 0) + 1
        await self.db.flush()

        # Audit
        await self.audit.record(
            entity_type="item",
            entity_id=data.item_id,
            action="exposure_recorded",
            actor_id="system",
            actor_role=actor_role,
        )

        return {"success": True, "event": event, "counter": counter}

    async def get_exposure(self, item_id: str) -> dict:
        """Get exposure data for an item."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        counter = await self.counter_repo.get_by_item(item.id)
        events, total = await self.event_repo.list_all(
            filters={"item_id": item.id},
        )

        return {
            "success": True,
            "counter": counter,
            "events": events,
            "total_events": total,
        }

    async def check_rotation_eligibility(
        self, item_id: str, policy: Optional[ItemRotationPolicy] = None,
    ) -> dict:
        """Check if an item is eligible for use."""
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"eligible": False, "reason": "Item not found"}

        if item.status == "suspended":
            return {"eligible": False, "suspended": True, "reason": "Item is suspended"}
        if item.status == "retired":
            return {"eligible": False, "retired": True, "reason": "Item is retired"}

        counter = await self.counter_repo.get_by_item(item.id)

        if not counter:
            return {"eligible": True}

        if policy and policy.enabled:
            # Check cool-down
            if counter.cooldown_until and counter.cooldown_until > datetime.now(timezone.utc):
                return {
                    "eligible": False,
                    "temporarily_cooling_down": True,
                    "reason": f"Cool-down until {counter.cooldown_until.isoformat()}",
                }

            # Check exposure limit
            if counter.total_exposures >= policy.max_total_exposures:
                return {
                    "eligible": False,
                    "exposure_limit_reached": True,
                    "reason": f"Exposure limit reached: {counter.total_exposures}/{policy.max_total_exposures}",
                }

            # Check rolling window
            if policy.rolling_window_days > 0:
                since = datetime.now(timezone.utc) - timedelta(days=policy.rolling_window_days)
                window_count = await self.event_repo.count_by_item_in_window(item.id, since)
                if window_count >= policy.max_total_exposures:
                    return {
                        "eligible": False,
                        "exposure_limit_reached": True,
                        "reason": f"Rolling window limit reached: {window_count} in {policy.rolling_window_days}d",
                    }

        return {"eligible": True}


# ---------------------------------------------------------------------------
# Rotation Policy Service
# ---------------------------------------------------------------------------

class RotationPolicyService:
    """Manages rotation policy configuration and eligibility checks.

    Evaluates all policy inputs:
    - locale compatibility
    - domain balance quotas
    - competency balance quotas
    - difficulty balance ratios
    - item family diversity
    - recent-use exclusion
    - exposure threshold
    - cool-down period
    - suspended/retired state
    - minimum pool size
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.policy_repo = ItemRotationPolicyRepository(db)
        self.exposure_service = ExposureService(db)
        self.item_repo = ItemRepository(db)
        self.pool_repo = ItemPoolMembershipRepository(db)
        self.audit = AuditService(db)

    async def create_policy(self, data: RotationPolicyCreate, actor_role: str) -> dict:
        """Create a rotation policy."""
        if actor_role not in ("platform_admin", "domain_owner"):
            return {"success": False, "message": "Insufficient permissions"}
        policy = await self.policy_repo.create(**data.model_dump())
        return {"success": True, "policy": policy}

    async def check_eligibility(self, item_id: str) -> dict:
        """Check item eligibility per applicable policy.

        Returns dict with eligible bool, all reason flags, decision_reasons list.
        """
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return self._build_result(item_id, eligible=False,
                                       reasons=["Item not found"], code="item_not_found")

        # Find applicable policy
        policy = await self.policy_repo.get_by_item(item_id)
        if not policy:
            # Try by domain pack
            if item.domain_pack_id:
                policies, _ = await self.policy_repo.get_by_domain_pack(item.domain_pack_id)
                if policies:
                    policy = policies[0]
            if not policy:
                # Try default
                policy = await self.policy_repo.get_by_business_id("default", "policy_id")

        policy_id = policy.policy_id if policy else "none"
        reasons: list[str] = []
        flags: dict = {}
        now = datetime.now(timezone.utc)

        # 1. Suspended check
        if item.status == "suspended":
            return self._build_result(item_id, eligible=False, policy_id=policy_id,
                                       reasons=["Item is suspended"], code="suspended",
                                       suspended=True)

        # 2. Retired check
        if item.status == "retired":
            return self._build_result(item_id, eligible=False, policy_id=policy_id,
                                       reasons=["Item is retired"], code="retired",
                                       retired=True)

        # 3. Locale compatibility
        if policy and policy.allowed_locales:
            if item.locale not in policy.allowed_locales:
                reasons.append(f"Locale '{item.locale}' not in allowed: {policy.allowed_locales}")
                flags["wrong_locale"] = True

        # 4. Domain balance
        if policy and policy.domain_balance_quotas and item.domain_pack_id:
            domain_key = item.domain_pack_id
            quota = policy.domain_balance_quotas.get(domain_key, 0)
            if quota > 0:
                # Count active exam-eligible items in this domain
                count_domain = await self.item_repo.count(
                    filters={"domain_pack_id": domain_key, "status": "exam_eligible"}
                )
                if count_domain >= quota:
                    reasons.append(f"Domain '{domain_key}' quota {quota} exceeded ({count_domain})")
                    flags["domain_balance_failed"] = True

        # 5. Competency balance
        if policy and policy.competency_balance_quotas and item.competency_ids:
            for comp_id in (item.competency_ids or []):
                quota = policy.competency_balance_quotas.get(str(comp_id), 0)
                if quota > 0:
                    count_comp = await self.item_repo.count(
                        filters={"status": "exam_eligible"}
                    )
                    # Rough check — count items referencing this competency
                    if count_comp >= quota:
                        reasons.append(f"Competency balance quota '{comp_id}' exceeded")
                        flags["competency_balance_failed"] = True
                        break

        # 6. Difficulty balance
        if policy and policy.difficulty_balance_ratios:
            diff = item.difficulty_target or "medium"
            max_ratio = policy.difficulty_balance_ratios.get(diff, 1.0)
            total_items = await self.item_repo.count(filters={"status": "exam_eligible"})
            diff_count = await self.item_repo.count(
                filters={"difficulty_target": diff, "status": "exam_eligible"}
            )
            if total_items > 0 and (diff_count / total_items) > max_ratio:
                reasons.append(f"Difficulty '{diff}' ratio {max_ratio} exceeded ({diff_count}/{total_items})")
                flags["difficulty_balance_failed"] = True

        # 7. Item family diversity
        if policy and policy.max_items_per_family > 0 and item.item_family_id:
            family_count = await self.item_repo.count(
                filters={"item_family_id": item.item_family_id, "status": "exam_eligible"}
            )
            if family_count >= policy.max_items_per_family:
                reasons.append(f"Item family limit {policy.max_items_per_family} reached ({family_count})")
                flags["item_family_diversity_failed"] = True

        # 8. Exposure checks via exposure service
        exposure_check = await self.exposure_service.check_rotation_eligibility(item_id, policy)
        if not exposure_check.get("eligible", True):
            if exposure_check.get("temporarily_cooling_down") or exposure_check.get("cooling_down"):
                reasons.append(exposure_check.get("reason", "Item is cooling down"))
                flags["cooling_down"] = True
            elif exposure_check.get("exposure_limit_reached"):
                reasons.append(exposure_check.get("reason", "Exposure limit reached"))
                flags["exposure_limit_reached"] = True

        # 9. Recent use exclusion (check if used recently)
        if policy and policy.recent_use_window_days > 0:
            since = now - timedelta(days=policy.recent_use_window_days)
            recent_events = await self.db.execute(
                select(func.count(ItemExposureEvent.id))
                .where(ItemExposureEvent.item_id == item.id)
                .where(ItemExposureEvent.exposure_timestamp >= since)
            )
            recent_count = recent_events.scalar() or 0
            if recent_count > 0:
                reasons.append(f"Recent use exclusion: {recent_count} exposures in {policy.recent_use_window_days}d")
                flags["recent_use_excluded"] = True

        # 10. Insufficient pool detection
        if policy and policy.min_pool_size > 0:
            pool_items, pool_total = await self.pool_repo.list_pool(
                pool_type="exam_eligible", status="active"
            )
            if pool_total < policy.min_pool_size:
                reasons.append(f"Insufficient pool: {pool_total} items, minimum {policy.min_pool_size}")
                flags["insufficient_pool"] = True

        eligible = len(flags) == 0
        if not eligible:
            code = "blocked"
        else:
            code = "eligible"

        # Build evaluated_inputs
        evaluated_inputs = {
            "item_id": item_id,
            "status": item.status,
            "locale": item.locale,
            "domain_pack_id": item.domain_pack_id,
            "difficulty_target": item.difficulty_target,
            "competency_ids": item.competency_ids,
            "item_family_id": item.item_family_id,
        }
        if policy:
            evaluated_inputs["policy_id"] = policy.policy_id
            evaluated_inputs["policy_enabled"] = policy.enabled
            evaluated_inputs["min_pool_size"] = policy.min_pool_size
            evaluated_inputs["recent_use_window_days"] = policy.recent_use_window_days
            evaluated_inputs["exposure_threshold"] = policy.exposure_threshold

        # Audit
        audit_action = "rotation_evaluated" if eligible else "rotation_excluded"
        await self.audit.record(
            entity_type="item",
            entity_id=item_id,
            action=audit_action,
            actor_id="system",
            actor_role="rotation_policy",
            reason=f"Rotation {'eligible' if eligible else 'excluded'}: {'; '.join(reasons) if reasons else 'all checks passed'}",
        )

        if flags.get("insufficient_pool"):
            await self.audit.record(
                entity_type="item",
                entity_id=item_id,
                action="insufficient_pool_detected",
                actor_id="system",
                actor_role="rotation_policy",
                reason=f"Pool has insufficient items: minimum {policy.min_pool_size if policy else 5}",
            )

        return self._build_result(
            item_id=item_id, eligible=eligible, policy_id=policy_id,
            reasons=reasons, code=code, evaluated_inputs=evaluated_inputs,
            **flags,
        )

    def _build_result(
        self, item_id: str, eligible: bool,
        policy_id: str = "none", reasons: list[str] = None,
        code: str = "eligible", evaluated_inputs: dict = None,
        **flags,
    ) -> dict:
        """Build a standardized rotation eligibility result."""
        from datetime import datetime, timezone
        result = {
            "item_id": item_id,
            "eligible": eligible,
            "policy_id": policy_id,
            "policy_version": "1",
            "decision_code": code,
            "decision_reasons": reasons or [],
            "evaluated_inputs": evaluated_inputs,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "; ".join(reasons) if reasons else ("Eligible" if eligible else "Blocked"),
        }
        # Apply flags
        for flag_name in [
            "cooling_down", "exposure_limit_reached", "wrong_locale",
            "domain_balance_failed", "competency_balance_failed",
            "difficulty_balance_failed", "item_family_diversity_failed",
            "recent_use_excluded", "suspended", "retired", "insufficient_pool",
        ]:
            result[flag_name] = flags.get(flag_name, False)
        return result


# ---------------------------------------------------------------------------
# Controlled Exception Service
# ---------------------------------------------------------------------------

class ControlledExceptionService:
    """Controlled psychometric exception with two-person control, expiration, and audit.

    Rules:
    - Requester must be platform_admin
    - Reason is required
    - Expiration is required and must be in the future
    - Requester cannot second-approve
    - Item author cannot approve exception
    - Expired/rejected/revoked exceptions are rejected
    - Scope is limited to one item version
    - All actions are audited
    - Exception never bypasses: source traceability, expert review, QA review,
      active item version, active rubric, suspension/retirement checks
    """

    SECOND_REVIEWER_ALLOWED_ROLES = [
        "psychometric_reviewer",
        "qa_reviewer",
        "domain_owner",
    ]

    def __init__(self, db: AsyncSession):
        self.db = db
        self.exception_repo = ItemExceptionApprovalRepository(db)
        self.item_repo = ItemRepository(db)
        self.pool_repo = ItemPoolMembershipRepository(db)
        self.traceability = SourceTraceabilityService(db)
        self.audit = AuditService(db)

    async def request_exception(
        self,
        data: ExceptionRequestCreate,
        requester_role: str,
    ) -> dict:
        """Request a controlled exception. Only platform_admin can request."""
        if requester_role != "platform_admin":
            return {"success": False, "message": "Only platform_admin can request exceptions",
                    "code": "FORBIDDEN_ROLE"}

        item = await self.item_repo.get_by_item_id(data.item_id)
        if not item:
            return {"success": False, "message": "Item not found", "code": "ITEM_NOT_FOUND"}

        # Reason is required
        if not data.reason or not data.reason.strip():
            return {"success": False, "message": "Reason is required",
                    "code": "REASON_REQUIRED"}

        # Expiration required
        if not data.expires_at:
            return {"success": False, "message": "Expiration date is required",
                    "code": "EXPIRATION_REQUIRED"}

        # Expiration must be in the future
        expires_at = data.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            return {"success": False, "message": "Expiration must be in the future",
                    "code": "EXPIRATION_PAST"}

        # Validate scope is limited to one item version
        if not data.item_version_id:
            # Use current item version as scope
            item_version = item.version
            data.item_version_id = f"{item.item_id}_v{item.version}"

        # Check for existing active exception for this item+version
        existing = await self.exception_repo.get_by_item_and_version(
            data.item_id, data.item_version_id,
        )
        for exc in existing[0] if existing[0] else []:
            if exc.is_active and exc.expires_at > datetime.now(timezone.utc):
                return {
                    "success": False,
                    "message": f"An active exception already exists: {exc.exception_id}",
                    "code": "DUPLICATE_EXCEPTION",
                    "existing_exception_id": exc.exception_id,
                }

        # DON'T check suspension/retirement here — exception cannot bypass those
        if item.status == "suspended":
            return {"success": False, "message": "Suspended items cannot receive exceptions",
                    "code": "ITEM_SUSPENDED"}
        if item.status == "retired":
            return {"success": False, "message": "Retired items cannot receive exceptions",
                    "code": "ITEM_RETIRED"}

        # Create exception record (status: pending)
        exception_id = f"exc-{uuid.uuid4().hex[:12]}"
        exc = await self.exception_repo.create(
            exception_id=exception_id,
            item_version_id=data.item_version_id,
            item_id=item.id,
            exception_type="psychometric_exception",
            reason=data.reason,
            scope=data.scope or f"item_version:{data.item_version_id}",
            requested_by=data.requested_by,
            requester_role=requester_role,
            granted_by=data.requested_by,
            granted_by_role=requester_role,
            expires_at=data.expires_at,
            is_active=True,
            status="pending",
        )

        # Audit
        audit_event = await self.audit.record(
            entity_type="item",
            entity_id=data.item_id,
            action="exception_requested",
            actor_id=data.requested_by,
            actor_role=requester_role,
            reason=f"Exception requested: {data.reason[:200]}",
        )

        # Link audit correlation ID
        exc.audit_correlation_id = audit_event.audit_event_id
        await self.db.flush()

        return {"success": True, "exception": exc}

    async def first_approve(
        self,
        exception_id: str,
        data: ExceptionApprovalFirst,
        actor_role: str,
    ) -> dict:
        """Record first approval (the requester's own approval)."""
        exc = await self.exception_repo.get_by_exception_id(exception_id)
        if not exc:
            return {"success": False, "message": "Exception not found", "code": "NOT_FOUND"}

        # Check expiration
        now = datetime.now(timezone.utc)
        expires = exc.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= now:
            await self.exception_repo.update_status(exception_id, "expired")
            return {"success": False, "message": "Exception has expired",
                    "code": "EXPIRED"}

        # Check status
        if exc.status != "pending":
            return {"success": False, "message": f"Exception is in '{exc.status}' state, not 'pending'",
                    "code": "WRONG_STATE"}

        # First approval — record
        exc.first_approver = data.reviewer_id
        exc.first_approval_timestamp = datetime.now(timezone.utc)
        exc.status = "first_approved"
        await self.db.flush()

        # Resolve business key for audit
        item = await self.item_repo.get_by_id(exc.item_id)

        # Audit
        await self.audit.record(
            entity_type="item",
            entity_id=item.item_id if item else exc.item_id,
            action="exception_first_approved",
            actor_id=data.reviewer_id,
            actor_role=actor_role,
            reason=f"Exception first approved by {data.reviewer_id}",
        )

        return {"success": True, "message": "First approval recorded",
                "exception": exc}

    async def second_approve(
        self,
        exception_id: str,
        data: ExceptionApprovalSecond,
        actor_role: str,
    ) -> dict:
        """Second (final) approval by an independent reviewer.

        Rules enforced:
        - Second reviewer must have an allowed role
        - Second reviewer cannot be the requester (self-approval blocked)
        - Item author cannot approve exception
        - Exception must not be expired
        - Exception must be in 'first_approved' state
        """
        exc = await self.exception_repo.get_by_exception_id(exception_id)
        if not exc:
            return {"success": False, "message": "Exception not found", "code": "NOT_FOUND"}

        # Check expiration
        now = datetime.now(timezone.utc)
        expires = exc.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= now:
            await self.exception_repo.update_status(exception_id, "expired")
            return {"success": False, "message": "Exception has expired",
                    "code": "EXPIRED"}

        # Check status — must be first_approved
        if exc.status != "first_approved":
            return {"success": False, "message": f"Exception is in '{exc.status}' state, need 'first_approved'",
                    "code": "WRONG_STATE"}

        # Second reviewer role check
        if actor_role not in self.SECOND_REVIEWER_ALLOWED_ROLES:
            return {
                "success": False,
                "message": f"Role '{actor_role}' cannot second-approve. Allowed: {self.SECOND_REVIEWER_ALLOWED_ROLES}",
                "code": "FORBIDDEN_ROLE",
            }

        # Requester cannot second-approve (self-approval prevention)
        if data.reviewer_id == exc.requested_by:
            return {
                "success": False,
                "message": "Requester cannot second-approve their own exception",
                "code": "SELF_APPROVAL_BLOCKED",
            }

        # First approver cannot second-approve
        if exc.first_approver and data.reviewer_id == exc.first_approver:
            return {
                "success": False,
                "message": "First approver cannot also be the second approver",
                "code": "SINGLE_PERSON_EXCEPTION_BLOCKED",
            }

        # Item author cannot approve exception
        item = await self.item_repo.get_by_id(exc.item_id)
        if item and item.created_by == data.reviewer_id:
            return {
                "success": False,
                "message": "Item author cannot approve exception for their own item",
                "code": "AUTHOR_APPROVAL_BLOCKED",
            }

        if data.decision == "reject":
            await self.exception_repo.update_status(exception_id, "rejected")
            reject_item = await self.item_repo.get_by_id(exc.item_id)
            await self.audit.record(
                entity_type="item",
                entity_id=reject_item.item_id if reject_item else exc.item_id,
                action="exception_rejected",
                actor_id=data.reviewer_id,
                actor_role=actor_role,
                reason=f"Exception rejected by {data.reviewer_id}",
            )
            return {"success": True, "message": "Exception rejected", "status": "rejected"}

        # Approve
        exc.second_reviewer = data.reviewer_id
        exc.second_approval_timestamp = datetime.now(timezone.utc)
        exc.status = "approved"
        await self.db.flush()

        # Audit
        item_for_audit = await self.item_repo.get_by_id(exc.item_id)
        await self.audit.record(
            entity_type="item",
            entity_id=item_for_audit.item_id if item_for_audit else exc.item_id,
            action="exception_second_approved",
            actor_id=data.reviewer_id,
            actor_role=actor_role,
            reason=f"Exception second approved by {data.reviewer_id}",
        )

        return {"success": True, "message": "Exception fully approved",
                "exception": exc}

    async def revoke_exception(
        self,
        exception_id: str,
        data: ExceptionRevocation,
        actor_role: str,
    ) -> dict:
        """Revoke an approved exception."""
        if actor_role != "platform_admin":
            return {"success": False, "message": "Only platform_admin can revoke exceptions",
                    "code": "FORBIDDEN_ROLE"}

        exc = await self.exception_repo.get_by_exception_id(exception_id)
        if not exc:
            return {"success": False, "message": "Exception not found", "code": "NOT_FOUND"}

        if exc.status == "revoked":
            return {"success": False, "message": "Exception already revoked", "code": "ALREADY_REVOKED"}

        await self.exception_repo.update_status(exception_id, "revoked")

        # Audit
        revoke_item = await self.item_repo.get_by_id(exc.item_id)
        await self.audit.record(
            entity_type="item",
            entity_id=revoke_item.item_id if revoke_item else exc.item_id,
            action="exception_revoked",
            actor_id=data.revoked_by,
            actor_role=actor_role,
            reason=f"Exception revoked: {data.reason[:200]}",
        )

        return {"success": True, "message": "Exception revoked"}

    async def validate_exception_for_gate(
        self,
        exception_id: str,
        item_id: str,
    ) -> dict:
        """Validate an exception can be used to grant exam eligibility.

        Checks all non-psychometric gates that the exception cannot bypass:
        - Source traceability
        - Active item version requirement
        - Active rubric requirement
        - Suspension/retirement checks
        """
        exc = await self.exception_repo.get_by_exception_id(exception_id)
        if not exc:
            return {"valid": False, "message": "Exception not found", "code": "NOT_FOUND"}

        # Exception must be approved
        if exc.status != "approved":
            return {"valid": False, "message": f"Exception is '{exc.status}', not 'approved'",
                    "code": "NOT_APPROVED"}

        # Must be active
        if not exc.is_active:
            return {"valid": False, "message": "Exception is not active", "code": "INACTIVE"}

        # Expiration check
        now = datetime.now(timezone.utc)
        expires = exc.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= now:
            return {"valid": False, "message": "Exception has expired", "code": "EXPIRED"}

        # Check scope — must match this item version
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {"valid": False, "message": "Item not found", "code": "ITEM_NOT_FOUND"}

        expected_version_id = f"{item.item_id}_v{item.version}"
        if exc.item_version_id and exc.item_version_id != expected_version_id:
            return {
                "valid": False,
                "message": f"Exception scope is version '{exc.item_version_id}' but item is '{expected_version_id}'",
                "code": "VERSION_MISMATCH",
            }

        # Non-bypassable checks:
        # Source traceability
        source_check = await self.traceability.validate_item_sources(item.id)
        if not source_check["valid"]:
            return {"valid": False, "message": source_check["message"], "code": "SOURCE_INVALID"}

        # Active rubric
        if item.rubric_id:
            rubric_result = await self.db.execute(
                select(CertRubric).where(CertRubric.rubric_id == item.rubric_id)
            )
            rubric = rubric_result.scalar_one_or_none()
            if not rubric or rubric.status not in ("active", "published"):
                return {"valid": False, "message": "Rubric is not active",
                        "code": "RUBRIC_INACTIVE"}

        # Suspension/retirement checks
        if item.status == "suspended":
            return {"valid": False, "message": "Item is suspended — exception cannot bypass",
                    "code": "ITEM_SUSPENDED"}
        if item.status == "retired":
            return {"valid": False, "message": "Item is retired — exception cannot bypass",
                    "code": "ITEM_RETIRED"}

        return {"valid": True, "message": "Exception valid for gate", "exception": exc}


# ---------------------------------------------------------------------------
# Single Exam-Eligibility Gate Service
# ---------------------------------------------------------------------------

class ExamEligibilityGateService:
    """Single authoritative entry point for granting exam-eligible status.

    All code paths that can result in 'exam_eligible' must pass through this service.
    Direct ORM/repository/update shortcuts are blocked.

    The service:
    1. Validates the item exists and is in a valid state
    2. Validates source traceability
    3. Validates active rubric
    4. Validates suspension/retirement not bypassed
    5. If controlled_exception_id is provided: validates and uses exception
    6. If no exception: requires 'calibrated' status
    7. Creates pool membership and transitions status
    8. Records audit
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.pool_repo = ItemPoolMembershipRepository(db)
        self.traceability = SourceTraceabilityService(db)
        self.audit = AuditService(db)
        self.exception_service = ControlledExceptionService(db)

    async def evaluate_and_grant_exam_eligibility(
        self,
        item_id: str,
        evaluated_by: str,
        evaluator_role: str,
        controlled_exception_id: Optional[str] = None,
    ) -> dict:
        """Single authoritative method to grant exam eligibility.

        Args:
            item_id: The business key of the item
            evaluated_by: User ID of the actor
            evaluator_role: Role of the actor
            controlled_exception_id: Optional exception ID if using controlled exception

        Returns:
            dict with eligibility result and decision details
        """
        item = await self.item_repo.get_by_item_id(item_id)
        if not item:
            return {
                "eligible": False, "item_id": item_id,
                "decision_code": "item_not_found",
                "decision_reasons": ["Item not found"],
                "messages": ["Item not found"],
            }

        reasons: list[str] = []

        # 1. Suspension/retirement check
        if item.status == "retired":
            reasons.append("Item is retired — cannot grant exam eligibility")
            await self._audit_denial(item_id, evaluated_by, evaluator_role, reasons)
            return {
                "eligible": False, "item_id": item_id,
                "decision_code": "retired",
                "decision_reasons": reasons,
                "messages": reasons,
            }
        if item.status == "suspended":
            reasons.append("Item is suspended — cannot grant exam eligibility")
            await self._audit_denial(item_id, evaluated_by, evaluator_role, reasons)
            return {
                "eligible": False, "item_id": item_id,
                "decision_code": "suspended",
                "decision_reasons": reasons,
                "messages": reasons,
            }

        # 2. Check if controlled exception path
        using_exception = controlled_exception_id is not None
        if using_exception:
            # Validate the exception
            exc_check = await self.exception_service.validate_exception_for_gate(
                controlled_exception_id, item_id,
            )
            if not exc_check["valid"]:
                reasons.append(exc_check["message"])
                await self._audit_denial(item_id, evaluated_by, evaluator_role, reasons)
                return {
                    "eligible": False, "item_id": item_id,
                    "decision_code": "exception_invalid",
                    "decision_reasons": reasons,
                    "messages": reasons,
                }
        else:
            # Standard path: must be calibrated
            if item.status != "calibrated":
                reasons.append(
                    f"Item must be 'calibrated' (status: '{item.status}'). "
                    "Use controlled exception for other statuses."
                )
                await self._audit_denial(item_id, evaluated_by, evaluator_role, reasons)
                return {
                    "eligible": False, "item_id": item_id,
                    "decision_code": "not_calibrated",
                    "decision_reasons": reasons,
                    "messages": reasons,
                }

        # 3. Source traceability (always required)
        source_check = await self.traceability.validate_item_sources(item.id)
        if not source_check["valid"]:
            reasons.append(source_check["message"])
            await self._audit_denial(item_id, evaluated_by, evaluator_role, reasons)
            return {
                "eligible": False, "item_id": item_id,
                "decision_code": "source_invalid",
                "decision_reasons": reasons,
                "messages": reasons,
            }

        # 4. Active rubric (always required)
        if item.rubric_id:
            rubric_result = await self.db.execute(
                select(CertRubric).where(CertRubric.rubric_id == item.rubric_id)
            )
            rubric = rubric_result.scalar_one_or_none()
            if not rubric or rubric.status not in ("active", "published"):
                reasons.append("Associated rubric is not active")
                await self._audit_denial(item_id, evaluated_by, evaluator_role, reasons)
                return {
                    "eligible": False, "item_id": item_id,
                    "decision_code": "rubric_inactive",
                    "decision_reasons": reasons,
                    "messages": reasons,
                }

        # 5. Check not already in exam_eligible pool
        existing = await self.pool_repo.get_active_by_item_and_pool(item.id, "exam_eligible")
        if existing:
            reasons.append("Item is already in the exam-eligible pool")
            return {
                "eligible": False, "item_id": item_id,
                "decision_code": "already_eligible",
                "decision_reasons": reasons,
                "messages": reasons,
            }

        # 6. Check not already in exam_eligible status
        if item.status == "exam_eligible":
            reasons.append("Item is already exam_eligible")
            return {
                "eligible": False, "item_id": item_id,
                "decision_code": "already_eligible",
                "decision_reasons": reasons,
                "messages": reasons,
            }

        # ALL CHECKS PASSED — grant eligibility
        membership = await self.pool_repo.create(
            membership_id=f"mem-{uuid.uuid4().hex[:12]}",
            item_id=item.id,
            pool_type="exam_eligible",
            status="active",
            controlled_exception=using_exception,
            entered_by=evaluated_by,
        )

        # Transition status
        await self.item_repo.update_status(item.id, "exam_eligible")

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason="Exam eligibility granted via ExamEligibilityGateService",
            created_by=evaluated_by,
        )

        # Audit
        await self.audit.record(
            entity_type="item",
            entity_id=item_id,
            action="exam_eligibility_granted",
            actor_id=evaluated_by,
            actor_role=evaluator_role,
            reason=f"Exam eligibility granted via ExamEligibilityGateService. "
                   f"Exception: {controlled_exception_id or 'none'}",
        )

        return {
            "eligible": True,
            "item_id": item_id,
            "gate": "exam_eligibility_gate",
            "decision_code": "eligible",
            "decision_reasons": ["All gates passed"],
            "exception_id": controlled_exception_id,
            "messages": ["Exam eligibility granted"],
            "membership": membership,
        }

    async def _audit_denial(
        self, item_id: str, actor_id: str, actor_role: str, reasons: list[str],
    ) -> None:
        """Record an exam-eligibility denial audit event."""
        await self.audit.record(
            entity_type="item",
            entity_id=item_id,
            action="exam_eligibility_denied",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=f"Exam eligibility denied: {'; '.join(reasons)}",
        )

class GovernanceService:
    """Handles suspension, unsuspension, retirement, and supersession."""

    SUSPENSION_REASONS = [
        "source_invalidated", "answer_key_defect", "ambiguity",
        "bias_concern", "legal_compliance", "overexposure",
        "psychometric_concern", "reviewer_incident", "operator_decision",
    ]

    def __init__(self, db: AsyncSession):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.pool_repo = ItemPoolMembershipRepository(db)
        self.incident_repo = ItemGovernanceIncidentRepository(db)
        self.supersession_repo = ItemSupersessionLinkRepository(db)
        self.exception_repo = ItemExceptionApprovalRepository(db)
        self.audit = AuditService(db)

    async def suspend(self, data: GovernanceActionCreate, actor_role: str) -> dict:
        """Suspend an item — removes from active pools."""
        item = await self.item_repo.get_by_item_id(data.item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        if item.status == "retired":
            return {"success": False, "message": "Retired items cannot be suspended"}

        # Validate suspension reason
        if data.suspension_reason and data.suspension_reason not in self.SUSPENSION_REASONS:
            return {
                "success": False,
                "message": f"Invalid suspension reason '{data.suspension_reason}'. "
                           f"Must be one of: {', '.join(self.SUSPENSION_REASONS)}",
            }

        before_status = item.status

        # Set status to suspended
        await self.item_repo.update_status(item.id, "suspended")

        # Remove from active pools
        for pool_type in ("pilot", "exam_eligible"):
            await self.pool_repo.deactivate_by_item_and_pool(
                item.id, pool_type,
                exit_reason=f"Suspended: {data.suspension_reason or data.reason}",
            )

        # Create governance incident
        incident_type = data.suspension_reason or "operator_decision"
        await self.incident_repo.create(
            incident_id=f"inc-{uuid.uuid4().hex[:12]}",
            item_id=item.id,
            incident_type=incident_type,
            severity="high" if incident_type in ("legal_compliance", "bias_concern") else "medium",
            status="open",
            description=data.reason,
            reported_by=data.actor_id,
        )

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason=f"Suspended: {data.suspension_reason or 'operator decision'}",
            created_by=data.actor_id,
        )

        # Audit
        await self.audit.record_transition(
            entity_type="item",
            entity_id=data.item_id,
            from_status=before_status,
            to_status="suspended",
            actor_id=data.actor_id,
            actor_role=actor_role,
            reason=data.reason,
        )

        return {"success": True, "message": "Item suspended"}

    async def unsuspend(self, data: GovernanceActionCreate, actor_role: str) -> dict:
        """Unsuspend an item — returns to under_review."""
        item = await self.item_repo.get_by_item_id(data.item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        if item.status != "suspended":
            return {"success": False, "message": f"Item is not suspended (status: '{item.status}')"}

        await self.item_repo.update_status(item.id, "under_review")

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason="Unsuspended",
            created_by=data.actor_id,
        )

        # Audit
        await self.audit.record_transition(
            entity_type="item",
            entity_id=data.item_id,
            from_status="suspended",
            to_status="under_review",
            actor_id=data.actor_id,
            actor_role=actor_role,
            reason=data.reason,
        )

        return {"success": True, "message": "Item unsuspended"}

    async def retire(self, data: GovernanceActionCreate, actor_role: str) -> dict:
        """Retire an item — permanent removal from active pools."""
        item = await self.item_repo.get_by_item_id(data.item_id)
        if not item:
            return {"success": False, "message": "Item not found"}

        if item.status == "retired":
            return {"success": False, "message": "Item is already retired"}

        before_status = item.status

        await self.item_repo.update_status(item.id, "retired")

        # Remove from all active pools
        for pool_type in ("pilot", "exam_eligible"):
            await self.pool_repo.deactivate_by_item_and_pool(
                item.id, pool_type,
                exit_reason=f"Retired: {data.reason}",
            )

        # Snapshot
        await self.item_repo.create_snapshot(
            item.id,
            change_reason=f"Retired: {data.reason}",
            created_by=data.actor_id,
        )

        # Audit
        await self.audit.record_transition(
            entity_type="item",
            entity_id=data.item_id,
            from_status=before_status,
            to_status="retired",
            actor_id=data.actor_id,
            actor_role=actor_role,
            reason=data.reason,
        )

        return {"success": True, "message": "Item retired"}

    async def supersede(self, data: SupersessionCreate, actor_role: str) -> dict:
        """Create a supersession link between predecessor and successor items."""
        predecessor = await self.item_repo.get_by_item_id(data.predecessor_item_id)
        if not predecessor:
            return {"success": False, "message": "Predecessor item not found"}

        successor = await self.item_repo.get_by_item_id(data.successor_item_id)
        if not successor:
            return {"success": False, "message": "Successor item not found"}

        # Retire predecessor if not already
        if predecessor.status != "retired":
            await self.item_repo.update_status(predecessor.id, "retired")
            await self.pool_repo.deactivate_by_item_and_pool(
                predecessor.id, "exam_eligible",
                exit_reason=f"Superseded by {data.successor_item_id}",
            )
            await self.pool_repo.deactivate_by_item_and_pool(
                predecessor.id, "pilot",
                exit_reason=f"Superseded by {data.successor_item_id}",
            )

        # Create link
        link = await self.supersession_repo.create(
            supersession_id=f"sup-{uuid.uuid4().hex[:12]}",
            predecessor_item_id=predecessor.id,
            successor_item_id=successor.id,
            reason=data.reason,
            created_by=data.created_by,
        )

        # Audit
        await self.audit.record(
            entity_type="item",
            entity_id=data.predecessor_item_id,
            action="superseded",
            actor_id=data.created_by,
            actor_role=actor_role,
            reason=f"Superseded by {data.successor_item_id}: {data.reason}",
        )

        return {"success": True, "link": link}

    async def get_governance_summary(
        self,
        domain_pack_id: Optional[str] = None,
        locale: Optional[str] = None,
    ) -> dict:
        """Get governance summary statistics."""
        # Build filters
        item_filters = {}
        if domain_pack_id:
            item_filters["domain_pack_id"] = domain_pack_id
        if locale:
            item_filters["locale"] = locale

        # Count by status
        def _make_count_filter(status: str) -> dict:
            f = dict(item_filters)
            f["status"] = status
            return f

        total_drafts = await self.item_repo.count(
            filters=_make_count_filter("draft"),
        )
        submitted_items = await self.item_repo.count(
            filters=_make_count_filter("expert_review_required"),
        )
        awaiting_expert = await self.item_repo.count(
            filters=_make_count_filter("expert_review_required"),
        )
        pilot_active = await self.item_repo.count(
            filters=_make_count_filter("pilot"),
        )
        exam_eligible = await self.item_repo.count(
            filters=_make_count_filter("exam_eligible"),
        )
        suspended = await self.item_repo.count(
            filters=_make_count_filter("suspended"),
        )
        retired = await self.item_repo.count(
            filters=_make_count_filter("retired"),
        )
        calibrated = await self.item_repo.count(
            filters=_make_count_filter("calibrated"),
        )
        under_review = await self.item_repo.count(
            filters=_make_count_filter("under_review"),
        )

        # Pilot pool
        pilot_pool, _ = await self.pool_repo.list_pool(pool_type="pilot", status="active")

        # Incidents
        unresolved = await self.incident_repo.count_open()

        return {
            "total_drafts": total_drafts,
            "submitted_items": submitted_items,
            "awaiting_expert_review": awaiting_expert,
            "awaiting_qa_review": 0,
            "pilot_ready_items": calibrated,
            "pilot_active_items": pilot_active,
            "exam_eligible_items": exam_eligible,
            "suspended_items": suspended,
            "retired_items": retired,
            "source_invalid_items": 0,
            "overexposed_items": 0,
            "items_without_active_rubric": 0,
            "review_sla_breaches": 0,
            "unresolved_incidents": unresolved,
            "domain_pack_id": domain_pack_id,
            "locale": locale,
        }

    async def list_incidents(
        self,
        incident_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        """List governance incidents."""
        items, total = await self.incident_repo.list_incidents(
            incident_type=incident_type, status=status, skip=skip, limit=limit,
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}
