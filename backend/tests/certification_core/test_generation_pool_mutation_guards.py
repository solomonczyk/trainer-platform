"""Tests for pool mutation guards — preventing generated items from entering pilot/exam pools."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.certification_core.validators.generation_validators import validate_pool_mutation_guard
from app.certification_core.models.generation_models import GeneratedCandidate, CandidateReviewHandoff


class TestPoolMutationGuards:
    """Prove that generated candidates cannot enter pilot/exam pools."""

    def test_generated_cannot_enter_pilot(self):
        """Generated candidate cannot be added to pilot pool.

        The pool mutation guard correctly flags 'generated' status
        because it has forbidden transitions (generated → pilot_pool).
        """
        candidate = {"status": "generated"}
        result = validate_pool_mutation_guard(candidate, "draft")
        assert result.status == "failed"  # Forbidden transition generated → pilot_pool
        assert result.reason_code == "POOL_MUTATION_GUARD_VIOLATION"

    def test_generated_cannot_become_exam_eligible(self):
        candidate = {"status": "generated"}
        result = validate_pool_mutation_guard(candidate, "draft")
        assert result.status == "failed"
        assert result.reason_code == "POOL_MUTATION_GUARD_VIOLATION"

    def test_exam_assembly_unavailable(self):
        candidate = {"status": "validation_failed"}
        result = validate_pool_mutation_guard(candidate, "authorized")
        assert result.status == "passed"
        assert result.details.get("exam_assembly_blocked") is True

    def test_auto_publication_blocked(self):
        candidate = {"status": "validation_failed"}
        result = validate_pool_mutation_guard(candidate, "draft")
        assert result.status == "passed"
        assert result.details.get("auto_publication_blocked") is True

    @pytest.mark.asyncio
    async def test_review_handoff_blocks_pilot_and_exam(self, db: AsyncSession):
        """Review handoff model must block pilot and exam flags."""
        handoff = CandidateReviewHandoff(
            handoff_id="test-ho-001",
            candidate_id="test-cand-id",
            status="pending_human_review",
            pilot_allowed=False,
            exam_eligible_allowed=False,
            publication_allowed=False,
        )
        assert handoff.pilot_allowed is False
        assert handoff.exam_eligible_allowed is False
        assert handoff.publication_allowed is False
        # SQLAlchemy server_default fields default to None in Python
        assert handoff.human_review_completed in (None, False)
        assert handoff.human_accepted in (None, False)
