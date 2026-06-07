"""Tests for domain pack contract validation."""

from __future__ import annotations

import pytest
from app.certification_core.validators.domain_pack_validator import DomainPackValidator


class TestDomainPackValidator:
    """Domain pack validation tests."""

    def test_valid_domain_pack(self):
        data = {
            "domain_pack_id": "test.pack.1",
            "name": "Test Domain Pack",
            "version": "1.0.0",
            "created_by": "test_user",
            "supported_modes": ["learning", "practice", "exam_simulation"],
        }
        errors = DomainPackValidator.validate_domain_pack(data)
        assert len(errors) == 0

    def test_missing_required(self):
        data = {}
        errors = DomainPackValidator.validate_domain_pack(data)
        field_names = {e["field"] for e in errors}
        assert "domain_pack_id" in field_names
        assert "name" in field_names
        assert "version" in field_names
        assert "created_by" in field_names

    def test_invalid_status(self):
        data = {
            "domain_pack_id": "test.1",
            "name": "Test",
            "version": "1.0",
            "created_by": "user",
            "status": "invalid",
        }
        errors = DomainPackValidator.validate_domain_pack(data)
        assert any("status" in e["field"] for e in errors)

    def test_valid_statuses(self):
        for status in ["draft", "active", "deprecated", "retired"]:
            data = {
                "domain_pack_id": f"test.{status}",
                "name": "Test",
                "version": "1.0",
                "created_by": "user",
                "status": status,
            }
            errors = DomainPackValidator.validate_domain_pack(data)
            status_errors = [e for e in errors if "status" in e["field"]]
            assert len(status_errors) == 0

    def test_invalid_supported_mode(self):
        data = {
            "domain_pack_id": "test.1",
            "name": "Test",
            "version": "1.0",
            "created_by": "user",
            "supported_modes": ["invalid_mode"],
        }
        errors = DomainPackValidator.validate_domain_pack(data)
        assert any("supported_modes" in e["field"] for e in errors)

    def test_valid_supported_modes(self):
        data = {
            "domain_pack_id": "test.1",
            "name": "Test",
            "version": "1.0",
            "created_by": "user",
            "supported_modes": ["learning", "practice"],
        }
        errors = DomainPackValidator.validate_domain_pack(data)
        assert len(errors) == 0

    def test_no_domain_hardcoding(self):
        """Domain packs must be generic — no BA or QA hardcoding in the model."""
        from app.certification_core.models.domain_pack_models import DomainPack
        columns = [c.name for c in DomainPack.__table__.columns]
        # The model should not have BA or QA specific fields
        ba_fields = [c for c in columns if "ba_" in c or "qa_" in c]
        assert len(ba_fields) == 0, f"Found BA/QA-specific fields: {ba_fields}"

    def test_to_validation_result(self):
        errors = [{"field": "test", "message": "error"}]
        result = DomainPackValidator.to_validation_result(errors)
        assert result["valid"] is False
        assert result["contract_type"] == "domain_pack"
