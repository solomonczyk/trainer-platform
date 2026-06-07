"""Validator for Domain Pack contracts."""

from __future__ import annotations

from typing import Any


VALID_STATUSES = {"draft", "active", "deprecated", "retired"}
VALID_MODES = {"learning", "practice", "exam_simulation"}


class DomainPackValidator:
    """Validation logic for domain packs."""

    @staticmethod
    def validate_domain_pack(data: dict) -> list[dict]:
        """Validate a domain pack. Returns list of errors (empty = valid)."""
        errors: list[dict] = []

        required = ["domain_pack_id", "name", "version", "created_by"]
        for field in required:
            if not data.get(field):
                errors.append({"field": field, "message": f"'{field}' is required"})

        status = data.get("status", "draft")
        if status and status not in VALID_STATUSES:
            errors.append({
                "field": "status",
                "message": f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            })

        # Validate supported modes
        modes = data.get("supported_modes", [])
        if modes:
            for mode in modes:
                if mode not in VALID_MODES:
                    errors.append({
                        "field": "supported_modes",
                        "message": f"Invalid mode '{mode}'. Must be one of: {', '.join(sorted(VALID_MODES))}",
                    })

        return errors

    @staticmethod
    def to_validation_result(errors: list[dict]) -> dict[str, Any]:
        return {"valid": len(errors) == 0, "errors": errors, "contract_type": "domain_pack"}
