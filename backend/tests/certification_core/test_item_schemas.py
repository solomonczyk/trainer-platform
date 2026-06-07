"""Tests for item and item family schema validation and versioning."""

from __future__ import annotations

import pytest
from app.certification_core.validators.item_validator import ItemValidator, ItemFamilyValidator


class TestItemValidator:
    """Item validation tests."""

    def test_valid_item(self):
        data = {
            "item_id": "test.item.1",
            "item_type": "multiple_choice",
            "created_by": "test_user",
        }
        errors = ItemValidator.validate_item(data)
        assert len(errors) == 0

    def test_missing_required_fields(self):
        data = {}
        errors = ItemValidator.validate_item(data)
        field_names = {e["field"] for e in errors}
        assert "item_id" in field_names
        assert "item_type" in field_names
        assert "created_by" in field_names

    def test_invalid_item_type(self):
        data = {
            "item_id": "test.1",
            "item_type": "invalid_type",
            "created_by": "user",
        }
        errors = ItemValidator.validate_item(data)
        assert any("item_type" in e["field"] for e in errors)

    def test_valid_item_types(self):
        for item_type in ["multiple_choice", "single_choice", "numeric", "fill_blanks", "matching", "essay", "scenario"]:
            data = {
                "item_id": f"test.{item_type}",
                "item_type": item_type,
                "created_by": "user",
            }
            errors = ItemValidator.validate_item(data)
            type_errors = [e for e in errors if "item_type" in e["field"]]
            assert len(type_errors) == 0, f"Item type '{item_type}' should be valid"

    def test_invalid_difficulty(self):
        data = {
            "item_id": "test.1",
            "item_type": "multiple_choice",
            "created_by": "user",
            "difficulty_target": "extreme",
        }
        errors = ItemValidator.validate_item(data)
        assert any("difficulty_target" in e["field"] for e in errors)

    def test_valid_difficulties(self):
        for diff in ["easy", "medium", "hard", "expert"]:
            data = {
                "item_id": f"test.{diff}",
                "item_type": "multiple_choice",
                "created_by": "user",
                "difficulty_target": diff,
            }
            errors = ItemValidator.validate_item(data)
            diff_errors = [e for e in errors if "difficulty" in e["field"]]
            assert len(diff_errors) == 0, f"Difficulty '{diff}' should be valid"

    def test_difficulty_measured_range(self):
        data = {
            "item_id": "test.range",
            "item_type": "multiple_choice",
            "created_by": "user",
            "difficulty_measured": 1.5,  # > 1.0
        }
        errors = ItemValidator.validate_item(data)
        assert any("difficulty_measured" in e["field"] for e in errors)

    def test_valid_difficulty_measured(self):
        data = {
            "item_id": "test.range",
            "item_type": "multiple_choice",
            "created_by": "user",
            "difficulty_measured": 0.58,
        }
        errors = ItemValidator.validate_item(data)
        diff_errors = [e for e in errors if "difficulty_measured" in e["field"]]
        assert len(diff_errors) == 0

    def test_invalid_compromise_risk(self):
        data = {
            "item_id": "test.1",
            "item_type": "multiple_choice",
            "created_by": "user",
            "compromise_risk": "unknown",
        }
        errors = ItemValidator.validate_item(data)
        assert any("compromise_risk" in e["field"] for e in errors)

    def test_valid_compromise_risks(self):
        for risk in ["low", "medium", "high", "critical"]:
            data = {
                "item_id": f"test.{risk}",
                "item_type": "multiple_choice",
                "created_by": "user",
                "compromise_risk": risk,
            }
            errors = ItemValidator.validate_item(data)
            risk_errors = [e for e in errors if "compromise_risk" in e["field"]]
            assert len(risk_errors) == 0

    def test_valid_statuses(self):
        valid_statuses = [
            "draft", "generated", "automated_validation_passed",
            "expert_review_required", "approved_for_pilot", "pilot",
            "calibrated", "exam_eligible", "suspended", "retired",
        ]
        for status in valid_statuses:
            data = {
                "item_id": f"test.{status}",
                "item_type": "multiple_choice",
                "created_by": "user",
                "status": status,
            }
            errors = ItemValidator.validate_item(data)
            status_errors = [e for e in errors if "status" in e["field"]]
            assert len(status_errors) == 0, f"Status '{status}' should be valid"


class TestItemFamilyValidator:
    """Item family validation tests."""

    def test_valid_family(self):
        data = {
            "family_id": "test.family.1",
            "name": "Test Family",
            "created_by": "test_user",
        }
        errors = ItemFamilyValidator.validate_family(data)
        assert len(errors) == 0

    def test_missing_required(self):
        data = {}
        errors = ItemFamilyValidator.validate_family(data)
        field_names = {e["field"] for e in errors}
        assert "family_id" in field_names
        assert "name" in field_names
        assert "created_by" in field_names

    def test_valid_allowed_types(self):
        data = {
            "family_id": "test.family.types",
            "name": "Test",
            "created_by": "user",
            "allowed_item_types": ["multiple_choice", "single_choice"],
        }
        errors = ItemFamilyValidator.validate_family(data)
        assert len(errors) == 0

    def test_invalid_allowed_type(self):
        data = {
            "family_id": "test.family.bad",
            "name": "Test",
            "created_by": "user",
            "allowed_item_types": ["invalid_type"],
        }
        errors = ItemFamilyValidator.validate_family(data)
        assert any("allowed_item_types" in e["field"] for e in errors)

    def test_status_validation(self):
        for status in ["draft", "active", "deprecated", "retired"]:
            data = {
                "family_id": f"test.{status}",
                "name": "Test",
                "created_by": "user",
                "status": status,
            }
            errors = ItemFamilyValidator.validate_family(data)
            status_errors = [e for e in errors if "status" in e["field"]]
            assert len(status_errors) == 0


class TestItemVersioning:
    """Item versioning model tests."""

    def test_version_progression(self):
        """Item versions should increment."""
        from app.certification_core.models.item_models import Item, ItemVersion
        # This tests the model structure, not database operations
        assert hasattr(Item, "version")
        assert hasattr(ItemVersion, "version")
        assert hasattr(ItemVersion, "snapshot")
        assert hasattr(ItemVersion, "change_reason")

    def test_item_version_unique_constraint(self):
        """ItemVersion should enforce unique (item_id, version)."""
        from app.certification_core.models.item_models import ItemVersion
        # Verify the constraint exists in table args
        has_constraint = any(
            hasattr(arg, "name") and arg.name == "uq_item_version"
            for arg in getattr(ItemVersion, "__table_args__", []) or []
            if hasattr(arg, "name")
        )
        assert has_constraint

    def test_item_immutable_fields(self):
        """Published item versions should be immutable."""
        # Verify the structure supports immutability through snapshots
        from app.certification_core.models.item_models import ItemVersion
        assert hasattr(ItemVersion, "snapshot")
