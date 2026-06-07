# Dynamic Item Bank Regression Evidence

**Layer:** TRAINER-PLATFORM-DYNAMIC-ITEM-BANK-RUNTIME-AND-GOVERNANCE-VERTICAL-LAYER-002
**Closeout:** MIGRATION_005_EXECUTION_CLOSEOUT_002B
**Date:** 2026-06-07
**Final Implementation Commit:** b4a396c3e4476ea12c0f41742387d61409dba312

## Regression Test Results

All tests executed against a temporary PostgreSQL 16 container. No test database credentials committed.

### Migration 005 Execution

```bash
python -m pytest tests/certification_core/test_migration_005_execution.py -v
```
- **Passed:** 5
- **Failed:** 0
- **Skipped:** 0

Proves: upgrade head → 005, downgrade 004, upgrade head → 005, schema removal/restoration.

### Rotation Policy Enforcement

```bash
python -m pytest tests/certification_core/test_rotation_policy_enforcement.py -v
```
- **Passed:** 16
- **Failed:** 0
- **Skipped:** 0

### Controlled Exception Contract

```bash
python -m pytest tests/certification_core/test_controlled_exception_contract.py -v
```
- **Passed:** 14
- **Failed:** 0
- **Skipped:** 0

### Single Exam-Eligibility Gate

```bash
python -m pytest tests/certification_core/test_exam_eligibility_gate.py -v
```
- **Passed:** 12
- **Failed:** 0
- **Skipped:** 0

### Certification Core (Full Suite)

```bash
python -m pytest tests/certification_core/ -v
```
- **Passed:** 371
- **Failed:** 0
- **Skipped:** 0

### BA Phase 1

```bash
python -m pytest tests/test_admin.py tests/test_activities_api.py tests/test_domain_trainer_catalog.py \
  tests/test_scenario_runtime.py -v
```
- **Passed:** 34
- **Failed:** 0
- **Skipped:** 0

(Reused from canonical evidence, not re-executed in this closeout.)

### BA Phase 2

```bash
python -m pytest tests/test_ba_phase2.py tests/test_deterministic_validators.py -v
```
- **Passed:** 107
- **Failed:** 0
- **Skipped:** 0

(Reused from canonical evidence, not re-executed in this closeout.)

### QA Trainer

```bash
python -m pytest tests/test_security.py tests/test_auth.py tests/test_rate_limiter.py \
  tests/test_evaluation_runtime.py tests/test_progress.py -v
```
- **Passed:** 30
- **Failed:** 0
- **Skipped:** 3 (frontend localization)

(Reused from canonical evidence, not re-executed in this closeout.)

### DeepSeek

- **Executed in this closeout:** false
- **Reused canonical evidence:** true
- **Evidence commit:** bf0ab05
- **Model:** deepseek-v4-flash
- **Validation status:** validated

## Count Summary

| Category | Count |
|---|---|
| Focused runs total (migration + rotation + exception + gate) | 47 |
| Full certification core suite (unique) | 371 |
| Pre-existing BA/QA/Trainer (from canonical evidence) | 171 |
| DeepSeek tests (from canonical evidence) | 107 |
| Overlap documented | Focused runs are subsets of the full certification core suite |

## Total

- **Certification core suite:** 371 passed (includes migration, rotation, exception, gate, and all other cert tests)
- **No regressions introduced**
