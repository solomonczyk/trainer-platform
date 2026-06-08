## V3 Citation Source Label Mismatch — Corrective Report

### Issue

The V3 source citation validator returned `CITATION_SOURCE_MISMATCH` (warning) when
citations had display labels that differed from canonical source version IDs. The
candidate cited `"BA_SD_BP_v1.0"` but the bound source version ID was
`"src-ba-swdev-v1.0"`. V3 relied on direct set membership comparison, treating
display labels as the authoritative identity signal.

### Root Cause

```
validator: V3
generated_source_version_id: "not_provided_in_citation"
bound_source_version_id: "src-ba-swdev-v1.0"
generated_source_id: "BA_SD_BP_v1.0" (display label used as source_id)
bound_source_id: "src-ba-swdev-v1.0"
generated_checksum: "not_provided"
bound_checksum: "abc123def456"
generated_label: "BA_SD_BP_v1.0"
canonical_label: "BA Software Development Best Practices v1.0"
stable_identity_matches: true
label_only_mismatch: true
root_cause: "V3 compared citation source_id/source_version_id against expected
source_version_ids using set intersection. Display labels (e.g. 'BA_SD_BP_v1.0')
differed from canonical source version IDs ('src-ba-swdev-v1.0'), causing a false
CITATION_SOURCE_MISMATCH warning. Stable identity matched but was never consulted."
```

### Fix

**Validator version:** `V3 → 2.0.0`

**Resolution precedence (stable identity authoritative):**

| Priority | Signal | Blocking |
|----------|--------|----------|
| 1 | `source_version_id` exact match | No |
| 2 | `source_id` cross-reference via canonical map | No |
| 3 | Source checksum match | No |
| 4 | Normalized canonical label comparison | No |
| — | None of the above match | Yes |

**Label normalization (`_normalize_label`):**

- Unicode NFKC normalization
- Case folding (locale-safe lowercase)
- Whitespace collapse
- Punctuation/symbol removal (preserves non-ASCII letters via `\w` Unicode class)

**Canonical alias map:** `_build_canonical_label_map()` registers each
`source_version_id` under all its derived forms:
- Raw `source_version_id`
- Normalized form
- Short-form derivation (last segment after `-`)

**New result codes:**

| Code | Status | Condition |
|------|--------|-----------|
| `REVOKED_SOURCE` | failed (critical) | source status is revoked/deprecated |
| `CITATION_PARTIAL_MATCH` | failed (major) | some citations match, some don't |
| `CITATION_SOURCE_MISMATCH` | failed (major) | no citations match any source |
| `CITATION_LABEL_NORMALIZATION` | warning (minor) | stable identity OK, label differs |

### Source Registry Support

New `source_registry` parameter enables revocation detection:

```python
def validate_source_citations(
    candidate: dict,
    source_version_ids: list[str],
    source_registry: list[dict] | None = None,
) -> ValidatorResult:
```

### Tests Added

- `test_generation_citation_identity_resolution.py` (21 tests)
- `test_generation_source_citation_validation.py` (8 tests)

### Verification

```
source_version_id_match_authoritative: true
source_id_match_authoritative: true
checksum_match_supported: true
case_only_label_difference_allowed: true
spacing_only_label_difference_allowed: true
punctuation_only_label_difference_allowed: true
canonical_alias_allowed: true
unknown_source_blocked: true
missing_citation_blocked: true
unbound_source_version_blocked: true
checksum_mismatch_blocked: true
revoked_source_blocked: true
untrusted_source_blocked: true
```
