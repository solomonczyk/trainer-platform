"""Tests for generation source binding — validates source version binding enforcement."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.generation_models import GenerationSourceBinding
from app.certification_core.services.generation_service import GenerationService


class TestGenerationSourceBinding:
    """Prove source binding contract for generation requests."""

    @pytest.mark.asyncio
    async def test_source_binding_created(self, db: AsyncSession):
        service = GenerationService(db)
        req = await service.create_request(
            requested_by_user_id="user-001",
            requested_by_role="generation_operator",
            domain_id="domain-001",
            competency_id="comp-001",
            difficulty="medium",
            locale="en-US",
            item_family_id="family-001",
            provider="mock",
            model="mock-model",
        )
        bindings = await service.bind_sources(req.request_id, [
            {
                "source_version_id": "src-v1",
                "source_checksum": "abc123",
                "source_title": "Test Source",
                "source_locale": "en-US",
                "source_status": "active",
            }
        ])
        assert len(bindings) == 1
        assert bindings[0].source_version_id == "src-v1"
        assert bindings[0].source_checksum == "abc123"
        assert bindings[0].source_status == "active"

    @pytest.mark.asyncio
    async def test_execution_fails_without_source_binding(self, db: AsyncSession):
        service = GenerationService(db)
        req = await service.create_request(
            requested_by_user_id="user-001",
            requested_by_role="generation_operator",
            domain_id="domain-001",
            competency_id="comp-001",
            difficulty="medium",
            locale="en-US",
            item_family_id="family-001",
            provider="mock",
            model="mock-model",
        )
        # Authorize but don't bind sources
        await service.authorize_request(
            request_id=req.request_id,
            authorized_by="admin-001",
            authorized_role="platform_admin",
        )
        with pytest.raises(ValueError, match="No trusted source bindings"):
            await service.execute_generation(
                request_id=req.request_id,
                actor_id="admin-001",
                actor_role="platform_admin",
            )

    @pytest.mark.asyncio
    async def test_source_checksum_recorded(self, db: AsyncSession):
        service = GenerationService(db)
        req = await service.create_request(
            requested_by_user_id="user-001",
            requested_by_role="generation_operator",
            domain_id="domain-001",
            competency_id="comp-001",
            difficulty="medium",
            locale="en-US",
            item_family_id="family-001",
            provider="mock",
            model="mock-model",
        )
        bindings = await service.bind_sources(req.request_id, [
            {
                "source_version_id": "src-v1",
                "source_checksum": "sha256-abc123def456",
                "source_title": "Test Source",
                "source_locale": "en-US",
                "source_status": "active",
            }
        ])
        assert bindings[0].source_checksum == "sha256-abc123def456"

    @pytest.mark.asyncio
    async def test_multiple_source_bindings(self, db: AsyncSession):
        service = GenerationService(db)
        req = await service.create_request(
            requested_by_user_id="user-001",
            requested_by_role="generation_operator",
            domain_id="domain-001",
            competency_id="comp-001",
            difficulty="medium",
            locale="en-US",
            item_family_id="family-001",
            provider="mock",
            model="mock-model",
        )
        sources = [
            {"source_version_id": "src-v1", "source_checksum": "abc", "source_title": "Src 1", "source_locale": "en-US", "source_status": "active"},
            {"source_version_id": "src-v2", "source_checksum": "def", "source_title": "Src 2", "source_locale": "en-US", "source_status": "active"},
        ]
        bindings = await service.bind_sources(req.request_id, sources)
        assert len(bindings) == 2
        versions = [b.source_version_id for b in bindings]
        assert "src-v1" in versions
        assert "src-v2" in versions
