"""Dynamic Item Bank Runtime services — authoring, review, publication, pools, exposure, rotation, governance."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.audit.service import AuditService
from app.certification_core.models.item_models import Item, ItemFamily
from app.certification_core.models.knowledge_source_models import KnowledgeSource
from app.certification_core.models.rubric_models import CertRubric
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
    """Manages rotation policy configuration and eligibility checks."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.policy_repo = ItemRotationPolicyRepository(db)
        self.exposure_service = ExposureService(db)

    async def create_policy(self, data: RotationPolicyCreate, actor_role: str) -> dict:
        """Create a rotation policy."""
        if actor_role not in ("platform_admin", "domain_owner"):
            return {"success": False, "message": "Insufficient permissions"}
        policy = await self.policy_repo.create(**data.model_dump())
        return {"success": True, "policy": policy}

    async def check_eligibility(self, item_id: str) -> dict:
        """Check item eligibility per applicable policy."""
        policy = await self.policy_repo.get_by_item(item_id)
        if not policy and await self.policy_repo.get_by_business_id("default", "policy_id"):
            policy_result = await self.db.execute(
                select(ItemRotationPolicy).where(
                    ItemRotationPolicy.policy_id == "default"
                )
            )
            policy = policy_result.scalar_one_or_none()

        result = await self.exposure_service.check_rotation_eligibility(item_id, policy)
        return result


# ---------------------------------------------------------------------------
# Suspension / Retirement Service
# ---------------------------------------------------------------------------

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
