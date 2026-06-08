## V10 Self-Duplicate False Positive — Corrective Report

### Issue

The V10 duplicate/similarity validator returned `EXACT_DUPLICATE` (major failure) when a
generated candidate was compared against itself. The root cause was that the comparison
set included records created in the same persistence transaction — the candidate's own
normalized payload was in the database before validation ran.

### Root Cause

```
validator: V10
root_cause: "Candidate was compared against itself — _load_existing_candidates queried
all candidates for the generation_request_id, including the candidate that was just
persisted before validation."
current_candidate_id_was_in_comparison_set: true
current_candidate_hash_was_in_comparison_set: true
same_logical_candidate_duplicate_rows_found: true
query_or_repository_layer_at_fault: "_load_existing_candidates in GenerationService"
fix_location: "validate_duplicate — accept validation_context with current_candidate_id"
```

The original `validate_duplicate` function received `existing_candidates` containing all
candidates for the same generation request (including the current candidate). Since the
candidate was already flushed to the database before validation, its own stem text matched
itself via SHA-256 hash comparison, producing an exact duplicate false positive.

### Fix

**Validator version:** `V10 → 2.0.0`

**Change:** Added `validation_context` parameter with self-exclusion rules:

```python
def validate_duplicate(
    candidate: dict,
    existing_candidates: list[dict],
    threshold: float = 0.85,
    validation_context: dict | None = None,
) -> ValidatorResult:
```

**Self-exclusion rules:**

| Rule | Condition | Effect |
|------|-----------|--------|
| 1 | same `candidate_id` | Excluded (self record) |
| 2 | same payload hash AND same `candidate_id` | Excluded (projection match) |
| 3 | same stem text AND same `candidate_id` | Excluded (soft projection) |

**Critical invariant:** Same hash WITHOUT same `candidate_id` → real duplicate, BLOCKED.

**Evidence tracking added:**

- `comparison_candidate_count_before_self_exclusion`
- `self_records_excluded`
- `comparison_candidate_count_after_self_exclusion`
- `matched_other_candidate_ids`
- `threshold_version`

### Preserved Checks

- Exact normalized-text hash (stem)
- Exact normalized-payload hash
- Cross-generation duplicates
- Same-family duplicates
- Same-source duplicates
- Option-set duplication (stem + options)
- Jaccard semantic similarity
- Near-duplicate warnings

### Tests Added

- `test_generated_candidate_duplicate_detection.py` (15 tests)
- `test_generated_candidate_self_exclusion.py` (14 tests)

### Verification

```
candidate_not_duplicate_of_itself: true
same_candidate_projection_excluded: true
different_candidate_same_hash_blocked: true
near_duplicate_detection_preserved: true
retired_and_suspended_similarity_preserved: true
option_set_duplicate_checked: true
same_family_duplicate_checked: true
```
