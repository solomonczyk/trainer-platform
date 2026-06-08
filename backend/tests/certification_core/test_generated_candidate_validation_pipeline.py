"""Tests for the full validation pipeline — all 15 validators with versions and decision rules."""

from __future__ import annotations

import pytest

from app.certification_core.validators.generation_validators import (
    VALIDATOR_VERSIONS,
    VALIDATION_POLICY_VERSION,
    validate_schema,
    validate_required_fields,
    validate_source_citations,
    validate_competency_alignment,
    validate_difficulty,
    validate_item_family,
    validate_answer_consistency,
    validate_rubric,
    validate_ambiguity,
    validate_locale,
    validate_answer_key_leak,
    validate_provenance,
    validate_pool_mutation_guard,
)


class TestValidationPipeline:
    """Prove all 15 validators are registered and functional."""

    def test_all_validators_versioned(self):
        expected = {"V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
                    "V10", "V11", "V12", "V13", "V14", "V15"}
        assert set(VALIDATOR_VERSIONS.keys()) == expected
        for code, version in VALIDATOR_VERSIONS.items():
            assert version.startswith("1.") or version.startswith("2.")

    def test_v3_updated_to_v2(self):
        """V3 must be version 2.0.0 for corrective fix."""
        assert VALIDATOR_VERSIONS["V3"] == "2.0.0"

    def test_v10_updated_to_v2(self):
        """V10 must be version 2.0.0 for corrective fix."""
        assert VALIDATOR_VERSIONS["V10"] == "2.0.0"

    def test_validation_policy_version_updated(self):
        """Validation policy version must be 1.1.0."""
        assert VALIDATION_POLICY_VERSION == "1.1.0"

    def test_competency_mismatch_detected(self):
        candidate = {"competency_id": "comp-999", "domain_id": "domain-001"}
        result = validate_competency_alignment(candidate, "comp-001", "domain-001")
        assert result.status == "failed"
        assert result.reason_code == "COMPETENCY_MISMATCH"

    def test_difficulty_mismatch_detected(self):
        candidate = {"difficulty": "hard"}
        result = validate_difficulty(candidate, "easy")
        assert result.status == "failed"
        assert result.reason_code == "DIFFICULTY_MISMATCH"

    def test_item_family_mismatch_detected(self):
        candidate = {"item_family_id": "family-999"}
        result = validate_item_family(candidate, "family-001")
        assert result.status == "failed"

    def test_rubric_missing_criteria_warning(self):
        candidate = {"rubric": {}}
        result = validate_rubric(candidate)
        assert result.status in ("warning", "info")

    def test_locale_mismatch_detected(self):
        candidate = {"locale": "ru-RU"}
        result = validate_locale(candidate, "en-US")
        assert result.status == "failed"

    def test_answer_key_leak_detected(self):
        candidate = {
            "stem": "What is the correct answer?",
            "options": [{"id": "A", "text": "This is the (correct) answer"}],
            "answer_key": {"correct_option_id": "A"},
            "rationale": "Test",
        }
        result = validate_answer_key_leak(candidate)
        assert result.status == "failed"
        assert result.reason_code == "ANSWER_KEY_LEAK"

    def test_pool_mutation_guard_enforced(self):
        candidate = {"status": "validation_failed"}
        result = validate_pool_mutation_guard(candidate, "draft")
        assert result.status == "passed"

    def test_rubric_score_range_invalid(self):
        candidate = {
            "rubric": {
                "criteria": [
                    {"criterion_id": "c1", "name": "Test", "max_score": 0}
                ]
            }
        }
        result = validate_rubric(candidate)
        assert result.status == "failed"
        assert result.reason_code == "RUBRIC_SCORE_RANGE_INVALID"

    def test_provenance_missing_fields(self):
        provenance = {}
        result = validate_provenance(provenance)
        assert result.status == "failed"
        assert result.reason_code == "PROVENANCE_INCOMPLETE"

    def test_provenance_complete_passes(self):
        provenance = {
            "provider": "deepseek",
            "model": "deepseek-v4-flash",
            "prompt_template_version": "1.0.0",
            "generation_policy_version": "1.0.0",
            "schema_version": "1.0.0",
            "candidate_hash": "abc123",
        }
        result = validate_provenance(provenance)
        assert result.status == "passed"

    def test_missing_source_citations_warning(self):
        candidate = {}
        result = validate_source_citations(candidate, ["src-001"])
        assert result.status == "failed"

    def test_v3_citation_with_source_version_id_passes(self):
        """V3 must pass when source_version_id matches."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-001", "label": "Source One"},
            ],
        }
        result = validate_source_citations(candidate, ["src-001"])
        assert result.status == "passed"

    def test_v3_citation_with_mismatch_fails(self):
        """V3 must fail when no citation matches any expected source."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-999", "label": "Unknown"},
            ],
        }
        result = validate_source_citations(candidate, ["src-001", "src-002"])
        assert result.status == "failed"
