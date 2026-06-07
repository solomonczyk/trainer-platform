# Core Contracts Test Report

**Document ID:** CGSF-IMPL-TEST-001  
**Date:** 2026-06-07  

## Test Results

### Certification Core Tests: 190 passed ✅

| Test Group | Tests | Status |
|------------|-------|--------|
| competency_contract_tests | 10 | ✅ Passed |
| blueprint_validation_tests | 12 | ✅ Passed |
| knowledge_registry_version_tests | 13 | ✅ Passed |
| item_schema_tests | 18 | ✅ Passed |
| item_versioning_tests | 3 | ✅ Passed |
| lifecycle_transition_tests | 13 | ✅ Passed |
| forbidden_transition_tests | 9 | ✅ Passed |
| rubric_weight_tests | 12 | ✅ Passed |
| domain_pack_validation_tests | 8 | ✅ Passed |
| audit_append_only_tests | 18 | ✅ Passed |
| rbac_tests | 21 | ✅ Passed |
| learner_answer_key_protection_tests | 6 | ✅ Passed |
| migration_tests | 16 | ✅ Passed |
| ba_qa_regression_tests | 14 | ✅ Passed |
| openapi_export_tests | 9 | ✅ Passed |

### Existing Regression Tests: 183 passed, 3 skipped ✅

| Suite | Tests | Status |
|-------|-------|--------|
| BA Phase 1 regression | — | ✅ No regression |
| BA Phase 2 regression | — | ✅ No regression |
| QA Trainer regression | — | ✅ No regression |

### Total: 373 passed, 3 skipped ✅

## Key Validations Verified

- ✅ Competency frameworks validate required fields, statuses, cognitive levels, weights
- ✅ Blueprint sections enforce total weight = 100%, item bounds, difficulty distributions
- ✅ Knowledge sources validate types, statuses, URLs, versions
- ✅ Items validate types, difficulties, compromise risks, statuses
- ✅ Item families validate types and statuses
- ✅ Item versions track version history with unique constraints
- ✅ Lifecycle state machine enforces 12+ states with allowed/forbidden transitions
- ✅ Forbidden transitions: draft→exam_eligible, generated→exam_eligible, etc. (9 forbidden paths documented and enforced)
- ✅ Rubrics enforce total weight = 100%, unique criterion IDs, valid weights
- ✅ Domain packs validate required fields, statuses, supported modes
- ✅ Audit events have append-only design, before/after hashing, query filters
- ✅ RBAC enforces 7 roles with distinct permission sets
- ✅ Answer keys protected from learner/guest roles
- ✅ Self-approval prevention for content_authors and domain_owners
- ✅ LLM self-approval blocked for expert and domain-owner gates
- ✅ Migration adapter structure verified
- ✅ Existing BA/QA content confirmed unchanged
- ✅ OpenAPI export generates 46 paths
