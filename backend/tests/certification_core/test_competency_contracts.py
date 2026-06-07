"""Tests for competency framework contracts."""

from __future__ import annotations

import pytest
from app.certification_core.validators.competency_validator import CompetencyValidator


class TestCompetencyValidator:
    """Competency framework validation tests."""

    def test_valid_framework(self):
        data = {
            "framework_id": "ba.test.1",
            "version": "1.0",
            "created_by": "test_user",
            "competencies": [
                {
                    "competency_id": "comp.1",
                    "name": "Test competency",
                    "cognitive_levels": ["understand", "apply"],
                    "critical": True,
                    "weight": 50.0,
                }
            ],
        }
        errors = CompetencyValidator.validate_framework(data)
        assert len(errors) == 0

    def test_framework_missing_required_fields(self):
        data = {}
        errors = CompetencyValidator.validate_framework(data)
        assert len(errors) >= 3  # framework_id, version, created_by

    def test_framework_invalid_status(self):
        data = {
            "framework_id": "test.1",
            "version": "1.0",
            "created_by": "user",
            "status": "invalid_status",
        }
        errors = CompetencyValidator.validate_framework(data)
        assert any("status" in e["field"] for e in errors)

    def test_competency_invalid_cognitive_level(self):
        data = {
            "framework_id": "test.1",
            "version": "1.0",
            "created_by": "user",
            "competencies": [
                {
                    "competency_id": "comp.1",
                    "name": "Test",
                    "cognitive_levels": ["invalid_level"],
                }
            ],
        }
        errors = CompetencyValidator.validate_framework(data)
        assert any("cognitive_levels" in e["field"] for e in errors)

    def test_duplicate_competency_ids(self):
        data = {
            "framework_id": "test.1",
            "version": "1.0",
            "created_by": "user",
            "competencies": [
                {"competency_id": "comp.1", "name": "First"},
                {"competency_id": "comp.1", "name": "Duplicate"},
            ],
        }
        errors = CompetencyValidator.validate_framework(data)
        assert any("Duplicate" in e["message"] for e in errors)

    def test_valid_statuses_accepted(self):
        for status in ["draft", "active", "deprecated", "retired"]:
            data = {
                "framework_id": f"test.{status}",
                "version": "1.0",
                "created_by": "user",
                "status": status,
            }
            errors = CompetencyValidator.validate_framework(data)
            status_errors = [e for e in errors if "status" in e["field"]]
            assert len(status_errors) == 0, f"Status '{status}' should be valid"

    def test_valid_cognitive_levels(self):
        levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        data = {
            "framework_id": "test.levels",
            "version": "1.0",
            "created_by": "user",
            "competencies": [
                {
                    "competency_id": "comp.1",
                    "name": "Test",
                    "cognitive_levels": levels,
                }
            ],
        }
        errors = CompetencyValidator.validate_framework(data)
        assert len(errors) == 0

    def test_weight_bounds(self):
        data = {
            "framework_id": "test.weight",
            "version": "1.0",
            "created_by": "user",
            "competencies": [
                {
                    "competency_id": "comp.1",
                    "name": "Test",
                    "weight": 150,  # exceeds 100
                }
            ],
        }
        errors = CompetencyValidator.validate_framework(data)
        assert any("weight" in e["field"] for e in errors)

    def test_competency_missing_required(self):
        errors = CompetencyValidator.validate_competency({})
        assert len(errors) >= 2  # competency_id and name

    def test_to_validation_result(self):
        errors = [{"field": "test", "message": "error"}]
        result = CompetencyValidator.to_validation_result(errors)
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["contract_type"] == "competency_framework"
