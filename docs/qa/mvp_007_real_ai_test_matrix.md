# MVP-007 Real AI Test Matrix

## Scope

This matrix defines staging-only real AI acceptance cases for DeepSeek after MVP-006C is accepted. It is not an execution log and does not run real AI smoke by itself.

## Default Expectations

Unless a row says otherwise:

```json
{
  "expected_validation_status": "validated",
  "expected_criteria_present": true,
  "analytics_should_store_raw_answer": false
}
```

## Test Matrix

| ID | Input type | Expected score range | Expected passed | Expected validation status | Expected criteria present | Progress should update | Analytics should store raw answer | Notes |
|---|---|---:|---|---|---|---|---|---|
| M7-RAI-001 | good answer | 80-100 | true | `validated` | true | true | false | Strong structured QA bug report answer with evidence, steps, expected/actual behavior, environment, severity, and impact. |
| M7-RAI-002 | weak answer | 30-59 | false | `validated` | true | true | false | Vague answer with limited structure and little evidence. |
| M7-RAI-003 | empty answer | 0-10 | false | `validated` or safe validation error | true for evaluated response, false if rejected before provider | false if rejected before evaluation, true only if evaluated | false | Empty attempt should not create misleading success. |
| M7-RAI-004 | too short answer | 0-39 | false | `validated` | true | true | false | One-sentence answer missing most rubric requirements. |
| M7-RAI-005 | irrelevant answer | 0-29 | false | `validated` | true | true | false | Off-topic answer unrelated to QA bug reports. |
| M7-RAI-006 | partially correct answer | 60-79 | false | `validated` | true | true | false | Covers steps and expected/actual behavior but misses severity, evidence, or environment. |
| M7-RAI-007 | answer with risky/private data | 70-90 | true | `validated` | true | true | false | Synthetic private-like values only; quality can pass, but analytics and proof must not store raw answer. |
| M7-RAI-008 | answer in wrong language | 40-69 | false | `validated` | true | true | false | Evaluator should still return English JSON keys and locale-appropriate comments when requested. |
| M7-RAI-009 | repeated attempt by same user | 80-100 | true | `validated` | true | true | false | Repeat with another good answer; progress total attempts must increment again without overwriting earlier score incorrectly. |
| M7-RAI-010 | API timeout/failure path | none | false | `failed` or safe failure status | false allowed | false | false | Must not silently mark success or create fake DeepSeek model usage. |
| M7-RAI-011 | rate limit path | none | false | `failed` or safe rate-limit status | false allowed | false | false | Must return bounded, user-safe failure and no unbounded retry loop. |
| M7-RAI-012 | fallback/safe failure path | none or fallback score 0 | false | `fallback` or `failed` as designed | true only for explicit fallback payload | false unless product explicitly accepts fallback evaluations | false | Fallback must be visible, not reported as real DeepSeek success. |

## JSON Case Template

Each executed case should be recorded with this structure:

```json
{
  "case_id": "",
  "input_type": "",
  "expected_score_range": "",
  "actual_score": null,
  "expected_passed": false,
  "actual_passed": null,
  "expected_validation_status": "validated",
  "actual_validation_status": null,
  "expected_criteria_present": true,
  "actual_criteria_present": null,
  "progress_should_update": true,
  "progress_updated": null,
  "analytics_should_store_raw_answer": false,
  "raw_answer_found_in_analytics": null,
  "ai_model_used": null,
  "decision": "TBD"
}
```

## Matrix Acceptance Rule

The matrix passes only if every success-path case reports a DeepSeek model, `validation_status=validated`, non-empty criteria, expected progress behavior, and no raw-answer analytics storage. Failure-path cases pass only when they fail safely without fake success, silent fallback, unbounded retry, or secret exposure.
