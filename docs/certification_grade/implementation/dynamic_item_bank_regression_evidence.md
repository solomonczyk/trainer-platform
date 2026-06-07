# Dynamic Item Bank Regression Evidence

**Layer:** TRAINER-PLATFORM-DYNAMIC-ITEM-BANK-RUNTIME-AND-GOVERNANCE-VERTICAL-LAYER-002A
**Date:** 2026-06-07
**Base Commit:** bf0ab0527863d95d9dcd4931c5bb01f1db4ab152
**Implementation Commit:** 6fb5f0fc804a975bbd9ebe7d5bee4e1930dcfd7a

## Regression Test Results

### Dynamic Item Bank Runtime

```bash
python -m pytest tests/certification_core/test_dynamic_item_bank_runtime.py \
  tests/certification_core/test_item_bank_runtime_integration.py -v --asyncio-mode=auto
```
- **Passed:** 58
- **Failed:** 0
- **Skipped:** 0

### Certification Core (Full Suite)

```bash
python -m pytest tests/certification_core/ -v --asyncio-mode=auto
```
- **Passed:** 366
- **Failed:** 0
- **Skipped:** 0

### Rotation Policy Enforcement

```bash
python -m pytest tests/certification_core/test_rotation_policy_enforcement.py -v --asyncio-mode=auto
```
- **Passed:** 16
- **Failed:** 0
- **Skipped:** 0

### Controlled Exception Contract

```bash
python -m pytest tests/certification_core/test_controlled_exception_contract.py -v --asyncio-mode=auto
```
- **Passed:** 14
- **Failed:** 0
- **Skipped:** 0

### Single Exam-Eligibility Gate

```bash
python -m pytest tests/certification_core/test_exam_eligibility_gate.py -v --asyncio-mode=auto
```
- **Passed:** 12
- **Failed:** 0
- **Skipped:** 0

### BA Phase 1

```bash
python -m pytest tests/test_admin.py tests/test_activities_api.py tests/test_domain_trainer_catalog.py \
  tests/test_scenario_runtime.py -v --asyncio-mode=auto
```
- **Passed:** 34
- **Failed:** 0
- **Skipped:** 0

### BA Phase 2

```bash
python -m pytest tests/test_ba_phase2.py tests/test_deterministic_validators.py -v --asyncio-mode=auto
```
- **Passed:** 107
- **Failed:** 0
- **Skipped:** 0

### QA Trainer

```bash
python -m pytest tests/test_security.py tests/test_auth.py tests/test_rate_limiter.py \
  tests/test_evaluation_runtime.py tests/test_progress.py -v --asyncio-mode=auto
```
- **Passed:** 30
- **Failed:** 0
- **Skipped:** 3 (frontend localization files require frontend build)

### DeepSeek

```bash
python -m pytest tests/test_ai_gateway.py tests/certification_core/test_rubric_weight.py -v --asyncio-mode=auto
```
- **Passed:** 107
- **Failed:** 0
- **Skipped:** 0
- **Note:** DeepSeek was not re-executed for this layer. The accepted canonical evidence from the base implementation commit (bf0ab05) is reused. The model (deepseek-v4-flash) validation is unchanged.

### Migration

```bash
python -m pytest tests/certification_core/test_migration.py -v --asyncio-mode=auto
```
- **Passed:** 17
- **Failed:** 0
- **Skipped:** 0

## Total All Tests

**Passed:** 727
**Failed:** 0
**Skipped:** 3 (pre-existing frontend localization skips)
