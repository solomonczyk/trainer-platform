## Generated Item Validation Pipeline

### Validator List

| Code | Name | Severity | Description |
|------|------|----------|-------------|
| V1 | Schema Validation | critical | Validates JSON structure against schema |
| V2 | Required Fields | critical | Checks all required fields present and non-empty |
| V3 | Source Citations (v2.0.0) | major | Validates source citations via stable identity resolution |
| V4 | Competency Alignment | major | Validates competency and domain alignment |
| V5 | Difficulty Alignment | major | Validates difficulty level |
| V6 | Item Family Compliance | major | Validates item family binding |
| V7 | Answer/Options Consistency | critical | Validates MC options and answer key |
| V8 | Rubric Consistency | major | Validates rubric structure |
| V9 | Ambiguity Detection | minor | Detects ambiguous language |
| V10 | Duplicate/Similarity (v2.0.0) | major | Detects exact and near duplicates with self-exclusion |
| V11 | Prohibited Content/Safety | critical | Detects unsafe content |
| V12 | Locale Validation | major | Validates locale match |
| V13 | Answer Key Leak | critical | Detects answer markers in learner text |
| V14 | Provenance Completeness | major | Validates provenance record |
| V15 | Pool Mutation Guard | critical | Blocks pool mutations |

### Corrective Updates (Layer 003D)

**V10 v2.0.0 — Self-Exclusion:**

Accepts `validation_context` dict with `current_candidate_id`. Excludes self-records
from the duplicate comparison set. Same hash + different candidate ID = real duplicate
(still blocked). Evidence includes comparison counts before/after self-exclusion.

See: [V10 Corrective Report](v10_self_duplicate_corrective_report.md)

**V3 v2.0.0 — Stable Source Identity:**

Identity resolution precedence:
1. `source_version_id` exact match (authoritative)
2. `source_id` cross-reference via canonical label map
3. Source checksum match
4. Normalized canonical label comparison
5. Display-label-only mismatch → non-blocking warning

Label normalization: Unicode NFKC, case-fold, whitespace collapse, punctuation removal.
New `source_registry` parameter enables revocation/deprecation detection.

See: [V3 Corrective Report](v3_citation_identity_corrective_report.md)

### Policy Version

- **VALIDATION_POLICY_VERSION:** 1.1.0 (was 1.0.0)

### Decision Rules

- **REJECTED**: any critical failure → candidate rejected, no review handoff
- **VALIDATION_FAILED**: major failures but no critical → validation_failed, no handoff
- **READY_FOR_HUMAN_REVIEW**: no critical or major failures → handoff created
- Warnings alone do not block handoff

### Validation Result Format

```json
{
  "validator_code": "V1",
  "validator_version": "1.0.0",
  "status": "passed|failed|warning|not_run",
  "severity": "info|minor|major|critical",
  "reason_code": "string",
  "details": {},
  "executed_at": "timestamp"
}
```

### Corrective Revalidation

The `CandidateRevalidationService` enables deterministic revalidation of existing
candidates without provider calls. Usage:

```bash
python scripts/revalidate_existing_candidate.py \
  --candidate-id cand-c1a83dade217 \
  --reason V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX \
  --execute
```

See: [Revalidation Report](existing_candidate_revalidation_report.md)
