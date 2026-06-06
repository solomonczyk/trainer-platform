"""Tests for the deterministic validator layer.

Validates all five activity type validators:
- single_choice: exact option comparison
- multiple_choice: order-independent set comparison with partial/extra rejection
- numeric: exact or tolerance-based comparison
- fill_blanks: ordered blank comparison with normalization
- matching: exact pair mapping, order-independent, unknown-key rejection
"""
from __future__ import annotations

import pytest

from app.modules.activities.validators.single_choice import validate_single_choice
from app.modules.activities.validators.multiple_choice import validate_multiple_choice
from app.modules.activities.validators.numeric import validate_numeric
from app.modules.activities.validators.fill_blanks import validate_fill_blanks
from app.modules.activities.validators.matching import validate_matching
from app.modules.activities.validators.registry import validate, get_validator, VALIDATORS


# ==============================================================================
# Registry tests
# ==============================================================================

class TestRegistry:
    def test_all_five_validators_registered(self):
        assert set(VALIDATORS.keys()) == {"single_choice", "multiple_choice", "numeric", "fill_blanks", "matching"}

    def test_get_validator_returns_function(self):
        for type_name in VALIDATORS:
            fn = get_validator(type_name)
            assert callable(fn)

    def test_get_validator_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown activity type"):
            get_validator("nonexistent")

    def test_validate_dispatches_correctly(self):
        result = validate("B", {"options": ["A", "B"], "correct": "B"}, "single_choice")
        assert result["status"] == "correct"

    def test_validate_unknown_type_raises(self):
        with pytest.raises(ValueError):
            validate("answer", {}, "unknown_type")

    def test_validator_result_contract(self):
        """All validators must return the standard result contract keys."""
        result = validate_single_choice("A", {"correct": "A"})
        assert set(result.keys()) >= {"status", "score", "passed", "feedback", "evaluation_mode", "validation_status"}
        assert result["evaluation_mode"] == "deterministic"
        assert result["validation_status"] == "validated"


# ==============================================================================
# Single Choice Validator
# ==============================================================================

class TestSingleChoiceValidator:
    def test_correct_answer(self):
        result = validate_single_choice("Paris", {"correct": "Paris"})
        assert result["status"] == "correct"
        assert result["score"] == 100
        assert result["passed"] is True

    def test_incorrect_answer(self):
        result = validate_single_choice("London", {"correct": "Paris"})
        assert result["status"] == "incorrect"
        assert result["score"] == 0
        assert result["passed"] is False

    def test_whitespace_insensitive(self):
        result = validate_single_choice("  Paris  ", {"correct": "Paris"})
        assert result["status"] == "correct"

    def test_empty_answer(self):
        result = validate_single_choice("", {"correct": "Paris"})
        assert result["status"] == "incorrect"

    def test_none_answer(self):
        result = validate_single_choice(None, {"correct": "Paris"})
        assert result["status"] == "incorrect"

    def test_missing_correct_in_payload(self):
        result = validate_single_choice("A", {})
        assert result["status"] == "incorrect"

    def test_case_sensitive(self):
        result = validate_single_choice("paris", {"correct": "Paris"})
        assert result["status"] == "incorrect"


# ==============================================================================
# Multiple Choice Validator
# ==============================================================================

class TestMultipleChoiceValidator:
    def test_correct_all_options_selected(self):
        result = validate_multiple_choice(["A", "B"], {"correct": ["A", "B"]})
        assert result["status"] == "correct"
        assert result["score"] == 100
        assert result["passed"] is True

    def test_correct_order_independent(self):
        result = validate_multiple_choice(["B", "A"], {"correct": ["A", "B"]})
        assert result["status"] == "correct"

    def test_partial_selection(self):
        result = validate_multiple_choice(["A"], {"correct": ["A", "B", "C"]})
        assert result["status"] == "partial"
        assert result["score"] == 33  # 1/3 = 33%
        assert result["passed"] is False

    def test_extra_options_rejected(self):
        result = validate_multiple_choice(["A", "B", "C"], {"correct": ["A", "B"]})
        assert result["status"] == "incorrect"
        assert result["score"] == 0
        assert "extra_options" in result["feedback"]

    def test_empty_selection(self):
        result = validate_multiple_choice([], {"correct": ["A", "B"]})
        assert result["status"] == "incorrect"
        assert result["score"] == 0

    def test_none_answer(self):
        result = validate_multiple_choice(None, {"correct": ["A"]})
        assert result["status"] == "incorrect"

    def test_single_correct_option(self):
        result = validate_multiple_choice(["A"], {"correct": ["A"]})
        assert result["status"] == "correct"
        assert result["score"] == 100

    def test_missing_correct_in_payload(self):
        result = validate_multiple_choice(["A"], {})
        assert result["status"] == "incorrect"

    def test_whitespace_trimmed(self):
        result = validate_multiple_choice(["  A  ", "  B  "], {"correct": ["A", "B"]})
        assert result["status"] == "correct"


# ==============================================================================
# Numeric Validator
# ==============================================================================

class TestNumericValidator:
    def test_exact_match(self):
        result = validate_numeric(42, {"correct": 42})
        assert result["status"] == "correct"
        assert result["score"] == 100
        assert result["passed"] is True

    def test_string_number(self):
        result = validate_numeric("42", {"correct": 42})
        assert result["status"] == "correct"

    def test_float_equivalence(self):
        result = validate_numeric(42.0, {"correct": 42})
        assert result["status"] == "correct"

    def test_incorrect_number(self):
        result = validate_numeric(41, {"correct": 42})
        assert result["status"] == "incorrect"
        assert result["score"] == 0

    def test_with_tolerance(self):
        result = validate_numeric(44, {"correct": 42, "tolerance": 2})
        assert result["status"] == "correct"

    def test_exceeds_tolerance(self):
        result = validate_numeric(45, {"correct": 42, "tolerance": 2})
        assert result["status"] == "incorrect"

    def test_zero_tolerance(self):
        result = validate_numeric(42.1, {"correct": 42, "tolerance": 0})
        assert result["status"] == "incorrect"

    def test_invalid_format(self):
        result = validate_numeric("not_a_number", {"correct": 42})
        assert result["status"] == "incorrect"

    def test_none_answer(self):
        result = validate_numeric(None, {"correct": 42})
        assert result["status"] == "incorrect"

    def test_missing_correct(self):
        result = validate_numeric(42, {})
        assert result["status"] == "incorrect"


# ==============================================================================
# Fill Blanks Validator
# ==============================================================================

class TestFillBlanksValidator:
    def test_all_correct(self):
        result = validate_fill_blanks(
            {"blank_0": "Scrum", "blank_1": "Agile"},
            {
                "correct": ["Scrum", "Agile"],
                "blanks": [{"id": "blank_0"}, {"id": "blank_1"}],
            },
        )
        assert result["status"] == "correct"
        assert result["score"] == 100
        assert result["passed"] is True

    def test_partial_correct(self):
        result = validate_fill_blanks(
            {"blank_0": "Scrum", "blank_1": "Waterfall"},
            {
                "correct": ["Scrum", "Agile"],
                "blanks": [{"id": "blank_0"}, {"id": "blank_1"}],
            },
        )
        assert result["status"] == "partial"
        assert result["score"] == 50
        assert result["passed"] is False

    def test_all_incorrect(self):
        result = validate_fill_blanks(
            {"blank_0": "Waterfall", "blank_1": "XP"},
            {
                "correct": ["Scrum", "Agile"],
                "blanks": [{"id": "blank_0"}, {"id": "blank_1"}],
            },
        )
        assert result["status"] == "incorrect"
        assert result["score"] == 0

    def text_normalization(self):
        """Whitespace normalization should match."""
        result = validate_fill_blanks(
            {"blank_0": "  scrum  "},
            {
                "correct": ["Scrum"],
                "blanks": [{"id": "blank_0"}],
            },
        )
        assert result["status"] == "correct"

    def test_empty_answer(self):
        result = validate_fill_blanks({}, {"correct": ["Scrum"], "blanks": [{"id": "blank_0"}]})
        assert result["status"] == "incorrect"

    def test_none_answer(self):
        result = validate_fill_blanks(None, {"correct": ["Scrum"]})
        assert result["status"] == "incorrect"

    def test_missing_correct(self):
        result = validate_fill_blanks({"blank_0": "Scrum"}, {})
        assert result["status"] == "incorrect"

    def test_wrong_type_answer(self):
        result = validate_fill_blanks("not_a_dict", {"correct": ["Scrum"]})
        assert result["status"] == "incorrect"


# ==============================================================================
# Matching Validator
# ==============================================================================

class TestMatchingValidator:
    def test_all_correct(self):
        result = validate_matching(
            {"A": "1", "B": "2"},
            {
                "pairs": [
                    {"left": "A", "right": "1"},
                    {"left": "B", "right": "2"},
                ],
            },
        )
        assert result["status"] == "correct"
        assert result["score"] == 100
        assert result["passed"] is True

    def test_order_independent(self):
        """Matching should be order-independent (checked by left-key)."""
        result = validate_matching(
            {"B": "2", "A": "1"},
            {
                "pairs": [
                    {"left": "A", "right": "1"},
                    {"left": "B", "right": "2"},
                ],
            },
        )
        assert result["status"] == "correct"

    def test_partial_correct(self):
        result = validate_matching(
            {"A": "1", "B": "3"},
            {
                "pairs": [
                    {"left": "A", "right": "1"},
                    {"left": "B", "right": "2"},
                    {"left": "C", "right": "3"},
                ],
            },
        )
        assert result["status"] == "partial"
        assert result["score"] == 33  # 1/3 done
        assert result["passed"] is False

    def test_unknown_key_rejected(self):
        result = validate_matching(
            {"A": "1", "X": "2"},
            {
                "pairs": [
                    {"left": "A", "right": "1"},
                    {"left": "B", "right": "2"},
                ],
            },
        )
        assert result["status"] == "incorrect"
        assert result["score"] == 0
        assert "unknown_keys" in result["feedback"]

    def test_list_input(self):
        result = validate_matching(
            [{"left": "A", "right": "1"}, {"left": "B", "right": "2"}],
            {
                "pairs": [
                    {"left": "A", "right": "1"},
                    {"left": "B", "right": "2"},
                ],
            },
        )
        assert result["status"] == "correct"

    def test_empty_answer(self):
        result = validate_matching({}, {"pairs": [{"left": "A", "right": "1"}]})
        assert result["status"] == "incorrect"

    def test_none_answer(self):
        result = validate_matching(None, {"pairs": [{"left": "A", "right": "1"}]})
        assert result["status"] == "incorrect"

    def test_missing_pairs_in_payload(self):
        result = validate_matching({"A": "1"}, {})
        assert result["status"] == "incorrect"

    def test_wrong_type_answer(self):
        result = validate_matching("string", {"pairs": [{"left": "A", "right": "1"}]})
        assert result["status"] == "incorrect"
