## Existing Candidate Corrective Revalidation Report

### Candidate

- **candidate_id:** `cand-c1a83dade217`
- **generation_request_id:** `gen-6db686968c0d`
- **provider:** deepseek
- **model:** deepseek-v4-flash
- **original_decision:** VALIDATION_FAILED
- **original V10:** failed (EXACT_DUPLICATE — self-match false positive)
- **original V3:** warning (CITATION_SOURCE_MISMATCH)
- **original review handoff:** not created

### Revalidation Service

**Service:** `CandidateRevalidationService` in `generation_revalidation_service.py`

**CLI:** `scripts/revalidate_existing_candidate.py`

**Usage:**
```bash
# Dry-run inspection
python scripts/revalidate_existing_candidate.py \
  --candidate-id cand-c1a83dade217 \
  --reason V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX

# Execute revalidation
python scripts/revalidate_existing_candidate.py \
  --candidate-id cand-c1a83dade217 \
  --reason V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX \
  --execute
```

**Controls:**
- `--candidate-id` required
- `--reason` required
- `--execute` flag required (without it, dry-run only)
- No generation, no provider call, no retry

### Revalidation Contract

```json
{
  "revalidation_reason": "V10_SELF_DUPLICATE_FALSE_POSITIVE_AND_V3_CITATION_IDENTITY_FIX",
  "trigger_type": "controlled_corrective_revalidation",
  "provider_call_required": false,
  "generation_required": false,
  "retry": false
}
```

### Candidate Content Verification

- Content hash computed before and after revalidation
- **content_changed:** false
- Revalidation aborts with REJECTED if hash changes

### Validator Bundle

- **validator_bundle_version:** 1.0.0
- **validation_policy_version:** 1.1.0
- **V3 validator version:** 2.0.0
- **V10 validator version:** 2.0.0

### Audit Events

New append-only audit actions:
- `candidate_corrective_revalidation_started`
- `candidate_validator_v3_corrective_run_completed`
- `candidate_validator_v10_corrective_run_completed`
- `candidate_corrective_revalidation_completed`
- `candidate_review_handoff_created_corrective`

### Provenance Update

Original provenance is preserved. Validator versions are appended:
```json
{
  "V3_corrective": "2.0.0",
  "V10_corrective": "2.0.0",
  "revalidation_policy_version": "1.1.0"
}
```
