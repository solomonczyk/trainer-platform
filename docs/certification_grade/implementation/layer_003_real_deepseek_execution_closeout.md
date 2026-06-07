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
| Key available | ❌ (DEEPSEEK_API_KEY not in environment) |
| Key exposed | ❌ |
| OpenAI used | ❌ |
| Silent fallback | ❌ |

## Real Controlled Generation

**NOT EXECUTED** — The DEEPSEEK_API_KEY is not available in the execution environment.

All preconditions are in place:
- Provider adapter correctly resolves for 'deepseek'
- OpenAIProviderAdapter selects base_url 'https://api.deepseek.com' when provider_name='deepseek'
- _resolve_api_key() falls back to DEEPSEEK_API_KEY env var
- Generation service correctly routes through AI Gateway
- All 15 validators (V1-V15) are implemented and tested

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

## Final Verdict

```json
{
  "TRAINER_PLATFORM_CONTROLLED_ITEM_GENERATION_AND_AUTOMATED_VALIDATION_VERTICAL_LAYER_003": "ACCEPTED_WITH_BLOCKERS",
  "real_deepseek_execution": "BLOCKED — DEEPSEEK_API_KEY UNAVAILABLE",
  "automated_validation_pipeline": "VERIFIED",
  "certification_core_regression": "PASSED (errors resolved)",
  "migration_head": "006",
  "blockers": [
    "DEEPSEEK_API_KEY not available in execution environment"
  ],
  "next_allowed_action": "NEEDS_OPERATOR_ACTION"
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

1. **OPERATOR ACTION REQUIRED**: Set DEEPSEEK_API_KEY in the execution environment
2. After key is available, re-execute steps 6-9 of the closeout task: real generation preflight → execution → validation pipeline → review handoff
3. If candidate passes validation (READY_FOR_HUMAN_REVIEW), proceed to Layer 004 (Human Review)
4. If candidate fails validation, document failure reason and adjust prompt/source configuration without retry
