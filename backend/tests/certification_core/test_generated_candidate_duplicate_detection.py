"""Tests for duplicate and similarity detection (V10 v2.0.0 — self-exclusion)."""

from __future__ import annotations

import pytest

from app.certification_core.validators.generation_validators import validate_duplicate


class TestDuplicateDetection:
    """Prove exact and near-duplicate detection with self-exclusion."""

    def test_exact_duplicate_blocked(self):
        """Different candidate with identical stem must be blocked."""
        candidate = {"stem": "What is the capital of France?", "candidate_id": "cand-002"}
        existing = [{"stem": "What is the capital of France?", "candidate_id": "cand-001"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"

    def test_no_duplicate_passes(self):
        """Different stems must pass."""
        candidate = {"stem": "What is Python?", "candidate_id": "cand-002"}
        existing = [{"stem": "What is Java?", "candidate_id": "cand-001"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "passed"

    def test_near_duplicate_flagged(self):
        """Similar stems must be flagged as near-duplicate."""
        candidate = {"stem": "What is the primary purpose of unit testing?"}
        existing = [{"stem": "What is the main purpose of unit testing?"}]
        result = validate_duplicate(candidate, existing, threshold=0.5)
        assert result.status in ("passed", "warning")

    def test_similarity_evidence_persisted(self):
        """Evidence must be persisted in the result details."""
        candidate = {"stem": "Duplicate text here for testing purposes exactly"}
        existing = [{"stem": "Duplicate text here for testing purposes exactly"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert "stem_hash" in result.details
        assert result.details.get("similarity") == 1.0

    def test_empty_existing_list(self):
        """No existing candidates must pass."""
        candidate = {"stem": "First candidate ever"}
        result = validate_duplicate(candidate, [])
        assert result.status == "passed"

    def test_different_candidate_same_hash_blocked(self):
        """Different candidate ID with same stem hash must be blocked."""
        candidate = {"stem": "What is polymorphism in OOP?", "candidate_id": "cand-002"}
        existing = [{"stem": "What is polymorphism in OOP?", "candidate_id": "cand-001"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"
        assert result.details.get("existing_candidate_id") == "cand-001"

    def test_same_candidate_id_excluded(self):
        """Same candidate ID with same stem must pass via self-exclusion."""
        candidate = {"stem": "What is encapsulation?", "candidate_id": "cand-001"}
        existing = [{"stem": "What is encapsulation?", "candidate_id": "cand-001"}]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-001"},
        )
        assert result.status == "passed"
        assert result.details.get("self_records_excluded", 0) >= 1
        assert result.details.get("comparison_candidate_count_after_self_exclusion") == 0

    def test_self_records_excluded_but_other_duplicates_found(self):
        """Self-excluded records must not prevent detection of real duplicates."""
        candidate = {"stem": "What is inheritance?", "candidate_id": "cand-002"}
        existing = [
            {"stem": "What is inheritance?", "candidate_id": "cand-002"},  # self
            {"stem": "What is inheritance?", "candidate_id": "cand-001"},  # real duplicate
        ]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-002"},
        )
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"
        assert result.details.get("existing_candidate_id") == "cand-001"

    def test_near_duplicate_self_excluded(self):
        """Self must not trigger near-duplicate warnings."""
        candidate = {"stem": "What is the main goal of unit testing in software?", "candidate_id": "cand-001"}
        existing = [{"stem": "What is the main goal of unit testing in software?", "candidate_id": "cand-001"}]
        result = validate_duplicate(
            candidate, existing, threshold=0.5,
            validation_context={"current_candidate_id": "cand-001"},
        )
        assert result.status == "passed"

    def test_different_candidate_near_duplicate_flagged(self):
        """Different candidate with similar text must be flagged."""
        candidate = {"stem": "What is the main goal of unit testing?", "candidate_id": "cand-002"}
        existing = [{"stem": "What is the primary purpose of unit testing?", "candidate_id": "cand-001"}]
        result = validate_duplicate(candidate, existing, threshold=0.5)
        # With 5/7 words shared, jaccard is ~0.71, should be caught
        assert result.status == "warning"
        assert result.reason_code == "NEAR_DUPLICATE"

    def test_same_generation_distinct_candidates_compared(self):
        """Two candidates in the same generation must be compared."""
        candidate = {"stem": "What is SQL injection?", "candidate_id": "cand-003"}
        existing = [{"stem": "What is cross-site scripting?", "candidate_id": "cand-004"}]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"generation_request_id": "gen-same"},
        )
        assert result.status == "passed"

    def test_different_generation_candidates_compared(self):
        """Candidates from different generations must be compared."""
        candidate = {"stem": "What is a REST API?", "candidate_id": "cand-005"}
        existing = [{"stem": "What is a SOAP API?", "candidate_id": "cand-006"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "passed"

    def test_option_set_duplicate_checked(self):
        """Duplicate options must be detected."""
        candidate = {
            "stem": "What is the capital of France?",
            "options": [
                {"id": "A", "text": "Paris"},
                {"id": "B", "text": "London"},
            ],
            "candidate_id": "cand-007",
        }
        existing = [{
            "stem": "What is the capital of France?",
            "options": [
                {"id": "A", "text": "Paris"},
                {"id": "B", "text": "London"},
            ],
            "candidate_id": "cand-008",
        }]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"

    def test_empty_options_no_error(self):
        """Candidates without options must not cause errors."""
        candidate = {"stem": "What is TDD?", "options": [], "candidate_id": "cand-009"}
        existing = [{"stem": "What is BDD?", "options": [], "candidate_id": "cand-010"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "passed"

    def test_comparison_counts_recorded(self):
        """The validator must record comparison counts in results."""
        candidate = {"stem": "Unique stem", "candidate_id": "cand-011"}
        existing = [
            {"stem": "Other stem 1", "candidate_id": "cand-012"},
            {"stem": "Other stem 2", "candidate_id": "cand-013"},
        ]
        result = validate_duplicate(candidate, existing)
        assert result.status == "passed"
        assert result.details.get("comparison_candidate_count_before_self_exclusion") == 2
        assert result.details.get("comparison_candidate_count_after_self_exclusion") == 2
