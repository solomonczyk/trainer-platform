"""Validator for Rubric contracts — enforces weight constraints, level validity."""

from __future__ import annotations

from typing import Any


VALID_STATUSES = {"draft", "active", "deprecated", "retired"}


class RubricValidator:
    """Validation logic for rubrics and rubric criteria."""

    @staticmethod
    def validate_rubric(data: dict) -> list[dict]:
        """Validate a rubric. Returns list of errors (empty = valid)."""
        errors: list[dict] = []

        required = ["rubric_id", "version", "created_by"]
        for field in required:
            if not data.get(field):
                errors.append({"field": field, "message": f"'{field}' is required"})

        status = data.get("status", "draft")
        if status and status not in VALID_STATUSES:
            errors.append({
                "field": "status",
                "message": f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            })

        # Validate criteria
        criteria = data.get("criteria", [])
        if not criteria:
            errors.append({"field": "criteria", "message": "At least one criterion is required"})

        total_weight = 0.0
        seen_ids = set()
        for i, criterion in enumerate(criteria):
            crit_errors = RubricValidator.validate_criterion(criterion)
            for err in crit_errors:
                errors.append({
                    "field": f"criteria[{i}].{err['field']}",
                    "message": err["message"],
                })

            total_weight += criterion.get("weight", 0)

            # Check duplicate criterion_ids
            cid = criterion.get("criterion_id")
            if cid:
                if cid in seen_ids:
                    errors.append({
                        "field": f"criteria[{i}].criterion_id",
                        "message": f"Duplicate criterion_id '{cid}'",
                    })
                seen_ids.add(cid)

        # Total weight must equal 100
        if criteria and abs(total_weight - 100.0) > 0.01:
            errors.append({
                "field": "criteria",
                "message": f"Total weight must equal 100, got {total_weight}",
            })

        return errors

    @staticmethod
    def validate_criterion(data: dict) -> list[dict]:
        """Validate a single rubric criterion."""
        errors: list[dict] = []

        if not data.get("criterion_id"):
            errors.append({"field": "criterion_id", "message": "criterion_id is required"})

        if not data.get("name"):
            errors.append({"field": "name", "message": "name is required"})

        weight = data.get("weight", 0)
        if weight <= 0:
            errors.append({"field": "weight", "message": "weight must be greater than 0"})
        if weight > 100:
            errors.append({"field": "weight", "message": "weight must be <= 100"})

        return errors

    @staticmethod
    def to_validation_result(errors: list[dict]) -> dict[str, Any]:
        return {"valid": len(errors) == 0, "errors": errors, "contract_type": "rubric"}
