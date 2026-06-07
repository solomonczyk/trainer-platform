"""Validator for Exam Blueprint contracts."""

from __future__ import annotations

from typing import Any


VALID_STATUSES = {"draft", "active", "deprecated", "retired"}


class BlueprintValidator:
    """Validation logic for exam blueprints — enforces weight totals, item counts, etc."""

    @staticmethod
    def validate_blueprint(data: dict) -> list[dict]:
        """Validate a full exam blueprint. Returns list of errors (empty = valid)."""
        errors: list[dict] = []

        # Required fields
        required = ["blueprint_id", "competency_framework_version", "version", "created_by"]
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

        # Exam duration
        duration = data.get("exam_duration_minutes", 0)
        if duration <= 0:
            errors.append({"field": "exam_duration_minutes", "message": "Must be greater than 0"})

        # Validate sections
        sections = data.get("sections", [])
        if not sections:
            errors.append({"field": "sections", "message": "At least one section is required"})

        section_ids_seen = set()
        total_weight = 0.0
        for i, section in enumerate(sections):
            sec_errors = BlueprintValidator.validate_section(section)
            for err in sec_errors:
                errors.append({
                    "field": f"sections[{i}].{err['field']}",
                    "message": err["message"],
                })

            # Track weight sum
            total_weight += section.get("weight_percent", 0)

            # Check duplicate section_ids
            sid = section.get("section_id")
            if sid:
                if sid in section_ids_seen:
                    errors.append({
                        "field": f"sections[{i}].section_id",
                        "message": f"Duplicate section_id '{sid}'",
                    })
                section_ids_seen.add(sid)

        # Weights must total 100%
        if sections and abs(total_weight - 100.0) > 0.01:
            errors.append({
                "field": "sections",
                "message": f"Section weights must total 100%, got {total_weight}%",
            })

        # Total items check
        total_min = sum(s.get("minimum_items", 0) for s in sections)
        total_max = sum(s.get("maximum_items", 0) for s in sections)
        blueprint_total = data.get("total_items", 0)

        if total_min > 0 and blueprint_total > 0 and blueprint_total < total_min:
            errors.append({
                "field": "total_items",
                "message": f"total_items ({blueprint_total}) is less than sum of section minimum_items ({total_min})",
            })

        return errors

    @staticmethod
    def validate_section(data: dict) -> list[dict]:
        """Validate a blueprint section."""
        errors: list[dict] = []

        if not data.get("section_id"):
            errors.append({"field": "section_id", "message": "section_id is required"})

        if not data.get("name"):
            errors.append({"field": "name", "message": "name is required"})

        # Weight
        weight = data.get("weight_percent", 0)
        if weight < 0 or weight > 100:
            errors.append({"field": "weight_percent", "message": "Must be between 0 and 100"})

        # Item counts
        min_items = data.get("minimum_items", 0)
        max_items = data.get("maximum_items", 0)
        if min_items < 0:
            errors.append({"field": "minimum_items", "message": "Must be >= 0"})
        if max_items < 0:
            errors.append({"field": "maximum_items", "message": "Must be >= 0"})
        if max_items > 0 and min_items > max_items:
            errors.append({
                "field": "minimum_items",
                "message": f"minimum_items ({min_items}) exceeds maximum_items ({max_items})",
            })

        # Difficulty distribution should sum to ~100%
        diff_dist = data.get("difficulty_distribution", {})
        if diff_dist:
            total_diff = sum(diff_dist.values())
            if abs(total_diff - 1.0) > 0.01:
                errors.append({
                    "field": "difficulty_distribution",
                    "message": f"Difficulty distribution should sum to 1.0, got {total_diff}",
                })

        # Competency IDs
        competency_ids = data.get("competency_ids", [])
        if not competency_ids:
            errors.append({"field": "competency_ids", "message": "At least one competency_id is required"})

        return errors

    @staticmethod
    def to_validation_result(errors: list[dict]) -> dict[str, Any]:
        """Convert error list to standard validation result."""
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "contract_type": "exam_blueprint",
        }
