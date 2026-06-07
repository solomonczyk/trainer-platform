"""Validators for Item Family and Item contracts."""

from __future__ import annotations

from typing import Any


VALID_ITEM_TYPES = {
    "multiple_choice", "single_choice", "numeric", "fill_blanks", "matching",
    "essay", "scenario", "coding", "drag_drop", "hotspot",
}
VALID_STATUSES = {
    "draft", "generated", "automated_validation_failed", "automated_validation_passed",
    "expert_review_required", "approved_for_pilot", "pilot", "calibration_review",
    "calibrated", "exam_eligible", "under_review", "suspended", "retired", "archived",
}
VALID_DIFFICULTY_LEVELS = {"easy", "medium", "hard", "expert"}
VALID_COMPROMISE_RISKS = {"low", "medium", "high", "critical"}
VALID_FAMILY_STATUSES = {"draft", "active", "deprecated", "retired"}


class ItemFamilyValidator:
    """Validation logic for item families."""

    @staticmethod
    def validate_family(data: dict) -> list[dict]:
        errors: list[dict] = []

        required = ["family_id", "name", "created_by"]
        for field in required:
            if not data.get(field):
                errors.append({"field": field, "message": f"'{field}' is required"})

        status = data.get("status", "draft")
        if status and status not in VALID_FAMILY_STATUSES:
            errors.append({
                "field": "status",
                "message": f"Invalid status '{status}'",
            })

        allowed_types = data.get("allowed_item_types", [])
        if allowed_types:
            for at in allowed_types:
                if at not in VALID_ITEM_TYPES:
                    errors.append({
                        "field": "allowed_item_types",
                        "message": f"Invalid item type '{at}'",
                    })

        return errors

    @staticmethod
    def to_validation_result(errors: list[dict]) -> dict[str, Any]:
        return {"valid": len(errors) == 0, "errors": errors, "contract_type": "item_family"}


class ItemValidator:
    """Validation logic for items."""

    @staticmethod
    def validate_item(data: dict) -> list[dict]:
        errors: list[dict] = []

        required = ["item_id", "item_type", "created_by"]
        for field in required:
            if not data.get(field):
                errors.append({"field": field, "message": f"'{field}' is required"})

        item_type = data.get("item_type", "")
        if item_type and item_type not in VALID_ITEM_TYPES:
            errors.append({
                "field": "item_type",
                "message": f"Invalid item_type '{item_type}'. Must be one of: {', '.join(sorted(VALID_ITEM_TYPES))}",
            })

        status = data.get("status", "draft")
        if status and status not in VALID_STATUSES:
            errors.append({
                "field": "status",
                "message": f"Invalid status '{status}'",
            })

        difficulty = data.get("difficulty_target", "medium")
        if difficulty and difficulty not in VALID_DIFFICULTY_LEVELS:
            errors.append({
                "field": "difficulty_target",
                "message": f"Invalid difficulty_target '{difficulty}'",
            })

        compromise_risk = data.get("compromise_risk", "low")
        if compromise_risk and compromise_risk not in VALID_COMPROMISE_RISKS:
            errors.append({
                "field": "compromise_risk",
                "message": f"Invalid compromise_risk '{compromise_risk}'",
            })

        # Measured difficulty range
        diff_measured = data.get("difficulty_measured")
        if diff_measured is not None and (diff_measured < 0 or diff_measured > 1):
            errors.append({
                "field": "difficulty_measured",
                "message": "difficulty_measured must be between 0 and 1",
            })

        return errors

    @staticmethod
    def to_validation_result(errors: list[dict]) -> dict[str, Any]:
        return {"valid": len(errors) == 0, "errors": errors, "contract_type": "item"}
