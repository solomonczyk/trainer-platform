"""Tests for rubric versioning contracts and weight validation."""

from __future__ import annotations

import pytest
from app.certification_core.validators.rubric_validator import RubricValidator


class TestRubricValidator:
    """Rubric validation tests — including total weight = 100 enforcement."""

    def test_valid_rubric(self):
        data = {
            "rubric_id": "test.rubric.1",
            "version": "1.0",
            "created_by": "test_user",
            "criteria": [
                {"criterion_id": "crit.1", "name": "Clarity", "weight": 40.0},
                {"criterion_id": "crit.2", "name": "Accuracy", "weight": 60.0},
            ],
        }
        errors = RubricValidator.validate_rubric(data)
        assert len(errors) == 0

    def test_total_weight_must_equal_100(self):
        data = {
            "rubric_id": "test.weight",
            "version": "1.0",
            "created_by": "user",
            "criteria": [
                {"criterion_id": "crit.1", "name": "Clarity", "weight": 30.0},
                {"criterion_id": "crit.2", "name": "Accuracy", "weight": 30.0},
            ],
        }
        errors = RubricValidator.validate_rubric(data)
        assert any("must equal 100" in e["message"] for e in errors)

    def test_single_criterion_weight_100(self):
        data = {
            "rubric_id": "test.single",
            "version": "1.0",
            "created_by": "user",
            "criteria": [
                {"criterion_id": "crit.1", "name": "Overall", "weight": 100.0},
            ],
        }
        errors = RubricValidator.validate_rubric(data)
        assert len(errors) == 0

    def test_missing_criteria(self):
        data = {
            "rubric_id": "test.nocriteria",
            "version": "1.0",
            "created_by": "user",
            "criteria": [],
        }
        errors = RubricValidator.validate_rubric(data)
        assert any("At least one criterion" in e["message"] for e in errors)

    def test_criterion_weight_zero(self):
        data = {
            "criterion_id": "crit.1",
            "name": "Test",
            "weight": 0,
        }
        errors = RubricValidator.validate_criterion(data)
        assert any("weight must be greater than 0" in e["message"] for e in errors)

    def test_criterion_weight_negative(self):
        data = {
            "criterion_id": "crit.1",
            "name": "Test",
            "weight": -10,
        }
        errors = RubricValidator.validate_criterion(data)
        assert any("weight" in e["message"].lower() and "0" in e["message"] for e in errors)

    def test_criterion_missing_required(self):
        errors = RubricValidator.validate_criterion({})
        field_names = {e["field"] for e in errors}
        assert "criterion_id" in field_names
        assert "name" in field_names

    def test_duplicate_criterion_ids(self):
        data = {
            "rubric_id": "test.dup",
            "version": "1.0",
            "created_by": "user",
            "criteria": [
                {"criterion_id": "crit.1", "name": "First", "weight": 50.0},
                {"criterion_id": "crit.1", "name": "Duplicate", "weight": 50.0},
            ],
        }
        errors = RubricValidator.validate_rubric(data)
        assert any("Duplicate criterion_id" in e["message"] for e in errors)

    def test_criterion_over_100(self):
        data = {
            "criterion_id": "crit.1",
            "name": "Test",
            "weight": 150,
        }
        errors = RubricValidator.validate_criterion(data)
        assert any("weight must be <= 100" in e["message"] for e in errors)

    def test_valid_statuses(self):
        for status in ["draft", "active", "deprecated", "retired"]:
            data = {
                "rubric_id": f"test.{status}",
                "version": "1.0",
                "created_by": "user",
                "status": status,
                "criteria": [
                    {"criterion_id": "crit.1", "name": "C1", "weight": 100.0},
                ],
            }
            errors = RubricValidator.validate_rubric(data)
            assert len(errors) == 0, f"Status '{status}' should be valid"

    def test_criterion_levels(self):
        data = {
            "criterion_id": "crit.levels",
            "name": "Test with levels",
            "weight": 50.0,
            "levels": {"0": "Poor", "1": "Fair", "2": "Good", "3": "Excellent"},
        }
        errors = RubricValidator.validate_criterion(data)
        assert len(errors) == 0

    def test_to_validation_result(self):
        errors = [{"field": "test", "message": "e"}]
        result = RubricValidator.to_validation_result(errors)
        assert result["valid"] is False
        assert result["contract_type"] == "rubric"
