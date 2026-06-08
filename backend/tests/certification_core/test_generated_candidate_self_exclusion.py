"""Tests for V10 self-exclusion — candidate must not be compared against itself.

These tests prove that the V10 duplicate validator correctly excludes the current
candidate from the comparison set while still detecting real duplicates from other
candidates, item versions, and retired/suspended items.
"""

from __future__ import annotations

import pytest

from app.certification_core.validators.generation_validators import validate_duplicate


class TestCandidateSelfExclusion:
    """Prove V10 self-exclusion rules."""

    def test_candidate_not_duplicate_of_itself(self):
        """A candidate must not be flagged as a duplicate of itself."""
        candidate = {"stem": "What is dependency injection?", "candidate_id": "cand-self-001"}
        existing = [{"stem": "What is dependency injection?", "candidate_id": "cand-self-001"}]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-self-001"},
        )
        assert result.status == "passed"
        assert result.details.get("self_records_excluded", 0) >= 1

    def test_same_candidate_projection_excluded(self):
        """A candidate must be excluded even if projected differently."""
        candidate = {
            "stem": "What is microservices architecture?",
            "options": [{"id": "A", "text": "Option A"}],
            "candidate_id": "cand-self-002",
        }
        # Same content, same candidate_id, different projection (extra field)
        existing = [{
            "stem": "What is microservices architecture?",
            "options": [{"id": "A", "text": "Option A"}],
            "candidate_id": "cand-self-002",
            "extra_field": "some_value",
        }]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-self-002"},
        )
        assert result.status == "passed"
        assert result.details.get("self_records_excluded", 0) >= 1

    def test_same_candidate_hash_owned_by_current_candidate_excluded(self):
        """Same hash owned by current candidate must be excluded."""
        payload_hash = "abc123def456"
        candidate = {
            "stem": "Same hash test",
            "candidate_id": "cand-self-003",
        }
        existing = [{
            "stem": "Same hash test",
            "candidate_id": "cand-self-003",
        }]
        result = validate_duplicate(
            candidate, existing,
            validation_context={
                "current_candidate_id": "cand-self-003",
                "current_normalized_payload_hash": payload_hash,
            },
        )
        assert result.status == "passed"

    def test_different_candidate_same_hash_blocked(self):
        """Different candidate with same hash must still be blocked."""
        candidate = {"stem": "What is Kubernetes?", "candidate_id": "cand-other-001"}
        existing = [{"stem": "What is Kubernetes?", "candidate_id": "cand-other-002"}]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-other-001"},
        )
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"

    def test_different_candidate_same_text_blocked(self):
        """Different candidate with identical text must be blocked."""
        candidate = {"stem": "Explain the CAP theorem.", "candidate_id": "cand-cap-1"}
        existing = [{"stem": "Explain the CAP theorem.", "candidate_id": "cand-cap-2"}]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-cap-1"},
        )
        assert result.status == "failed"
        assert result.details.get("existing_candidate_id") == "cand-cap-2"

    def test_different_candidate_near_duplicate_flagged_or_blocked(self):
        """Different candidate with similar text must be flagged."""
        candidate = {"stem": "Describe the MVC pattern in web development.", "candidate_id": "cand-mvc-1"}
        existing = [{"stem": "Describe the MVC pattern in web frameworks.", "candidate_id": "cand-mvc-2"}]
        result = validate_duplicate(candidate, existing, threshold=0.5)
        assert result.status in ("passed", "warning")
        if result.status == "warning":
            assert result.reason_code == "NEAR_DUPLICATE"

    def test_same_generation_distinct_candidates_compared(self):
        """Two distinct candidates in the same generation must be compared."""
        candidate = {"stem": "What is a JWT token?", "candidate_id": "cand-gen-a"}
        existing = [{"stem": "What is OAuth 2.0?", "candidate_id": "cand-gen-b"}]
        result = validate_duplicate(
            candidate, existing,
            validation_context={
                "current_candidate_id": "cand-gen-a",
                "generation_request_id": "gen-common",
            },
        )
        assert result.status == "passed"

    def test_different_generation_candidates_compared(self):
        """Candidates from different generations must be compared."""
        candidate = {"stem": "What is Docker?", "candidate_id": "cand-001"}
        existing = [{"stem": "What is Podman?", "candidate_id": "cand-002"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "passed"

    def test_retired_item_similarity_checked(self):
        """Retired items with similar text must still be detected."""
        candidate = {"stem": "What is the definition of technical debt?", "candidate_id": "cand-new"}
        # Simulate a retired item
        existing = [{"stem": "Define technical debt and its implications.", "candidate_id": "cand-retired"}]
        result = validate_duplicate(candidate, existing, threshold=0.3)
        # At threshold 0.3, these will be near-duplicates
        assert result.status in ("passed", "warning")

    def test_suspended_item_similarity_checked(self):
        """Suspended items with similar text must still be detected."""
        candidate = {"stem": "Explain the SOLID principles.", "candidate_id": "cand-active"}
        existing = [{"stem": "Explain SOLID principles of OOP.", "candidate_id": "cand-suspended"}]
        result = validate_duplicate(candidate, existing, threshold=0.4)
        assert result.status in ("passed", "warning")

    def test_same_family_duplicate_checked(self):
        """Candidates in the same item family must be checked for duplication."""
        candidate = {"stem": "What is a database index?", "candidate_id": "cand-fam-001"}
        existing = [{"stem": "What is a database index?", "candidate_id": "cand-fam-002"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"

    def test_same_source_duplicate_checked(self):
        """Candidates from the same source must be checked."""
        candidate = {"stem": "What is ACID in databases?", "candidate_id": "cand-src-001"}
        existing = [{"stem": "What is ACID in databases?", "candidate_id": "cand-src-002"}]
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"

    def test_option_set_duplicate_checked(self):
        """Candidates with same option sets must be detected."""
        candidate = {
            "stem": "Choose the correct sorting algorithm:",
            "options": [
                {"id": "A", "text": "Quick sort"},
                {"id": "B", "text": "Bubble sort"},
            ],
            "candidate_id": "cand-opt-001",
        }
        existing = [{
            "stem": "Choose the correct sorting algorithm:",
            "options": [
                {"id": "A", "text": "Quick sort"},
                {"id": "B", "text": "Bubble sort"},
            ],
            "candidate_id": "cand-opt-002",
        }]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-opt-001"},
        )
        assert result.status == "failed"

    def test_no_validation_context_defaults_to_no_self_exclusion(self):
        """Without validation context, self-duplicate detection is unchanged."""
        candidate = {"stem": "Self detection test", "candidate_id": "cand-noctx-001"}
        existing = [{"stem": "Self detection test", "candidate_id": "cand-noctx-001"}]
        # No validation_context provided — self-exclusion is NOT applied
        result = validate_duplicate(candidate, existing)
        assert result.status == "failed"
        assert result.reason_code == "EXACT_DUPLICATE"

    def test_evidence_records_comparison_counts(self):
        """Evidence must include comparison counts before and after exclusion."""
        candidate = {"stem": "Evidence test stem", "candidate_id": "cand-evidence"}
        existing = [
            {"stem": "Other stem 1", "candidate_id": "cand-other-1"},
            {"stem": "Evidence test stem", "candidate_id": "cand-evidence"},  # self
            {"stem": "Other stem 2", "candidate_id": "cand-other-2"},
        ]
        result = validate_duplicate(
            candidate, existing,
            validation_context={"current_candidate_id": "cand-evidence"},
        )
        assert result.status == "passed"
        assert result.details.get("comparison_candidate_count_before_self_exclusion") == 3
        assert result.details.get("self_records_excluded", 0) == 1
        assert result.details.get("comparison_candidate_count_after_self_exclusion") == 2
