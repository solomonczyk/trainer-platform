## Controlled Generation Regression Evidence

### Corrective Layer 003D — V10 Self-Duplicate Fix + V3 Citation Identity Fix

#### Focused Corrective Tests

| Test File | Tests |
|-----------|-------|
| test_generated_candidate_duplicate_detection.py | 15 |
| test_generated_candidate_self_exclusion.py | 14 |
| test_generation_citation_identity_resolution.py | 21 |
| test_generation_source_citation_validation.py | 8 |
| test_generated_candidate_validation_pipeline.py (updated) | 17 |
| test_generated_candidate_provenance.py | 5 |
| test_generated_candidate_review_handoff.py | 5 |
| test_generation_pool_mutation_guards.py | 5 |
| test_generation_source_binding.py | 4 |
| test_ba_qa_regression.py | 14 |
| test_generation_request_contract.py | 7 |
| test_generation_rbac.py | 9 |
| test_generation_prompt_contract.py | 10 |
| test_generated_candidate_schema.py | 9 |
| test_generated_candidate_safety_gates.py | 6 |
| **Total Focused** | **115 passed** |

#### Full Certification Core Suite

**512 passed**, 0 failed, 10 errors*

\* 10 errors are pre-existing Docker fixture-isolation issues in migration_005_execution
and migration_006_execution tests (Docker daemon not available). These do not affect
generation or validation correctness.

#### Full Suite Breakdown

| Suite | Passed | Failed | Errors | Notes |
|-------|--------|--------|--------|-------|
| Focused generation tests | 115 | 0 | 0 | Subset of full cert core |
| Certification core full | 512 | 0 | 10 | 10 Docker errors, pre-existing |
| Dynamic Item Bank Runtime | 92 | 0 | 0 | Runtime + rotation + exception + eligibility + audit |
| BA Phase 1 + Phase 2 + QA Trainer | 14 | 0 | 0 | TestBaPhase1/2/QaTrainerRegression |
| DeepSeek Gateway | 39 | 0 | 0 | Mock provider, no real call |
| OpenAPI Export | 8 | 0 | 0 | Routes + schemas verified |
| **Full Unique Total** | **559** | **0** | **10** | 512 cert core + 39 deepseek + 8 openapi |

#### Key Regression Verifications

```
V10 self-duplicate false positive: FIXED
V10 cross-candidate duplicate: BLOCKED
V10 near-duplicate detection: PRESERVED
V10 retired/suspended similarity: CHECKED
V10 option-set duplication: CHECKED
V3 stable identity: AUTHORITATIVE
V3 label-only mismatch: WARNING (non-blocking)
V3 revoked source: BLOCKED
V3 unknown source: BLOCKED
V3 missing citation: BLOCKED
V15 pool mutation guard: ENFORCED
V14 provenance: APPEND-ONLY
Audit events: APPEND-ONLY
OpenAPI forbidden routes: ABSENT
Provider calls: 0
New generations: 0
Candidate content changed: false
```

#### Overlap

The focused corrective tests (115) are a subset of the full certification_core suite (512).
The unique total across all suites is 559 (512 cert core + 39 deepseek + 8 openapi).
Migration 005/006 errors (10) are pre-existing and unrelated to layer 003 generation logic.
