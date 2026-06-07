"""Validator for Knowledge Source Registry contracts."""

from __future__ import annotations

from typing import Any


VALID_SOURCE_TYPES = {
    "standard", "syllabus", "law", "book", "official_documentation",
    "expert_policy", "dataset",
}
VALID_STATUSES = {"draft", "verified", "active", "superseded", "revoked"}
VALID_CHANGE_CATEGORIES = {"editorial", "clarification", "substantive", "breaking"}


class KnowledgeSourceValidator:
    """Validation logic for knowledge source registry entries."""

    @staticmethod
    def validate_source(data: dict) -> list[dict]:
        """Validate a knowledge source record."""
        errors: list[dict] = []

        # Required fields
        required = ["source_id", "title", "version", "created_by"]
        for field in required:
            if not data.get(field):
                errors.append({"field": field, "message": f"'{field}' is required"})

        # Source type
        source_type = data.get("source_type", "standard")
        if source_type not in VALID_SOURCE_TYPES:
            errors.append({
                "field": "source_type",
                "message": f"Invalid source_type '{source_type}'. Must be one of: {', '.join(sorted(VALID_SOURCE_TYPES))}",
            })

        # Status
        status = data.get("status", "draft")
        if status and status not in VALID_STATUSES:
            errors.append({
                "field": "status",
                "message": f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            })

        # Change category
        change_cat = data.get("change_category")
        if change_cat and change_cat not in VALID_CHANGE_CATEGORIES:
            errors.append({
                "field": "change_category",
                "message": f"Invalid change_category '{change_cat}'. Must be one of: {', '.join(sorted(VALID_CHANGE_CATEGORIES))}",
            })

        # URL format check (basic)
        source_url = data.get("source_url")
        if source_url and not source_url.startswith(("http://", "https://", "ftp://")):
            errors.append({
                "field": "source_url",
                "message": "source_url must start with http://, https://, or ftp://",
            })

        return errors

    @staticmethod
    def to_validation_result(errors: list[dict]) -> dict[str, Any]:
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "contract_type": "knowledge_source",
        }
