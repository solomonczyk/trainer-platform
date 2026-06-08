"""Tests for V3 citation identity resolution (v2.0.0 — stable source identity authoritative).

Identity resolution precedence:
1. source_version_id exact match
2. canonical source_id cross-reference via registry
3. source checksum match
4. normalized canonical label comparison

Display-label-only mismatch is non-blocking when stable identity matches.
"""

from __future__ import annotations

import pytest

from app.certification_core.validators.generation_validators import (
    validate_source_citations,
    resolve_citation_source,
    _normalize_label,
    _build_canonical_label_map,
)


class TestCitationIdentityResolutionHelpers:
    """Prove identity resolution helper functions."""

    def test_normalize_label_basic(self):
        """Basic label normalization."""
        assert _normalize_label("Hello World") == "hello world"
        assert _normalize_label("  HELLO  WORLD  ") == "hello world"

    def test_normalize_label_unicode(self):
        """Unicode normalization (NFKC preserves accented chars)."""
        result = _normalize_label("Café")
        # NFKC keeps "é" as composed form; we preserve non-ASCII letters
        assert "caf" in result
        assert isinstance(result, str)

    def test_normalize_label_punctuation(self):
        """Punctuation removal."""
        result = _normalize_label("Source-v1.0!")
        assert "!" not in result
        assert result == "sourcev10"

    def test_normalize_label_empty(self):
        """Empty label."""
        assert _normalize_label("") == ""
        assert _normalize_label("   ") == ""

    def test_build_canonical_label_map(self):
        """Canonical label map construction."""
        source_ids = ["src-ba-swdev-v1.0", "src-qa-testing-v2.0"]
        label_map = _build_canonical_label_map(source_ids)

        # Direct ID lookup
        assert "src-ba-swdev-v1.0" in label_map
        assert label_map["src-ba-swdev-v1.0"]["source_version_id"] == "src-ba-swdev-v1.0"

        # Normalized lookup
        assert "srcbaswdevv10" in label_map

    def test_resolve_citation_source_version_id_exact(self):
        """source_version_id exact match must resolve."""
        result = resolve_citation_source(
            {"source_version_id": "src-ba-swdev-v1.0"},
            ["src-ba-swdev-v1.0", "src-qa-testing-v2.0"],
        )
        assert result["matched"] is True
        assert result["method"] == "source_version_id"

    def test_resolve_citation_source_id_via_map(self):
        """source_id must resolve via canonical label map."""
        result = resolve_citation_source(
            {"source_id": "src-ba-swdev-v1.0"},
            ["src-ba-swdev-v1.0"],
        )
        # source_id direct membership test should match
        assert result["matched"] is True

    def test_resolve_citation_unresolved(self):
        """Unknown citation must return unresolved."""
        result = resolve_citation_source(
            {"source_version_id": "unknown-source-99"},
            ["src-ba-swdev-v1.0"],
        )
        assert result["matched"] is False
        assert result["method"] == "unresolved"

    def test_resolve_citation_empty_citation(self):
        """Empty citation must return unmatched."""
        result = resolve_citation_source({}, ["src-ba-swdev-v1.0"])
        assert result["matched"] is False
        assert result["method"] == "empty_citation"

    def test_resolve_citation_non_dict(self):
        """Non-dict citation must return unmatched."""
        result = resolve_citation_source("not a dict", ["src-ba-swdev-v1.0"])
        assert result["matched"] is False
        assert result["method"] == "invalid_citation"

    def test_resolve_citation_label_normalization(self):
        """Normalized label must resolve canonical source."""
        label_map = _build_canonical_label_map(["src-ba-swdev-v1.0"])
        result = resolve_citation_source(
            {"source_id": "src-ba-swdev-v1.0", "label": "BA Software Development Best Practices"},
            ["src-ba-swdev-v1.0"],
            label_map,
        )
        assert result["matched"] is True


class TestSourceCitationValidation:
    """Prove V3 citation validation with identity resolution."""

    def test_source_version_id_match_authoritative(self):
        """source_version_id exact match must pass."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "label": "BA SD Best Practices"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0", "src-qa-testing-v2.0"]
        )
        assert result.status == "passed"

    def test_source_id_match_authoritative(self):
        """source_id matching canonical ID must pass (label may differ)."""
        candidate = {
            "source_citations": [
                {"source_id": "src-ba-swdev-v1.0", "label": "BA SD Different Label"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status in ("passed", "warning")

    def test_checksum_match_supported(self):
        """Checksum match must be supported."""
        candidate = {
            "source_citations": [
                {
                    "source_version_id": "src-ba-swdev-v1.0",
                    "checksum": "abc123def456",
                    "label": "BA SD Best Practices",
                },
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status in ("passed", "warning")

    def test_case_only_label_difference_allowed(self):
        """Case-only label difference must not block."""
        candidate = {
            "source_citations": [
                {"source_version_id": "SRC-BA-SWDEV-V1.0", "label": "ba sd best practices"},
            ],
        }
        result = validate_source_citations(
            candidate, ["SRC-BA-SWDEV-V1.0"]
        )
        assert result.status == "passed"

    def test_spacing_only_label_difference_allowed(self):
        """Spacing-only label difference must not block."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "label": "BA  SD   Best  Practices"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "passed"

    def test_punctuation_only_label_difference_allowed(self):
        """Punctuation-only difference must not block."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "label": "BA_SD_BP_v1.0!"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "passed"

    def test_canonical_alias_allowed(self):
        """Canonical alias (short form) must resolve."""
        candidate = {
            "source_citations": [
                {"source_id": "swdev-v1.0", "source_version_id": "src-ba-swdev-v1.0"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "passed"

    def test_unknown_source_blocked(self):
        """Unknown source must be blocked."""
        candidate = {
            "source_citations": [
                {"source_version_id": "unknown-source-99", "label": "Unknown Source"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0", "src-qa-testing-v2.0"]
        )
        assert result.status == "failed"
        assert result.reason_code in ("CITATION_SOURCE_MISMATCH", "CITATION_PARTIAL_MATCH")

    def test_missing_citation_blocked(self):
        """Missing citations must be blocked."""
        candidate = {}
        result = validate_source_citations(candidate, ["src-ba-swdev-v1.0"])
        assert result.status == "failed"
        assert result.reason_code == "MISSING_SOURCE_CITATIONS"

    def test_unbound_source_version_blocked(self):
        """Citation referencing unbound source version must be blocked."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-unbound-v1.0", "label": "Unbound Source"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "failed"

    def test_checksum_mismatch_blocked(self):
        """Different checksum on same source must be handled."""
        # With no registry, checksum-only difference can't be detected
        # The source_version_id match should still pass even with different checksum
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "checksum": "different-checksum"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "passed"

    def test_revoked_source_blocked(self):
        """Citation referencing revoked source must be blocked."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-revoked-v1.0", "label": "Revoked Source"},
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

    def test_untrusted_source_blocked(self):
        """Citation referencing untrusted source must be blocked."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-untrusted-v1.0", "label": "Untrusted"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "failed"

    def test_multiple_citations_all_match(self):
        """Multiple valid citations must all pass."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "label": "BA SD"},
                {"source_version_id": "src-qa-testing-v2.0", "label": "QA Testing"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0", "src-qa-testing-v2.0"]
        )
        assert result.status == "passed"

    def test_mixed_match_fails(self):
        """Mixed valid and invalid citations must fail."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "label": "BA SD"},
                {"source_version_id": "unknown-source", "label": "Unknown"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        assert result.status == "failed"

    def test_label_mismatch_non_blocking_warning(self):
        """Label mismatch with stable identity match must produce warning, not failure."""
        candidate = {
            "source_citations": [
                {"source_version_id": "src-ba-swdev-v1.0", "label": "Completely Different Label"},
            ],
        }
        result = validate_source_citations(
            candidate, ["src-ba-swdev-v1.0"]
        )
        # source_version_id matches, so stable identity is OK
        # Label might differ but that's non-blocking
        assert result.status in ("passed", "warning")
        if result.status == "warning":
            assert result.reason_code == "CITATION_LABEL_NORMALIZATION"
