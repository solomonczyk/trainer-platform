"""Tests for the generation request contract — status transitions, forbidden transitions."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.generation_models import GenerationRequest
from app.certification_core.services.generation_service import GenerationService


class TestGenerationRequestContract:
    """Prove generation request contract behavior."""

    async def _create_draft_request(self, db: AsyncSession) -> GenerationRequest:
        service = GenerationService(db)
        return await service.create_request(
            requested_by_user_id="user-001",
            requested_by_role="generation_operator",
            domain_id="domain-001",
            competency_id="comp-001",
            difficulty="medium",
            locale="en-US",
            item_family_id="family-001",
            requested_candidate_count=1,
            provider="mock",
            model="mock-model",
        )

    @pytest.mark.asyncio
    async def test_create_request_defaults_to_draft(self, db: AsyncSession):
        req = await self._create_draft_request(db)
        assert req.status == "draft"
        assert req.requested_candidate_count == 1

    @pytest.mark.asyncio
    async def test_authorize_transition(self, db: AsyncSession):
        req = await self._create_draft_request(db)
        service = GenerationService(db)
        authorized = await service.authorize_request(
            request_id=req.request_id,
            authorized_by="admin-001",
            authorized_role="platform_admin",
        )
        assert authorized.status == "authorized"
        assert authorized.authorized_by == "admin-001"

    @pytest.mark.asyncio
    async def test_self_authorization_blocked(self, db: AsyncSession):
        req = await self._create_draft_request(db)
        service = GenerationService(db)
        with pytest.raises(PermissionError, match="self-authorization"):
            await service.authorize_request(
                request_id=req.request_id,
                authorized_by=req.requested_by_user_id,
                authorized_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_forbidden_transition_draft_to_generated(self, db: AsyncSession):
        req = await self._create_draft_request(db)
        service = GenerationService(db)
        with pytest.raises(ValueError, match="Forbidden transition"):
            await service._transition_status(req, "generated", "test", "test")

    @pytest.mark.asyncio
    async def test_forbidden_transition_draft_to_review_handoff(self, db: AsyncSession):
        req = await self._create_draft_request(db)
        service = GenerationService(db)
        with pytest.raises(ValueError, match="Forbidden transition"):
            await service._transition_status(req, "review_handoff_ready", "test", "test")

    @pytest.mark.asyncio
    async def test_valid_transition_chain(self, db: AsyncSession):
        req = await self._create_draft_request(db)
        service = GenerationService(db)

        # draft -> authorized
        req.status = "authorized"
        await db.flush()

        # authorized -> generating
        await service._transition_status(req, "generating", "admin", "platform_admin")
        assert req.status == "generating"

    @pytest.mark.asyncio
    async def test_max_candidates_enforced(self, db: AsyncSession):
        """Max 3 candidates enforced at service level."""
        service = GenerationService(db)
        req = await service.create_request(
            requested_by_user_id="user-001",
            requested_by_role="generation_operator",
            domain_id="domain-001",
            competency_id="comp-001",
            difficulty="medium",
            locale="en-US",
            item_family_id="family-001",
            requested_candidate_count=10,  # Exceeds max
            provider="mock",
            model="mock-model",
        )
        assert req.requested_candidate_count <= 3
        assert req.requested_candidate_count == 3  # Clamped to max
