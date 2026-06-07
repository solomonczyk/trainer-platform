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
| **Total Focused** | **86 passed** |

### Full Certification Core Suite

**452 passed**, 5 pre-existing errors in migration_005_execution (requires specific Docker container)

### Existing Regression Suites

| Suite | Passed | Notes |
|-------|--------|-------|
| Dynamic Item Bank Runtime | 92 passed | Combined suite |
| BA Phase 1 | 34 passed | Evidence reused |
| BA Phase 2 | 107 passed | Evidence reused |
| QA Trainer | 30 passed, 3 skipped | Evidence reused |

### Overlap

The focused generation tests (86) are a subset of the full certification_core suite (452). The true unique total across all suites is approximately 544.
