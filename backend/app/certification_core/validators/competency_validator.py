"""Validator for Competency Framework contracts."""

from __future__ import annotations

from typing import Any

from app.certification_core.models.competency_models import CompetencyFramework


VALID_STATUSES = {"draft", "active", "deprecated", "retired"}
VALID_COGNITIVE_LEVELS = {"remember", "understand", "apply", "analyze", "evaluate", "create"}


class CompetencyValidator:
    """Validation logic for competency frameworks and competencies."""

    @staticmethod
    def validate_framework(data: dict) -> list[dict]:
        """Validate a competency framework. Returns list of errors (empty = valid)."""
        errors: list[dict] = []

        # Required fields
        required = ["framework_id", "version", "created_by"]
        for field in required:
            if not data.get(field):
                errors.append({"field": field, "message": f"'{field}' is required"})

        # Status
        status = data.get("status", "draft")
        if status and status not in VALID_STATUSES:
            errors.append({
                "field": "status",
                "message": f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            })

        # Validate competencies if present
        competencies = data.get("competencies", [])
        for i, comp in enumerate(competencies):
            comp_errors = CompetencyValidator.validate_competency(comp)
            for err in comp_errors:
                errors.append({
                    "field": f"competencies[{i}].{err['field']}",
                    "message": err["message"],
                })

        # Check duplicate competency_ids
        seen_ids = set()
        for comp in competencies:
            cid = comp.get("competency_id")
            if cid:
                if cid in seen_ids:
                    errors.append({
                        "field": "competencies",
                        "message": f"Duplicate competency_id '{cid}'",
                    })
                seen_ids.add(cid)

        return errors

    @staticmethod
    def validate_competency(data: dict) -> list[dict]:
        """Validate a single competency node."""
        errors: list[dict] = []

        if not data.get("competency_id"):
            errors.append({"field": "competency_id", "message": "competency_id is required"})

        if not data.get("name"):
            errors.append({"field": "name", "message": "name is required"})

        # Validate cognitive levels
        levels = data.get("cognitive_levels", [])
        if levels:
            for level in levels:
                if level not in VALID_COGNITIVE_LEVELS:
                    errors.append({
                        "field": "cognitive_levels",
                        "message": f"Invalid cognitive level '{level}'. Must be one of: {', '.join(sorted(VALID_COGNITIVE_LEVELS))}",
                    })

        # Weight validation
        weight = data.get("weight", 0)
        if weight < 0 or weight > 100:
            errors.append({"field": "weight", "message": "weight must be between 0 and 100"})

        return errors

    @staticmethod
    def to_validation_result(errors: list[dict]) -> dict[str, Any]:
        """Convert error list to standard validation result."""
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "contract_type": "competency_framework",
        }
