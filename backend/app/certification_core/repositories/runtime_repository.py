"""Repositories for Dynamic Item Bank Runtime entities."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select, func, and_, or_, delete, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.runtime_models import (
    ItemSourceBinding,
    ItemReview,
    ItemReviewDecision,
    ItemPoolMembership,
    ItemExposureEvent,
    ItemExposureCounter,
    ItemRotationPolicy,
    ItemGovernanceIncident,
    ItemSupersessionLink,
    ItemExceptionApproval,
)
from app.certification_core.repositories.base import CertBaseRepository


class ItemSourceBindingRepository(CertBaseRepository[ItemSourceBinding]):
    """Repository for source traceability bindings."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemSourceBinding)

    async def get_by_binding_id(self, binding_id: str) -> Optional[ItemSourceBinding]:
        return await self.get_by_business_id(binding_id, id_field="binding_id")

    async def get_by_item(self, item_id: str) -> tuple[list[ItemSourceBinding], int]:
        return await self.list_all(filters={"item_id": item_id})

    async def count_by_item(self, item_id: str) -> int:
        return await self.count(filters={"item_id": item_id})


class ItemReviewRepository(CertBaseRepository[ItemReview]):
    """Repository for item reviews."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemReview)

    async def get_by_review_id(self, review_id: str) -> Optional[ItemReview]:
        return await self.get_by_business_id(review_id, id_field="review_id")

    async def list_reviews(
        self,
        item_id: Optional[str] = None,
        review_stage: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        decision: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ItemReview], int]:
        filters = {}
        if item_id:
            filters["item_id"] = item_id
        if review_stage:
            filters["review_stage"] = review_stage
        if reviewer_id:
            filters["reviewer_id"] = reviewer_id
        if decision:
            filters["decision"] = decision
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)

    async def get_review_queue(
        self,
        review_stage: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ItemReview], int]:
        filters = {"decision": "request_changes"}
        if review_stage:
            filters["review_stage"] = review_stage
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)


class ItemReviewDecisionRepository(CertBaseRepository[ItemReviewDecision]):
    """Repository for immutable review decision trail."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemReviewDecision)

    async def get_by_decision_id(self, decision_id: str) -> Optional[ItemReviewDecision]:
        return await self.get_by_business_id(decision_id, id_field="decision_id")

    async def get_by_review(self, review_id: str) -> tuple[list[ItemReviewDecision], int]:
        return await self.list_all(filters={"review_id": review_id})


class ItemPoolMembershipRepository(CertBaseRepository[ItemPoolMembership]):
    """Repository for pool memberships (pilot and exam-eligible)."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemPoolMembership)

    async def get_by_membership_id(self, membership_id: str) -> Optional[ItemPoolMembership]:
        return await self.get_by_business_id(membership_id, id_field="membership_id")

    async def get_active_by_item_and_pool(
        self, item_id: str, pool_type: str,
    ) -> Optional[ItemPoolMembership]:
        result = await self.db.execute(
            select(ItemPoolMembership)
            .where(ItemPoolMembership.item_id == item_id)
            .where(ItemPoolMembership.pool_type == pool_type)
            .where(ItemPoolMembership.status == "active")
        )
        return result.scalar_one_or_none()

    async def list_pool(
        self,
        pool_type: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ItemPoolMembership], int]:
        filters = {"pool_type": pool_type}
        if status:
            filters["status"] = status
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)

    async def deactivate(
        self, membership_id: str, exit_reason: str,
    ) -> Optional[ItemPoolMembership]:
        member = await self.get_by_id(membership_id)
        if member is None:
            return None
        member.status = "exited"
        member.exit_date = datetime.now(timezone.utc)
        member.exit_reason = exit_reason
        await self.db.flush()
        return member

    async def deactivate_by_item_and_pool(
        self, item_id: str, pool_type: str, exit_reason: str,
    ) -> Optional[ItemPoolMembership]:
        member = await self.get_active_by_item_and_pool(item_id, pool_type)
        if member is None:
            return None
        member.status = "exited"
        member.exit_date = datetime.now(timezone.utc)
        member.exit_reason = exit_reason
        await self.db.flush()
        return member


class ItemExposureEventRepository(CertBaseRepository[ItemExposureEvent]):
    """Repository for exposure events with idempotency."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemExposureEvent)

    async def get_by_event_id(self, event_id: str) -> Optional[ItemExposureEvent]:
        return await self.get_by_business_id(event_id, id_field="event_id")

    async def get_by_item_and_session(
        self, item_id: str, session_id: str,
    ) -> Optional[ItemExposureEvent]:
        result = await self.db.execute(
            select(ItemExposureEvent)
            .where(ItemExposureEvent.item_id == item_id)
            .where(ItemExposureEvent.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def exists(self, item_id: str, session_id: str) -> bool:
        result = await self.db.execute(
            select(func.count(ItemExposureEvent.id))
            .where(ItemExposureEvent.item_id == item_id)
            .where(ItemExposureEvent.session_id == session_id)
        )
        return (result.scalar() or 0) > 0

    async def count_by_item_in_window(
        self, item_id: str, since: datetime,
    ) -> int:
        result = await self.db.execute(
            select(func.count(ItemExposureEvent.id))
            .where(ItemExposureEvent.item_id == item_id)
            .where(ItemExposureEvent.exposure_timestamp >= since)
        )
        return result.scalar() or 0


class ItemExposureCounterRepository(CertBaseRepository[ItemExposureCounter]):
    """Repository for aggregated exposure counters."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemExposureCounter)

    async def get_by_item(self, item_id: str) -> Optional[ItemExposureCounter]:
        result = await self.db.execute(
            select(ItemExposureCounter)
            .where(ItemExposureCounter.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def increment(
        self, item_id: str, exposure_threshold: int = 50,
    ) -> ItemExposureCounter:
        """Atomic increment of exposure counter."""
        counter = await self.get_by_item(item_id)
        if counter is None:
            counter = ItemExposureCounter(
                item_id=item_id,
                total_exposures=1,
                rolling_window_exposures=1,
                last_exposure_timestamp=datetime.now(timezone.utc),
                exposure_threshold=exposure_threshold,
            )
            self.db.add(counter)
        else:
            counter.total_exposures = (counter.total_exposures or 0) + 1
            counter.rolling_window_exposures = (counter.rolling_window_exposures or 0) + 1
            counter.last_exposure_timestamp = datetime.now(timezone.utc)
            if (counter.total_exposures or 0) >= exposure_threshold:
                counter.overexposed = True
        await self.db.flush()
        return counter


class ItemRotationPolicyRepository(CertBaseRepository[ItemRotationPolicy]):
    """Repository for rotation policies."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemRotationPolicy)

    async def get_by_policy_id(self, policy_id: str) -> Optional[ItemRotationPolicy]:
        return await self.get_by_business_id(policy_id, id_field="policy_id")

    async def get_by_item(self, item_id: str) -> Optional[ItemRotationPolicy]:
        result = await self.db.execute(
            select(ItemRotationPolicy)
            .where(ItemRotationPolicy.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_by_domain_pack(self, domain_pack_id: str) -> tuple[list[ItemRotationPolicy], int]:
        return await self.list_all(filters={"domain_pack_id": domain_pack_id})


class ItemGovernanceIncidentRepository(CertBaseRepository[ItemGovernanceIncident]):
    """Repository for governance incidents."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemGovernanceIncident)

    async def get_by_incident_id(self, incident_id: str) -> Optional[ItemGovernanceIncident]:
        return await self.get_by_business_id(incident_id, id_field="incident_id")

    async def list_incidents(
        self,
        incident_type: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ItemGovernanceIncident], int]:
        filters = {}
        if incident_type:
            filters["incident_type"] = incident_type
        if status:
            filters["status"] = status
        if severity:
            filters["severity"] = severity
        return await self.list_all(skip=skip, limit=limit, filters=filters or None)

    async def count_open(self) -> int:
        return await self.count(filters={"status": "open"})


class ItemSupersessionLinkRepository(CertBaseRepository[ItemSupersessionLink]):
    """Repository for supersession links."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemSupersessionLink)

    async def get_by_supersession_id(self, supersession_id: str) -> Optional[ItemSupersessionLink]:
        return await self.get_by_business_id(supersession_id, id_field="supersession_id")

    async def get_by_predecessor(self, item_id: str) -> Optional[ItemSupersessionLink]:
        result = await self.db.execute(
            select(ItemSupersessionLink)
            .where(ItemSupersessionLink.predecessor_item_id == item_id)
        )
        return result.scalar_one_or_none()


class ItemExceptionApprovalRepository(CertBaseRepository[ItemExceptionApproval]):
    """Repository for controlled exception approvals."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ItemExceptionApproval)

    async def get_active_by_item(self, item_id: str) -> Optional[ItemExceptionApproval]:
        result = await self.db.execute(
            select(ItemExceptionApproval)
            .where(ItemExceptionApproval.item_id == item_id)
            .where(ItemExceptionApproval.is_active.is_(True))
            .where(ItemExceptionApproval.expires_at > datetime.now(timezone.utc))
        )
        return result.scalar_one_or_none()
