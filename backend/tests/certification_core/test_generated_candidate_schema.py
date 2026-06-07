"""Tests for generated candidate schema validation."""

from __future__ import annotations

import pytest

from app.certification_core.validators.generation_validators import (
    validate_schema,
    validate_required_fields,
    validate_answer_consistency,
)


class TestGeneratedCandidateSchema:
    """Prove candidate schema and field validation."""

    def test_valid_schema_passes(self):
        candidate = {
            "item_type": "multiple_choice",
            "stem": "What is QA?",
            "answer_key": {"correct_option_id": "A"},
            "rationale": "Because testing is important.",
        }
        result = validate_schema(candidate)
        assert result.status == "passed"

    def test_malformed_json_rejected(self):
        candidate = {}
        result = validate_schema(candidate)
        assert result.status == "failed"

    def test_missing_required_fields_rejected(self):
        candidate = {"item_type": "multiple_choice"}
        result = validate_required_fields(candidate)
        assert result.status == "failed"
        assert result.reason_code == "MISSING_REQUIRED_FIELDS"

    def test_invalid_item_type_rejected(self):
        candidate = {
            "item_type": "invalid_type",
            "stem": "Test",
            "answer_key": {},
            "rationale": "Test",
        }
        result = validate_schema(candidate)
        assert result.status == "failed"

    def test_partial_schema_not_accepted(self):
        candidate = {
            "stem": "Test only stem",
        }
        result = validate_schema(candidate)
        assert result.status == "failed"

    def test_empty_stem_rejected(self):
        candidate = {
            "item_type": "multiple_choice",
            "stem": "   ",
            "answer_key": {"correct_option_id": "A"},
            "rationale": "Test",
        }
        result = validate_required_fields(candidate)
        assert result.status == "failed"
        assert result.reason_code == "EMPTY_REQUIRED_FIELDS"

    def test_missing_answer_is_rejected(self):
        candidate = {
            "item_type": "multiple_choice",
            "stem": "Test question?",
            "answer_key": {},
            "rationale": "",
        }
        result = validate_required_fields(candidate)
        assert result.status == "failed" or result.status == "failed"

    def test_answer_not_in_options_rejected(self):
        candidate = {
            "item_type": "multiple_choice",
            "stem": "Test?",
            "options": [{"id": "A", "text": "Option A"}, {"id": "B", "text": "Option B"}],
            "answer_key": {"correct_option_id": "C"},
            "rationale": "Test",
        }
        result = validate_answer_consistency(candidate)
        assert result.status == "failed"
        assert result.reason_code == "ANSWER_NOT_IN_OPTIONS"

    def test_duplicate_options_rejected(self):
        candidate = {
            "item_type": "multiple_choice",
            "stem": "Test?",
            "options": [
                {"id": "A", "text": "Same text"},
                {"id": "B", "text": "Same text"},
            ],
            "answer_key": {"correct_option_id": "A"},
            "rationale": "Test",
        }
        result = validate_answer_consistency(candidate)
        assert result.status == "failed"
        assert result.reason_code == "DUPLICATE_OPTIONS"

    def test_empty_option_rejected(self):
        candidate = {
            "item_type": "multiple_choice",
            "stem": "Test?",
            "options": [
                {"id": "A", "text": "Valid option"},
                {"id": "B", "text": ""},
            ],
            "answer_key": {"correct_option_id": "A"},
            "rationale": "Test",
        }
        result = validate_answer_consistency(candidate)
        assert result.status == "failed"
        assert result.reason_code == "EMPTY_OPTION"
