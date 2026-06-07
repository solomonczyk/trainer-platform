# Layer 003 — Real DeepSeek Execution and Regression Closeout

## Closeout Date

2026-06-07

## Starting State

```json
{
  "layer_003": "ACCEPTED_WITH_BLOCKERS",
  "controlled_generation_runtime": "IMPLEMENTED",
  "automated_validation_pipeline": "IMPLEMENTED",
  "real_deepseek_generation": "NOT_EXECUTED",
  "last_provider_adapter": "MockProviderAdapter",
  "last_provider_reported_model": "mock-model",
  "certification_core_regression": "FAILED_WITH_5_ERRORS"
}
```

## Preflight Results

| Check | Result |
|------|--------|
| Branch | master |
| Starting commit | ac8411d2e2fea249a3bd2cb71613ab3d1701d6d3 |
| Git clean | ✅ |
| HEAD matches origin/master | ✅ |

## Regression Error Diagnosis

### 5 Errors — All in test_migration_005_execution.py

| Error | Test | Root Cause | Classification | Fixed |
|-------|------|-----------|---------------|-------|
| ERR-M005-001 | test_cycle_upgrade_downgrade_upgrade | Docker container 'trainer-item-bank-migration-005' not found; database 'trainer_item_bank_closeout' not found | fixture_isolation | ✅ |
| ERR-M005-002 | test_all_tables_preserved_after_cycle | Same container/database connectivity | fixture_isolation | ✅ |
| ERR-M005-003 | test_core_contract_table_count | Same + cert_ table count changed 22→31 with 006 | fixture_isolation / migration_conflict | ✅ |
| ERR-M005-004 | test_alembic_revision_matches_005 | Alembic head is now 006, test expected 005 | migration_conflict | ✅ |
| ERR-M005-005 | test_database_queryable | Same container connectivity | fixture_isolation | ✅ |

### Fix Applied

Narrowest valid fix in `test_migration_005_execution.py`:
1. `_pg()` function: Updated container to `trainer-migration-pg`, database to `trainer_platform`, added POSTGRES_MIGRATION_URL support
2. `test_cycle_upgrade_downgrade_upgrade`: Accept head revision (006) as final; still verify 005-specific columns/indexes
3. `test_all_tables_preserved_after_cycle`: Updated table count to 60 (inclusive of 006)
4. `test_core_contract_table_count`: Updated cert_ table count to 31
5. `test_alembic_revision_matches_005`: Renamed to `test_alembic_revision_matches_head`, accepts 006
6. All 5 tests pass independently and with 006 tests (order-independent)

## DeepSeek Configuration

| Item | Value |
|------|-------|
| Provider | deepseek |
| Configured model | deepseek-v4-flash |
| Base URL | https://api.deepseek.com |
| AI Gateway used | ✅ |
| Provider adapter | OpenAIProviderAdapter(provider_name='deepseek') |
| Key available | ✅ (DEEPSEEK_API_KEY set via environment) |
| Key exposed | ❌ |
| OpenAI used | ❌ |
| Silent fallback | ❌ |

## Real Controlled Generation

**EXECUTED SUCCESSFULLY** — One real DeepSeek generation request completed.

### Generation Flow

| Step | Result |
|------|--------|
| Create request (provider=deepseek, model=deepseek-v4-flash) | ✅ gen-6db686968c0d |
| Authorize (different user, self-auth blocked) | ✅ status=authorized |
| Bind trusted source (src-ba-swdev-v1.0) | ✅ 1 binding |
| Execute generation — 1 candidate, no retry | ✅ provider_call_executed=true |
| Provider adapter | OpenAIProviderAdapter(provider_name='deepseek') |
| Provider reported model | deepseek-v4-flash |
| Raw response stored | ✅ |
| Candidate normalized | ✅ cand-c1a83dade217 |

### Validation Results (V1–V15)

| Validator | Status | Details |
|-----------|--------|---------|
| V1 — Schema | ✅ passed | |
| V2 — Required fields | ✅ passed | |
| V3 — Source citations | ⚠️ warning | CITATION_SOURCE_MISMATCH: source "BA_SD_BP_v1.0" ≠ expected "src-ba-swdev-v1.0" |
| V4 — Competency alignment | ✅ passed | |
| V5 — Difficulty | ✅ passed | |
| V6 — Item family | ✅ passed | |
| V7 — Answer consistency | ✅ passed | |
| V8 — Rubric | ✅ passed | |
| V9 — Ambiguity | ✅ passed | |
| V10 — Duplicate | ❌ failed | EXACT_DUPLICATE: self-match false positive (candidate compared against itself) |
| V11 — Safety | ✅ passed | |
| V12 — Locale | ✅ passed | |
| V13 — Answer key leak | ✅ passed | |
| V14 — Provenance | ✅ passed | |
| V15 — Pool mutation guard | ✅ passed | |

### Aggregate

| Metric | Value |
|--------|-------|
| Passed | 13 |
| Failed | 1 (V10 — self-duplicate false positive) |
| Warnings | 1 (V3 — citation source label mismatch) |
| Critical | 0 |
| Major | 1 |
| **Decision** | **VALIDATION_FAILED** |

### Analysis

The V10 failure is a **false positive**: the duplicate detection validator compares the freshly-flushed candidate against the existing candidate list, which includes the same candidate just inserted. This is a known pre-existing issue where the validator does not exclude the current candidate_id from the comparison.

The V3 warning is a **cosmetic mismatch**: the DeepSeek-generated item cited source "BA_SD_BP_v1.0" (a reasonable abbreviation), while the expected source ID was "src-ba-swdev-v1.0". The content is substantively correct.

## Review Handoff

**NOT CREATED** — Decision is VALIDATION_FAILED, not READY_FOR_HUMAN_REVIEW. This is correct behavior per the validation pipeline contract.

## Provenance & Audit

| Check | Result |
|-------|--------|
| Candidate provenance record | ✅ Created (provider=deepseek, model=deepseek-v4-flash) |
| Audit events | ✅ generation_request_created → authorized → generation_started → provider_call_completed → candidate_normalized → candidate_validation_started → candidate_validation_failed → generation_request_completed |
| Raw response stored | ✅ In GenerationRawResponse table |
| Validator versions recorded | ✅ All 15 validators at v1.0.0 |
| Prompt hash recorded | ✅ 888fd326154cf69945df6ffffad60c1d0b4eaadc4dad5d184053d320c471e7e0 |

## Test Results

| Suite | Passed | Failed | Errors | Skipped |
|-------|--------|--------|--------|---------|
| Focused generation (81 tests) | 81 | 0 | 0 | 0 |
| Migration 005 | 5 | 0 | 0 | 0 |
| Migration 006 | 5 | 0 | 0 | 0 |
| Dynamic Item Bank + Rotation + Exception + Eligibility + Audit | 56 | 0 | 0 | 0 |
| BA Phase 1 | 5 | 0 | 0 | 0 |
| BA Phase 2 | 4 | 0 | 0 | 0 |
| QA Trainer | 5 | 0 | 0 | 0 |
| DeepSeek Gateway | 39 | 0 | 0 | 0 |
| **Certification Core Full** | **457** | **0** | **0** | **0** |

## Migration Cycle

| Step | Result |
|------|--------|
| 005 upgrade cycle (downgrade 004 → upgrade head) | ✅ |
| 006 upgrade cycle (downgrade 005 → upgrade head) | ✅ |
| Order-independence verified | ✅ |
| BA/QA tables preserved | ✅ |
| Current revision | 006 |

## OpenAPI

| Check | Result |
|-------|--------|
| Export | ✅ (80 paths, 96 schemas) |
| Generation routes | ✅ (5 routes) |
| Validation routes | ✅ (GET /candidates/{id}/validation) |
| Provenance routes | ✅ (GET /candidates/{id}/provenance) |
| Review handoff routes | ✅ (GET /candidates/{id}/review-handoff) |
| Publish routes absent | ✅ |
| Exam assembly routes absent | ✅ |
| Answer keys absent from learner schemas | ✅ |
| Raw provider output absent from learner schemas | ✅ |
| Audit mutation routes absent | ✅ |

## Mandatory Proof Checklist

| Requirement | Result |
|-------------|--------|
| provider_call_executed=true | ✅ |
| mock_adapter_used=false | ✅ (OpenAIProviderAdapter with provider_name='deepseek') |
| provider=deepseek | ✅ |
| provider_reported_model=deepseek-v4-flash | ✅ |
| real_generation_requests=1 | ✅ |
| candidates_requested=1 | ✅ |
| automatic_retry_executed=false | ✅ |
| review_handoff state matches decision | ✅ (no handoff for VALIDATION_FAILED) |
| certification_core=457 passed, 0 failed, 0 errors | ✅ |
| production_accepted=false | ✅ |
| release_allowed=false | ✅ |

## Final Verdict

```json
{
  "TRAINER_PLATFORM_CONTROLLED_ITEM_GENERATION_AND_AUTOMATED_VALIDATION_VERTICAL_LAYER_003": "ACCEPTED_WITH_BLOCKERS",
  "real_deepseek_execution": "EXECUTED — VALIDATION_FAILED (V10 self-duplicate false positive)",
  "automated_validation_pipeline": "VERIFIED",
  "certification_core_regression": "PASSED (errors resolved)",
  "migration_head": "006",
  "blockers": [
    "V10 EXACT_DUPLICATE false positive — validator does not exclude current candidate from comparison"
  ],
  "next_allowed_action": "ANALYZE_VALIDATION_FAILURE_V10"
}
```

## Forbidden Actions

All forbidden actions are confirmed as NOT executed:
- ❌ No second real generation
- ❌ No automatic retry
- ❌ No manual retry
- ❌ No exam form assembly
- ❌ No pilot pool mutation
- ❌ No exam-eligible pool mutation
- ❌ No generated item auto-publication
- ❌ No automatic human acceptance
- ❌ No BA/QA migration executed
- ❌ No production deployed
- ❌ production_accepted: false
- ❌ release_allowed: false
- ❌ No OpenAI used
- ❌ No secrets exposed

## Next Steps

1. **ANALYZE V10 false positive**: The duplicate detection validator (V10) should exclude the current candidate_id from comparison. Fix the validator to skip self-comparison.
2. **Address V3 citation label mismatch**: Align source citation labels between the generation prompt and the validation expectations, or make V3 tolerant of minor label differences.
3. **After V10 fix**: Re-run a single real DeepSeek generation to verify V10 passes with a non-duplicate candidate.
4. **If V10+V3 pass → READY_FOR_HUMAN_REVIEW**: Proceed to Layer 004 (Human Review).
