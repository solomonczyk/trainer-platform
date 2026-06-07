"""Tests for exam blueprint validation contracts."""

from __future__ import annotations

import pytest
from app.certification_core.validators.blueprint_validator import BlueprintValidator


class TestBlueprintValidator:
    """Exam blueprint validation tests."""

    def test_valid_blueprint(self):
        data = {
            "blueprint_id": "ba.bp.test.1",
            "competency_framework_version": "ba.1.0",
            "version": "1.0",
            "created_by": "test_user",
            "exam_duration_minutes": 120,
            "total_items": 50,
            "sections": [
                {
                    "section_id": "sec.1",
                    "name": "Requirements",
                    "competency_ids": ["comp.1"],
                    "weight_percent": 60.0,
                    "minimum_items": 10,
                    "maximum_items": 30,
                    "difficulty_distribution": {"easy": 0.3, "medium": 0.4, "hard": 0.3},
                },
                {
                    "section_id": "sec.2",
                    "name": "Analysis",
                    "competency_ids": ["comp.2"],
                    "weight_percent": 40.0,
                    "minimum_items": 5,
                    "maximum_items": 20,
                },
            ],
        }
        errors = BlueprintValidator.validate_blueprint(data)
        assert len(errors) == 0

    def test_weights_must_total_100(self):
        data = {
            "blueprint_id": "test.weight",
            "competency_framework_version": "v1",
            "version": "1.0",
            "created_by": "user",
            "exam_duration_minutes": 60,
            "sections": [
                {
                    "section_id": "sec.1",
                    "name": "Section 1",
                    "competency_ids": ["comp.1"],
                    "weight_percent": 30.0,
                },
                {
                    "section_id": "sec.2",
                    "name": "Section 2",
                    "competency_ids": ["comp.2"],
                    "weight_percent": 30.0,
                },
            ],
        }
        errors = BlueprintValidator.validate_blueprint(data)
        assert any("weights must total 100%" in e["message"] for e in errors)

    def test_weights_exactly_100(self):
        data = {
            "blueprint_id": "test.exact",
            "competency_framework_version": "v1",
            "version": "1.0",
            "created_by": "user",
            "exam_duration_minutes": 60,
            "sections": [
                {
                    "section_id": "sec.1",
                    "name": "Section 1",
                    "competency_ids": ["comp.1"],
                    "weight_percent": 100.0,
                },
            ],
        }
        errors = BlueprintValidator.validate_blueprint(data)
        assert len(errors) == 0

    def test_missing_sections(self):
        data = {
            "blueprint_id": "test.nosections",
            "competency_framework_version": "v1",
            "version": "1.0",
            "created_by": "user",
            "exam_duration_minutes": 60,
            "sections": [],
        }
        errors = BlueprintValidator.validate_blueprint(data)
        assert any("At least one section" in e["message"] for e in errors)

    def test_section_item_bounds(self):
        data = {
            "section_id": "sec.1",
            "name": "Test",
            "competency_ids": ["comp.1"],
            "weight_percent": 50.0,
            "minimum_items": 20,
            "maximum_items": 10,  # min > max
        }
        errors = BlueprintValidator.validate_section(data)
        assert any("exceeds maximum" in e["message"] for e in errors)

    def test_invalid_difficulty_distribution(self):
        data = {
            "section_id": "sec.1",
            "name": "Test",
            "competency_ids": ["comp.1"],
            "weight_percent": 100.0,
            "difficulty_distribution": {"easy": 0.3, "medium": 0.3},  # doesn't sum to 1
        }
        errors = BlueprintValidator.validate_section(data)
        assert any("sum to 1.0" in e["message"] for e in errors)

    def test_section_missing_competency_ids(self):
        data = {
            "section_id": "sec.1",
            "name": "Test",
            "competency_ids": [],
            "weight_percent": 100.0,
        }
        errors = BlueprintValidator.validate_section(data)
        assert any("competency_id" in e["field"] for e in errors)

    def test_duplicate_section_ids(self):
        data = {
            "blueprint_id": "test.dup",
            "competency_framework_version": "v1",
            "version": "1.0",
            "created_by": "user",
            "exam_duration_minutes": 60,
            "sections": [
                {
                    "section_id": "sec.1",
                    "name": "Section 1",
                    "competency_ids": ["comp.1"],
                    "weight_percent": 50.0,
                },
                {
                    "section_id": "sec.1",
                    "name": "Section 1 again",
                    "competency_ids": ["comp.2"],
                    "weight_percent": 50.0,
                },
            ],
        }
        errors = BlueprintValidator.validate_blueprint(data)
        assert any("Duplicate section_id" in e["message"] for e in errors)

    def test_zero_duration(self):
        data = {
            "blueprint_id": "test.time",
            "competency_framework_version": "v1",
            "version": "1.0",
            "created_by": "user",
            "exam_duration_minutes": 0,
            "sections": [{
                "section_id": "sec.1", "name": "S1",
                "competency_ids": ["c1"],
                "weight_percent": 100.0,
            }],
        }
        errors = BlueprintValidator.validate_blueprint(data)
        assert any("exam_duration_minutes" in e["field"] for e in errors)

    def test_total_items_check(self):
        data = {
            "blueprint_id": "test.items",
            "competency_framework_version": "v1",
            "version": "1.0",
            "created_by": "user",
            "exam_duration_minutes": 60,
            "total_items": 5,
            "sections": [{
                "section_id": "sec.1", "name": "S1",
                "competency_ids": ["c1"],
                "weight_percent": 100.0,
                "minimum_items": 10,
            }],
        }
        errors = BlueprintValidator.validate_blueprint(data)
        assert any("total_items" in e["field"] for e in errors)

    def test_required_fields(self):
        data = {}
        errors = BlueprintValidator.validate_blueprint(data)
        required = ["blueprint_id", "competency_framework_version", "version", "created_by"]
        found = set()
        for e in errors:
            if e["field"] in required:
                found.add(e["field"])
        assert found == set(required)

    def test_to_validation_result(self):
        errors = [{"field": "test", "message": "error"}]
        result = BlueprintValidator.to_validation_result(errors)
        assert result["valid"] is False
        assert result["contract_type"] == "exam_blueprint"
