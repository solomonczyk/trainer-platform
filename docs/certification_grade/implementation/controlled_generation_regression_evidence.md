## Controlled Generation Regression Evidence

### Focused Generation Tests

| Test File | Tests |
|-----------|-------|
| test_generation_request_contract.py | 7 |
| test_generation_rbac.py | 9 |
| test_generation_source_binding.py | 4 |
| test_generation_prompt_contract.py | 10 |
| test_generated_candidate_schema.py | 9 |
| test_generated_candidate_validation_pipeline.py | 12 |
| test_generated_candidate_duplicate_detection.py | 5 |
| test_generated_candidate_safety_gates.py | 6 |
| test_generated_candidate_provenance.py | 5 |
| test_generated_candidate_review_handoff.py | 5 |
| test_generation_pool_mutation_guards.py | 5 |
| test_migration_006_execution.py | 5 |
| **Total Focused** | **81 passed** |

### Full Certification Core Suite

**457 passed**, 0 failed, 0 errors (all 5 pre-existing migration_005_execution errors resolved)

### Full Suite Breakdown

| Suite | Passed | Failed | Errors | Skipped | Notes |
|-------|--------|--------|--------|---------|-------|
| Generation focused | 81 | 0 | 0 | 0 | Subset of full suite |
| Certification core full | 457 | 0 | 0 | 0 | Complete pass after migration fix |
| Dynamic Item Bank Runtime | 56 | 0 | 0 | 0 | Runtime + rotation + exception + eligibility + audit |
| BA Phase 1 | 5 | 0 | 0 | 0 | TestBaPhase1Regression |
| BA Phase 2 | 4 | 0 | 0 | 0 | TestBaPhase2Regression |
| QA Trainer | 5 | 0 | 0 | 0 | TestQaTrainerRegression |
| DeepSeek Gateway | 39 | 0 | 0 | 0 | All deepseek-focused tests from test_ai_gateway.py |
| Migration 005 | 5 | 0 | 0 | 0 | Real PostgreSQL cycle verified |
| Migration 006 | 5 | 0 | 0 | 0 | Real PostgreSQL cycle verified |

### Errors Resolved

All 5 pre-existing errors were in `test_migration_005_execution.py`. Root causes:
1. **ERR-M005-001 through ERR-M005-005**: Docker container `trainer-item-bank-migration-005` did not exist. Container was `trainer-migration-pg`. Fixed container/database references.
2. **ERR-M005-004 (partial)**: Alembic head changed from 005 to 006 with migration 006. Fixed revision assertion.

### Overlap

The focused generation tests (81) are a subset of the full certification_core suite (457). The unique total across all suites is 457.
