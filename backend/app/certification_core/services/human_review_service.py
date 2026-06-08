"""Human review service — review case lifecycle, assignment, decision workflow.

Implements the complete human review workflow for generated candidates:
PENDING_ASSIGNMENT → ASSIGNED → IN_REVIEW → decision outcome.

Enforces separation of duties, self-review blocking, LLM blocking,
and atomic audit events for every mutation.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.audit.service import AuditService
from app.certification_core.models.generation_models import (
    GeneratedCandidate,
    CandidateValidationRun,
    CandidateValidationResult,
    CandidateProvenance,
    CandidateReviewHandoff,
    GenerationSourceBinding,
    GenerationRequest,
)
from app.certification_core.models.human_review_models import (
    HumanReviewCase,
    ReviewerAssignment,
    HumanReviewDecision,
    REVIEW_CASE_STATUSES,
    REVIEW_DECISIONS,
    ASSIGNMENT_STATUSES,
    ELIGIBLE_REVIEWER_ROLES,
    PROHIBITED_REVIEWER_ROLES,
    SELF_REVIEW_BLOCKED_ROLES,
)
from app.certification_core.schemas.human_review_schemas import EvidenceSnapshot
from app.core.logging import get_logger

logger = get_logger(__name__)


class HumanReviewService:
    """Service for the human review vertical layer."""

    # Valid status transitions for review cases
    VALID_CASE_TRANSITIONS = {
        "PENDING_ASSIGNMENT": ["ASSIGNED", "CLOSED"],
        "ASSIGNED": ["IN_REVIEW", "CLOSED", "PENDING_ASSIGNMENT"],
        "IN_REVIEW": [
            "APPROVED_FOR_PILOT_REVIEW",
            "REJECTED",
            "CHANGES_REQUESTED",
            "ESCALATED",
            "CLOSED",
        ],
        "CHANGES_REQUESTED": ["IN_REVIEW", "CLOSED"],
        "REJECTED": ["CLOSED"],
        "APPROVED_FOR_PILOT_REVIEW": ["CLOSED"],
        "ESCALATED": ["CLOSED"],
        "CLOSED": [],
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _get_case_by_case_id(self, case_id: str) -> HumanReviewCase:
        """Get a review case by its case_id."""
        result = await self.db.execute(
            select(HumanReviewCase).where(HumanReviewCase.case_id == case_id)
        )
        case = result.scalar_one_or_none()
        if not case:
            raise ValueError(f"Review case not found: {case_id}")
        return case

    async def _get_assignment_by_assignment_id(
        self, assignment_id: str
    ) -> ReviewerAssignment:
        """Get an assignment by assignment_id."""
        result = await self.db.execute(
            select(ReviewerAssignment).where(
                ReviewerAssignment.assignment_id == assignment_id
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise ValueError(f"Assignment not found: {assignment_id}")
        return assignment

    async def _get_active_assignment_for_user(
        self, case_id: str, user_id: str
    ) -> Optional[ReviewerAssignment]:
        """Get an active assignment for a user in a case."""
        result = await self.db.execute(
            select(ReviewerAssignment).where(
                ReviewerAssignment.review_case_id == case_id,
                ReviewerAssignment.reviewer_user_id == user_id,
                ReviewerAssignment.status.in_(["ASSIGNED", "CLAIMED"]),
            )
        )
        return result.scalar_one_or_none()

    async def _get_latest_decision(
        self, case_id: str
    ) -> Optional[HumanReviewDecision]:
        """Get the latest decision for a case."""
        result = await self.db.execute(
            select(HumanReviewDecision)
            .where(HumanReviewDecision.review_case_id == case_id)
            .order_by(HumanReviewDecision.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Actor validation
    # ------------------------------------------------------------------

    async def _validate_actor_for_review(
        self,
        actor_id: str,
        actor_role: str,
        candidate_id: str | None = None,
    ) -> None:
        """Validate that an actor is allowed to participate in human review.

        Raises ValueError with a descriptive message if blocked.
        """
        # Anonymous blocked
        if actor_id == "guest" or not actor_id:
            raise ValueError("Anonymous review is blocked")

        # Learner blocked
        if actor_role == "learner" or actor_role == "registered_user":
            raise ValueError("Learner review is blocked")

        # Prohibited roles
        if actor_role in PROHIBITED_REVIEWER_ROLES:
            raise ValueError(
                f"Role '{actor_role}' is prohibited from performing human review"
            )

        # LLM / service account blocked
        if actor_id.startswith("llm:") or actor_id.startswith("service:"):
            raise ValueError("LLM and service account reviews are blocked")

        # Not an eligible reviewer role
        if actor_role not in ELIGIBLE_REVIEWER_ROLES:
            raise ValueError(
                f"Role '{actor_role}' is not eligible for human review. "
                f"Eligible roles: {ELIGIBLE_REVIEWER_ROLES}"
            )

    async def _validate_self_review(
        self,
        actor_id: str,
        actor_role: str,
        candidate_id: str,
    ) -> None:
        """Block self-review: generation operators and content authors
        cannot review candidates they were involved in creating.

        Also checks if the actor was the generation request creator.
        """
        # Get candidate
        result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.candidate_id == candidate_id
            )
        )
        candidate = result.scalar_one_or_none()
        if not candidate:
            return  # Let downstream validation handle it

        # Get generation request
        gr_result = await self.db.execute(
            select(GenerationRequest).where(
                GenerationRequest.id == candidate.generation_request_id
            )
        )
        gen_request = gr_result.scalar_one_or_none()
        if gen_request:
            # Candidate author / request creator self-review blocked
            if gen_request.requested_by_user_id == actor_id:
                raise ValueError(
                    "Self-review blocked: the candidate's generation request "
                    "creator cannot review their own generated candidate"
                )

        # Role-based self-review blocked
        if actor_role in SELF_REVIEW_BLOCKED_ROLES:
            raise ValueError(
                f"Self-review blocked: role '{actor_role}' cannot review "
                f"candidates from their own domain"
            )

        # Check if candidate has a provenance record with actor info
        prov_result = await self.db.execute(
            select(CandidateProvenance).where(
                CandidateProvenance.candidate_id == candidate.id
            )
        )
        provenance = prov_result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Review case creation
    # ------------------------------------------------------------------

    async def create_review_case(
        self,
        handoff_id: str,
        review_type: str = "expert_review",
        actor_id: str = "system",
        actor_role: str = "system",
    ) -> HumanReviewCase:
        """Create a review case from a valid handoff.

        Validates:
        - Handoff exists
        - Candidate exists
        - Candidate hash matches
        - Validation run exists
        - Validation decision allows human review
        - Provenance complete
        - Source bindings present

        Idempotent: repeated calls for the same handoff return the existing case.
        """
        # Get handoff
        ho_result = await self.db.execute(
            select(CandidateReviewHandoff).where(
                CandidateReviewHandoff.handoff_id == handoff_id
            )
        )
        handoff = ho_result.scalar_one_or_none()
        if not handoff:
            raise ValueError(f"Review handoff not found: {handoff_id}")

        # Check for existing case (idempotency) — use handoff.db_id, not external id
        existing = await self.db.execute(
            select(HumanReviewCase).where(
                HumanReviewCase.review_handoff_id == handoff.id
            ).where(
                HumanReviewCase.status.in_([
                    "PENDING_ASSIGNMENT", "ASSIGNED", "IN_REVIEW"
                ])
            )
        )
        existing_case = existing.scalar_one_or_none()
        if existing_case:
            logger.info(
                f"Review case already exists for handoff {handoff_id}: "
                f"{existing_case.case_id}"
            )
            return existing_case

        if handoff.status != "pending_human_review":
            raise ValueError(
                f"Invalid handoff status: {handoff.status}. "
                f"Expected 'pending_human_review'"
            )

        # Get candidate
        result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.id == handoff.candidate_id
            )
        )
        candidate = result.scalar_one_or_none()
        if not candidate:
            raise ValueError("Candidate not found for handoff")

        # Check candidate hash matches provenance
        prov_result = await self.db.execute(
            select(CandidateProvenance).where(
                CandidateProvenance.candidate_id == candidate.id
            )
        )
        provenance = prov_result.scalar_one_or_none()
        if not provenance:
            raise ValueError("Provenance not found for candidate")

        current_hash = self._compute_candidate_hash(candidate)
        if provenance.candidate_hash != current_hash:
            raise ValueError(
                "Candidate hash mismatch: candidate content has changed "
                "since generation"
            )

        # Get validation run
        vr_result = await self.db.execute(
            select(CandidateValidationRun).where(
                CandidateValidationRun.candidate_id == candidate.id
            ).order_by(CandidateValidationRun.created_at.desc()).limit(1)
        )
        validation_run = vr_result.scalar_one_or_none()
        if not validation_run:
            raise ValueError("No validation run found for candidate")

        # Validation decision must allow human review
        if validation_run.decision not in ("READY_FOR_HUMAN_REVIEW",):
            raise ValueError(
                f"Validation decision '{validation_run.decision}' does not "
                f"allow human review. Expected 'READY_FOR_HUMAN_REVIEW'"
            )

        # Check source bindings
        sb_result = await self.db.execute(
            select(GenerationSourceBinding).where(
                GenerationSourceBinding.generation_request_id ==
                candidate.generation_request_id
            )
        )
        source_bindings = sb_result.scalars().all()
        if not source_bindings:
            raise ValueError("No source bindings found for candidate's generation request")

        # Determine eligible reviewer roles from handoff
        allowed_roles = handoff.reviewer_roles_allowed or []
        if not allowed_roles:
            allowed_roles = ["platform_admin", "domain_owner", "psychometric_reviewer"]

        # Pick the first allowed role as the required role
        required_role = allowed_roles[0]

        case_id = f"rc-{uuid.uuid4().hex[:12]}"
        review_case = HumanReviewCase(
            case_id=case_id,
            candidate_id=candidate.id,
            review_handoff_id=handoff.id,
            validation_run_id=validation_run.id,
            status="PENDING_ASSIGNMENT",
            review_type=review_type,
            required_reviewer_role=required_role,
            created_by=actor_id,
        )
        self.db.add(review_case)
        await self.db.flush()

        # Mark handoff as in review
        handoff.status = "in_human_review"
        await self.db.flush()

        # Audit event
        await self.audit.record(
            entity_type="human_review_case",
            entity_id=case_id,
            action="review_case_created",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=f"Review case created from handoff {handoff_id}",
            after_state={
                "case_id": case_id,
                "candidate_id": candidate.candidate_id,
                "handoff_id": handoff_id,
                "status": "PENDING_ASSIGNMENT",
            },
        )

        logger.info(
            f"Review case {case_id} created for candidate "
            f"{candidate.candidate_id} from handoff {handoff_id}"
        )
        return review_case

    def _compute_candidate_hash(self, candidate: GeneratedCandidate) -> str:
        """Compute a hash of the candidate's content for integrity checking."""
        content = {
            "stem": candidate.stem,
            "options": candidate.options,
            "rationale": candidate.rationale,
            "rubric": candidate.rubric,
            "source_citations": candidate.source_citations,
        }
        serialized = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Case listing
    # ------------------------------------------------------------------

    async def list_cases(
        self,
        status: Optional[str] = None,
        reviewer_user_id: Optional[str] = None,
        required_reviewer_role: Optional[str] = None,
        assigned_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        actor_role: str | None = None,
    ) -> tuple[list[HumanReviewCase], int]:
        """List review cases with optional filters."""
        query = select(HumanReviewCase)
        count_query = select(func.count(HumanReviewCase.id))

        if status:
            query = query.where(HumanReviewCase.status == status)
            count_query = count_query.where(HumanReviewCase.status == status)
        if required_reviewer_role:
            query = query.where(
                HumanReviewCase.required_reviewer_role == required_reviewer_role
            )
            count_query = count_query.where(
                HumanReviewCase.required_reviewer_role == required_reviewer_role
            )

        # Filter by assignment (cases assigned to a specific reviewer)
        if reviewer_user_id or assigned_to:
            target_user = reviewer_user_id or assigned_to
            subquery = (
                select(ReviewerAssignment.review_case_id)
                .where(ReviewerAssignment.reviewer_user_id == target_user)
                .where(ReviewerAssignment.status.in_(["ASSIGNED", "CLAIMED"]))
                .subquery()
            )
            query = query.where(HumanReviewCase.id.in_(subquery))
            count_query = count_query.where(HumanReviewCase.id.in_(subquery))

        query = query.order_by(HumanReviewCase.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        count_result = await self.db.execute(count_query)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return list(items), total

    async def get_case_detail(self, case_id: str) -> dict:
        """Get full case detail with candidate info, assignments, decisions."""
        case = await self._get_case_by_case_id(case_id)

        # Get candidate
        cand_result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.id == case.candidate_id
            )
        )
        candidate = cand_result.scalar_one_or_none()

        # Get assignments
        assign_result = await self.db.execute(
            select(ReviewerAssignment).where(
                ReviewerAssignment.review_case_id == case.id
            ).order_by(ReviewerAssignment.assigned_at.desc())
        )
        assignments = assign_result.scalars().all()

        # Get decisions
        dec_result = await self.db.execute(
            select(HumanReviewDecision).where(
                HumanReviewDecision.review_case_id == case.id
            ).order_by(HumanReviewDecision.created_at.desc())
        )
        decisions = dec_result.scalars().all()

        cand_dict = None
        if candidate:
            cand_dict = {
                "candidate_id": candidate.candidate_id,
                "stem": candidate.stem,
                "item_type": candidate.item_type,
                "difficulty": candidate.difficulty,
                "locale": candidate.locale,
                "domain_id": candidate.domain_id,
                "competency_id": candidate.competency_id,
                "item_family_id": candidate.item_family_id,
                "status": candidate.status,
                "validation_status": candidate.validation_status,
                "provider": candidate.provider,
                "model": candidate.model,
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
            }

        return {
            "case_id": case.case_id,
            "candidate_id": case.candidate_id,
            "review_handoff_id": case.review_handoff_id,
            "validation_run_id": case.validation_run_id,
            "status": case.status,
            "review_type": case.review_type,
            "required_reviewer_role": case.required_reviewer_role,
            "created_by": case.created_by,
            "created_at": case.created_at,
            "opened_at": case.opened_at,
            "completed_at": case.completed_at,
            "version": case.version,
            "candidate": cand_dict,
            "assignments": [
                {
                    "assignment_id": a.assignment_id,
                    "reviewer_user_id": a.reviewer_user_id,
                    "reviewer_role": a.reviewer_role,
                    "assigned_by": a.assigned_by,
                    "assigned_at": a.assigned_at,
                    "claimed_at": a.claimed_at,
                    "released_at": a.released_at,
                    "status": a.status,
                    "reason": a.reason,
                }
                for a in assignments
            ],
            "decisions": [
                {
                    "decision_id": d.decision_id,
                    "decision": d.decision,
                    "reviewer_user_id": d.reviewer_user_id,
                    "reviewer_role": d.reviewer_role,
                    "reason": d.reason,
                    "findings_json": d.findings_json,
                    "candidate_hash": d.candidate_hash,
                    "correlation_id": d.correlation_id,
                    "created_at": d.created_at,
                }
                for d in decisions
            ],
        }

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    async def assign_reviewer(
        self,
        case_id: str,
        reviewer_user_id: str,
        reviewer_role: str,
        assigned_by: str,
        assigned_by_role: str,
        reason: Optional[str] = None,
    ) -> ReviewerAssignment:
        """Assign a human reviewer to a review case.

        Validates:
        - Case exists and is in PENDING_ASSIGNMENT or ASSIGNED status
        - Reviewer is eligible
        - Not self-assignment (reviewer != generation operator of this candidate)
        - No duplicate active assignment
        """
        case = await self._get_case_by_case_id(case_id)

        if case.status not in ("PENDING_ASSIGNMENT", "ASSIGNED", "IN_REVIEW"):
            raise ValueError(
                f"Cannot assign reviewer: case status is '{case.status}'. "
                f"Expected 'PENDING_ASSIGNMENT', 'ASSIGNED', or 'IN_REVIEW'"
            )

        # Check if case is completed
        if case.status == "CLOSED":
            raise ValueError("Cannot assign reviewer to a completed case")

        # Validate reviewer eligibility
        if reviewer_role not in ELIGIBLE_REVIEWER_ROLES:
            raise ValueError(
                f"Reviewer role '{reviewer_role}' is not eligible. "
                f"Eligible roles: {ELIGIBLE_REVIEWER_ROLES}"
            )

        # Block LLM / service account as reviewer
        if reviewer_user_id.startswith("llm:") or reviewer_user_id.startswith("service:"):
            raise ValueError("LLM and service account reviewers are blocked")

        # Block anonymous reviewer
        if not reviewer_user_id or reviewer_user_id == "guest":
            raise ValueError("Anonymous reviewer is blocked")

        # Self-review check: if the reviewer was the generation operator
        cand_result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.id == case.candidate_id
            )
        )
        candidate = cand_result.scalar_one_or_none()
        if candidate:
            gr_result = await self.db.execute(
                select(GenerationRequest).where(
                    GenerationRequest.id == candidate.generation_request_id
                )
            )
            gen_request = gr_result.scalar_one_or_none()
            if gen_request and gen_request.requested_by_user_id == reviewer_user_id:
                raise ValueError(
                    "Self-review blocked: the generation request creator "
                    "cannot review their own candidate"
                )

        # Check for existing active assignment
        existing = await self.db.execute(
            select(ReviewerAssignment).where(
                ReviewerAssignment.review_case_id == case.id,
                ReviewerAssignment.status.in_(["ASSIGNED", "CLAIMED"]),
            )
        )
        active = existing.scalar_one_or_none()
        if active:
            if active.reviewer_user_id == reviewer_user_id:
                # Same user — OK, already assigned
                return active
            raise ValueError(
                "An active assignment already exists for this case. "
                "Release the current assignment first."
            )

        assignment_id = f"ra-{uuid.uuid4().hex[:12]}"
        assignment = ReviewerAssignment(
            assignment_id=assignment_id,
            review_case_id=case.id,
            reviewer_user_id=reviewer_user_id,
            reviewer_role=reviewer_role,
            assigned_by=assigned_by,
            reason=reason,
            status="ASSIGNED",
        )
        self.db.add(assignment)

        # Update case status
        await self._transition_case_status(
            case, "ASSIGNED", assigned_by, assigned_by_role
        )
        await self.db.flush()

        # Audit
        await self.audit.record(
            entity_type="reviewer_assignment",
            entity_id=assignment_id,
            action="reviewer_assigned",
            actor_id=assigned_by,
            actor_role=assigned_by_role,
            reason=reason or f"Reviewer {reviewer_user_id} assigned to case {case_id}",
            after_state={
                "case_id": case_id,
                "reviewer_user_id": reviewer_user_id,
                "reviewer_role": reviewer_role,
                "status": "ASSIGNED",
            },
        )

        return assignment

    async def claim_assignment(
        self,
        case_id: str,
        actor_id: str,
        actor_role: str,
        reason: Optional[str] = None,
    ) -> ReviewerAssignment:
        """Claim an assignment. The reviewer claims their own active assignment."""
        case = await self._get_case_by_case_id(case_id)

        if case.status not in ("ASSIGNED", "PENDING_ASSIGNMENT"):
            raise ValueError(
                f"Cannot claim: case status is '{case.status}'. "
                f"Expected 'ASSIGNED' or 'PENDING_ASSIGNMENT'"
            )

        # Find active assignment for this user
        assignment = await self._get_active_assignment_for_user(case.id, actor_id)
        if not assignment:
            raise ValueError(
                f"No active assignment found for user {actor_id} in case {case_id}"
            )

        # Validate actor against assignment
        await self._validate_actor_for_review(actor_id, actor_role, case.candidate_id)

        # Set claimed
        assignment.status = "CLAIMED"
        assignment.claimed_at = datetime.now(timezone.utc)

        # Update case to IN_REVIEW
        case.opened_at = datetime.now(timezone.utc)
        await self._transition_case_status(
            case, "IN_REVIEW", actor_id, actor_role
        )
        await self.db.flush()

        # Audit
        await self.audit.record(
            entity_type="reviewer_assignment",
            entity_id=assignment.assignment_id,
            action="review_assignment_claimed",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason or f"Assignment claimed by reviewer {actor_id}",
            after_state={
                "case_id": case_id,
                "assignment_id": assignment.assignment_id,
                "status": "CLAIMED",
            },
        )

        await self.audit.record(
            entity_type="human_review_case",
            entity_id=case_id,
            action="review_started",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=f"Review started by {actor_id}",
        )

        return assignment

    async def release_assignment(
        self,
        case_id: str,
        actor_id: str,
        actor_role: str,
        reason: str,
    ) -> ReviewerAssignment:
        """Release/remove a reviewer from a case. Requires reason."""
        case = await self._get_case_by_case_id(case_id)

        if case.status == "CLOSED":
            raise ValueError("Cannot release assignment from a completed case")

        # Find active assignment for this case
        result = await self.db.execute(
            select(ReviewerAssignment).where(
                ReviewerAssignment.review_case_id == case.id,
                ReviewerAssignment.status.in_(["ASSIGNED", "CLAIMED"]),
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise ValueError("No active assignment found for this case")

        assignment.status = "RELEASED"
        assignment.released_at = datetime.now(timezone.utc)
        assignment.reason = reason

        # Reset case to PENDING_ASSIGNMENT
        await self._transition_case_status(
            case, "PENDING_ASSIGNMENT", actor_id, actor_role
        )
        case.opened_at = None
        await self.db.flush()

        # Audit
        await self.audit.record(
            entity_type="reviewer_assignment",
            entity_id=assignment.assignment_id,
            action="review_assignment_released",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason,
            after_state={
                "case_id": case_id,
                "assignment_id": assignment.assignment_id,
                "status": "RELEASED",
            },
        )

        return assignment

    async def _transition_case_status(
        self,
        case: HumanReviewCase,
        new_status: str,
        actor_id: str,
        actor_role: str,
    ) -> None:
        """Transition a review case to a new status with validation."""
        current = case.status
        allowed = self.VALID_CASE_TRANSITIONS.get(current, [])

        if new_status not in allowed:
            raise ValueError(
                f"Forbidden case transition: {current} → {new_status}. "
                f"Allowed from '{current}': {allowed}"
            )

        case.status = new_status
        if new_status in ("CLOSED",):
            case.completed_at = datetime.now(timezone.utc)

        case.version += 1
        await self.db.flush()

        # Audit transition
        await self.audit.record_transition(
            entity_type="human_review_case",
            entity_id=case.case_id,
            from_status=current,
            to_status=new_status,
            actor_id=actor_id,
            actor_role=actor_role,
            reason=f"Case status transition: {current} → {new_status}",
        )

    # ------------------------------------------------------------------
    # Decision
    # ------------------------------------------------------------------

    async def submit_decision(
        self,
        case_id: str,
        decision: str,
        reason: str,
        actor_id: str,
        actor_role: str,
        findings_json: Optional[dict] = None,
        evidence_confirmed: bool = False,
    ) -> HumanReviewDecision:
        """Submit a human review decision for a case.

        Validates:
        - Case exists and is in IN_REVIEW status
        - Actor has a claimed assignment
        - Decision value is valid
        - Evidence was confirmed
        - Candidate hash still matches
        - No duplicate decision exists
        - Actor is a validated human reviewer

        Creates an immutable decision record, updates case status,
        and writes audit events in a single transaction.
        """
        case = await self._get_case_by_case_id(case_id)

        if case.status != "IN_REVIEW":
            raise ValueError(
                f"Cannot submit decision: case status is '{case.status}'. "
                f"Expected 'IN_REVIEW'"
            )

        # Validate decision value
        if decision not in REVIEW_DECISIONS:
            raise ValueError(
                f"Invalid decision: '{decision}'. "
                f"Must be one of: {REVIEW_DECISIONS}"
            )

        # Validate actor
        await self._validate_actor_for_review(actor_id, actor_role, case.candidate_id)

        # Validate evidence confirmed
        if not evidence_confirmed:
            raise ValueError(
                "Evidence confirmation is required before submitting a decision"
            )

        # Find active claimed assignment for this reviewer
        assignment = await self._get_active_assignment_for_user(case.id, actor_id)
        if not assignment:
            raise ValueError(
                f"No active claimed assignment found for user {actor_id} in case {case_id}. "
                f"Reviewer must claim the assignment before submitting a decision."
            )

        if assignment.status != "CLAIMED":
            raise ValueError(
                f"Assignment must be CLAIMED before submitting a decision. "
                f"Current status: {assignment.status}"
            )

        # Check for duplicate decision
        existing = await self._get_latest_decision(case.id)
        if existing:
            raise ValueError(
                f"A decision has already been submitted for this case. "
                f"Decision ID: {existing.decision_id}, Decision: {existing.decision}"
            )

        # Re-check candidate hash
        result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.id == case.candidate_id
            )
        )
        candidate = result.scalar_one_or_none()
        if not candidate:
            raise ValueError("Candidate not found for case")

        current_hash = self._compute_candidate_hash(candidate)

        # Get provenance hash for comparison
        prov_result = await self.db.execute(
            select(CandidateProvenance).where(
                CandidateProvenance.candidate_id == candidate.id
            )
        )
        provenance = prov_result.scalar_one_or_none()
        expected_hash = provenance.candidate_hash if provenance else current_hash

        if current_hash != expected_hash:
            raise ValueError(
                "Candidate hash mismatch: candidate content has been modified "
                "since case was created. Review cannot proceed."
            )

        # Build evidence snapshot
        evidence = await self._build_evidence_snapshot(case, candidate)

        correlation_id = str(uuid.uuid4())

        decision_id = f"rd-{uuid.uuid4().hex[:12]}"
        review_decision = HumanReviewDecision(
            decision_id=decision_id,
            review_case_id=case.id,
            assignment_id=assignment.id,
            candidate_id=candidate.id,
            reviewer_user_id=actor_id,
            reviewer_role=actor_role,
            decision=decision,
            reason=reason,
            findings_json=findings_json,
            evidence_snapshot_json=evidence.model_dump() if evidence else None,
            candidate_hash=current_hash,
            validation_run_id=case.validation_run_id,
            correlation_id=correlation_id,
        )
        self.db.add(review_decision)

        # Mark assignment as completed
        assignment.status = "COMPLETED"

        # Update case status based on decision
        await self._transition_case_status(
            case, decision, actor_id, actor_role
        )

        await self.db.flush()

        # Audit
        await self.audit.record(
            entity_type="human_review_decision",
            entity_id=decision_id,
            action="review_decision_submitted",
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason,
            after_state={
                "case_id": case_id,
                "decision_id": decision_id,
                "decision": decision,
                "candidate_hash": current_hash,
            },
        )

        if decision == "ESCALATED":
            await self.audit.record(
                entity_type="human_review_case",
                entity_id=case_id,
                action="review_escalated",
                actor_id=actor_id,
                actor_role=actor_role,
                reason=reason,
            )

        logger.info(
            f"Decision {decision_id}: {decision} for case {case_id} "
            f"by reviewer {actor_id}"
        )

        return review_decision

    async def _build_evidence_snapshot(
        self,
        case: HumanReviewCase,
        candidate: GeneratedCandidate,
    ) -> EvidenceSnapshot:
        """Build a comprehensive evidence snapshot for a review decision."""
        # Get validation run
        vr_result = await self.db.execute(
            select(CandidateValidationRun).where(
                CandidateValidationRun.id == case.validation_run_id
            )
        )
        validation_run = vr_result.scalar_one_or_none()

        # Get validation results
        results_list = []
        if validation_run:
            res_result = await self.db.execute(
                select(CandidateValidationResult).where(
                    CandidateValidationResult.validation_run_id == validation_run.id
                )
            )
            results = res_result.scalars().all()
            results_list = [
                {
                    "validator_code": r.validator_code,
                    "validator_version": r.validator_version,
                    "status": r.status,
                    "severity": r.severity,
                }
                for r in results
            ]

        # Get provenance
        prov_result = await self.db.execute(
            select(CandidateProvenance).where(
                CandidateProvenance.candidate_id == candidate.id
            )
        )
        provenance = prov_result.scalar_one_or_none()

        # Get handoff
        ho_result = await self.db.execute(
            select(CandidateReviewHandoff).where(
                CandidateReviewHandoff.id == case.review_handoff_id
            )
        )
        handoff = ho_result.scalar_one_or_none()

        # Get source bindings
        sb_result = await self.db.execute(
            select(GenerationSourceBinding).where(
                GenerationSourceBinding.generation_request_id ==
                candidate.generation_request_id
            )
        )
        source_bindings = sb_result.scalars().all()

        return EvidenceSnapshot(
            candidate_id=candidate.candidate_id,
            candidate_hash=self._compute_candidate_hash(candidate),
            generation_request_id=candidate.generation_request_id,
            validation_run_id=case.validation_run_id,
            validation_decision=validation_run.decision if validation_run else None,
            validator_versions=provenance.validator_versions if provenance else None,
            provenance={
                "provider": provenance.provider if provenance else None,
                "model": provenance.model if provenance else None,
                "prompt_template_version": provenance.prompt_template_version if provenance else None,
                "generation_policy_version": provenance.generation_policy_version if provenance else None,
                "schema_version": provenance.schema_version if provenance else None,
                "candidate_hash": provenance.candidate_hash if provenance else None,
            } if provenance else None,
            source_bindings=[
                {
                    "source_version_id": sb.source_version_id,
                    "source_title": sb.source_title,
                    "source_locale": sb.source_locale,
                }
                for sb in source_bindings
            ] if source_bindings else [],
            citations=candidate.source_citations or [],
            duplicate_detection={
                "results": [
                    r for r in results_list
                    if r["validator_code"] == "V09"
                ],
            },
            safety_gate={
                "results": [
                    r for r in results_list
                    if r["validator_code"] == "V11"
                ],
            },
            review_handoff_id=case.review_handoff_id,
            review_handoff_status=handoff.status if handoff else None,
        )

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    async def get_review_history(self, case_id: str) -> list[dict]:
        """Get the full history of a review case from audit events."""
        case = await self._get_case_by_case_id(case_id)

        # Query audit events for this case
        events, _ = await self.audit.query(
            entity_type="human_review_case",
            entity_id=case_id,
            limit=100,
        )

        # Also get decision events
        dec_events, _ = await self.audit.query(
            entity_type="human_review_decision",
            entity_id=case_id,
            limit=50,
        )

        # Also get assignment events
        assign_events, _ = await self.audit.query(
            entity_type="reviewer_assignment",
            entity_id=case_id,
            limit=50,
        )

        # Also get decisions directly
        dec_result = await self.db.execute(
            select(HumanReviewDecision).where(
                HumanReviewDecision.review_case_id == case.id
            ).order_by(HumanReviewDecision.created_at.desc())
        )
        decisions = dec_result.scalars().all()

        history = []

        for event in events:
            history.append({
                "event_type": event.action,
                "actor_id": event.actor_id,
                "actor_role": event.actor_role,
                "previous_status": None,
                "new_status": None,
                "reason": event.reason,
                "correlation_id": None,
                "decision_id": None,
                "event_timestamp": event.event_timestamp,
            })

        for d in decisions:
            history.append({
                "event_type": "review_decision_submitted",
                "actor_id": d.reviewer_user_id,
                "actor_role": d.reviewer_role,
                "previous_status": "IN_REVIEW",
                "new_status": d.decision,
                "reason": d.reason,
                "correlation_id": d.correlation_id,
                "decision_id": d.decision_id,
                "event_timestamp": d.created_at,
            })

        # Sort by timestamp
        history.sort(key=lambda h: h["event_timestamp"], reverse=True)

        return history

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    async def get_evidence_snapshot(
        self, case_id: str
    ) -> Optional[EvidenceSnapshot]:
        """Get the evidence snapshot for a review case."""
        case = await self._get_case_by_case_id(case_id)

        result = await self.db.execute(
            select(GeneratedCandidate).where(
                GeneratedCandidate.id == case.candidate_id
            )
        )
        candidate = result.scalar_one_or_none()
        if not candidate:
            return None

        return await self._build_evidence_snapshot(case, candidate)
