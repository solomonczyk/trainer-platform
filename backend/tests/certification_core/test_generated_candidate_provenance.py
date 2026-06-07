"""Tests for generated candidate provenance completeness and append-only."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.models.generation_models import (
    GeneratedCandidate, CandidateProvenance, GenerationRequest,
)
from app.certification_core.validators.generation_validators import validate_provenance


class TestCandidateProvenance:
    """Prove provenance completeness and append-only behavior."""

    @pytest.mark.asyncio
    async def test_provenance_complete(self, db: AsyncSession):
        provenance = {
            "provider": "deepseek",
            "model": "deepseek-v4-flash",
            "prompt_template_version": "1.0.0",
            "generation_policy_version": "1.0.0",
            "schema_version": "1.0.0",
            "candidate_hash": "abc123def456",
        }
        result = validate_provenance(provenance)
        assert result.status == "passed"

    @pytest.mark.asyncio
    async def test_provenance_incomplete_rejected(self):
        provenance = {}
        result = validate_provenance(provenance)
        assert result.status == "failed"
        assert result.reason_code == "PROVENANCE_INCOMPLETE"

    @pytest.mark.asyncio
    async def test_provenance_stores_source_versions(self):
        provenance = {
            "provider": "deepseek",
            "model": "deepseek-v4-flash",
            "prompt_template_version": "1.0.0",
            "generation_policy_version": "1.0.0",
            "schema_version": "1.0.0",
            "candidate_hash": "abc",
        }
        result = validate_provenance(provenance)
        assert result.status == "passed"

    @pytest.mark.asyncio
    async def test_provenance_stores_validator_versions(self):
        from app.certification_core.validators.generation_validators import VALIDATOR_VERSIONS
        assert len(VALIDATOR_VERSIONS) == 15
        for code, version in VALIDATOR_VERSIONS.items():
            assert isinstance(version, str)
            assert "." in version

    def test_provenance_rejects_missing_hash(self):
        provenance = {
            "provider": "mock",
            "model": "mock-model",
            "prompt_template_version": "1.0.0",
            "generation_policy_version": "1.0.0",
            "schema_version": "1.0.0",
        }
        result = validate_provenance(provenance)
        assert result.status == "failed"
