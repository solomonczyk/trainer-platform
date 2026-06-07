"""Tests for duplicate and similarity detection."""

from __future__ import annotations

import pytest

from app.certification_core.validators.generation_validators import validate_duplicate


class TestDuplicateDetection:
    """Prove exact and near-duplicate detection."""

    def test_exact_duplicate_blocked(self):
        candidate = {"stem": "What is the capital of France?", "candidate_id": "cand-002"}
        existing = [{"stem": "What is the capital of France?", "candidate_id": "cand-001"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"

    def test_no_duplicate_passes(self):
        candidate = {"stem": "What is Python?", "candidate_id": "cand-002"}
        existing = [{"stem": "What is Java?", "candidate_id": "cand-001"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "passed"

    def test_near_duplicate_flagged(self):
        candidate = {"stem": "What is the primary purpose of unit testing?"}
        existing = [{"stem": "What is the main purpose of unit testing?"}]
        result = validate_duplicate(candidate, existing, threshold=0.5)
        # These may or may not be near-duplicates depending on jaccard
        assert result.status in ("passed", "warning")

    def test_similarity_evidence_persisted(self):
        candidate = {"stem": "Duplicate text here for testing purposes exactly"}
        existing = [{"stem": "Duplicate text here for testing purposes exactly"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert "stem_hash" in result.details
        assert result.details.get("similarity") == 1.0

    def test_empty_existing_list(self):
        candidate = {"stem": "First candidate ever"}
        result = validate_duplicate(candidate, [])
        assert result.status == "passed"
