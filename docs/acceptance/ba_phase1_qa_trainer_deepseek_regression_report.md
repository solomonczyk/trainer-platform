# BA Trainer Phase 1 — QA Trainer DeepSeek Regression Report

## Overview

Verified that the QA Engineer Interview Trainer completes a real DeepSeek AI evaluation
through the deployed Railway staging environment.

## Test Details

| Setting | Value |
|---------|-------|
| QA Trainer | ✅ Available (5 scenarios) |
| Scenario Used | `qa_bug_report_structure_v1` |
| AI Provider | **deepseek** |
| AI Model | **deepseek-v4-flash** |
| Validation Status | **validated** |
| OpenAI Used | ❌ false |

## Evaluation Result

| Metric | Value |
|--------|-------|
| Overall Score | 75 |
| Evaluation Completed | ✅ |
| Score Returned | ✅ |
| Feedback Returned | ✅ (criteria array populated) |
| Progress Updated | ✅ |

## Regression Status

**PASS** — The QA Trainer real DeepSeek evaluation completes successfully.
The model used is `deepseek-v4-flash` (not GPT, not mock), with full validation.
No provider configuration was changed during this acceptance run.

## Evidence

- `evidence/ba_phase1_real_browser_acceptance_005/qa_deepseek_regression/`
- API: `POST /api/v1/scenarios/{id}/start`
- API: `POST /api/v1/sessions/{id}/messages`
- API: `POST /api/v1/sessions/{id}/complete`
- API: `POST /api/v1/attempts/{id}/evaluate`
