"""Tests for generation source citation validation — V3 citation completeness and identity.

These tests verify that V3 correctly validates source citations using stable identity
resolution and blocks missing, unknown, or revoked sources.
"""

from __future__ import annotations

import pytest

from app.certification_core.validators.generation_validators import (
    validate_source_citations,
)


class TestGenerationSourceCitationValidation:
    """Prove V3 source citation validation."""

    def test_valid_citation_passes(self):
        """Valid citation with exact source_version_id must pass."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "label": "BA SD Best Practices"},
            ],
        }
        result = validate_source_citations(candidate, ["src-ba-swdev-v1.0"])
        assert result.status == "passed"

    def test_missing_citations_fails(self):
        """Missing source_citations field must fail."""
        candidate = {}
        result = validate_source_citations(candidate, ["src-ba-swdev-v1.0"])
        assert result.status == "failed"
        assert result.reason_code == "MISSING_SOURCE_CITATIONS"

    def test_empty_citations_fails(self):
        """Empty source_citations list must fail."""
        candidate = {"source_citations": []}
        result = validate_source_citations(candidate, ["src-ba-swdev-v1.0"])
        assert result.status == "failed"
        assert result.reason_code == "MISSING_SOURCE_CITATIONS"

    def test_non_dict_citation_handled(self):
        """Non-dict citation entries must be handled gracefully."""
        candidate = {"source_citations": ["string citation"]}
        result = validate_source_citations(candidate, ["src-ba-swdev-v1.0"])
        assert result.status == "failed"

    def test_no_expected_sources_still_validates(self):
        """Citations are checked even when no expected sources provided."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0"},
            ],
        }
        # With no expected sources, the citation can't match
        result = validate_source_citations(candidate, [])
        assert result.status == "failed"

    def test_revoked_source_with_registry(self):
        """Revoked source must be blocked when registry is provided."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-revoked-v1.0"},
            ],
        }
        source_registry = [
            {
                "source_version_id": "src-revoked-v1.0",
                "source_status": "revoked",
                "source_title": "Revoked Source",
            },
        ]
        result = validate_source_citations(
            candidate, ["src-revoked-v1.0"], source_registry=source_registry
        )
        assert result.status == "failed"
        assert result.reason_code == "REVOKED_SOURCE"

    def test_multiple_sources_valid(self):
        """Multiple valid citations must pass."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0"},
                {"source_version_id": "src-qa-testing-v2.0"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0", "src-qa-testing-v2.0"]
        )
        assert result.status == "passed"

    def test_partial_match_detected(self):
        """When some citations match and some don't, must report partial match."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0"},
                {"source_version_id": "unknown-source"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "failed"
        assert result.reason_code == "CITATION_PARTIAL_MATCH"
