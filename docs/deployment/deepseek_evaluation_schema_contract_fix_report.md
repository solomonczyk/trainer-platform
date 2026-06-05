# DeepSeek Evaluation Schema Contract Fix Report

## Summary

MVP-006C fixes the DeepSeek evaluation schema contract so that real DeepSeek evaluations
return `validation_status="validated"` instead of `"partial"`.

## Problem

When DeepSeek v4-flash (a reasoning model) returns evaluation results, the response may contain:

1. **Alternative field names** — `id` instead of `criterion_id`, `reasoning` instead of `evidence`
2. **Missing optional fields** — no `comment` or `improvement` on criterion items
3. **Empty criteria array** — `criteria: []` when the model does not populate it
4. **`reasoning_content`** — DeepSeek-specific field that could leak into persisted data
5. **Criteria as dict** — Some provider responses wrap criteria `{"id": {...}}` instead of an array

These variations cause `validate_evaluation_output()` to add validation errors, setting
`validation_status="partial"` rather than `"validated"`.

## Root Cause

The `OpenAIProviderAdapter._parse_response()` correctly extracts and parses the JSON content,
but does not normalise the provider-specific output shape to the canonical `EvaluationOutput`
schema. The schema validator is intentionally strict about field names and required fields,
so any deviation produces `partial` status.

## Fix

Added `_normalize_response()` to `OpenAIProviderAdapter` — a rubric-aware normalisation
layer that runs **only** when `provider_name == "deepseek"`.

### Normalisation steps

1. **Criteria → list of dicts** — Handles array, dict-keyed, or missing criteria input.
2. **criterion_id mapping** — Tries `criterion_id` → `id` → `criteria_id` → `criterionId`.
3. **Evidence mapping** — Tries `evidence` → `evidences` → `justification` → `reasoning`.
4. **Score coercion** — Converts float/string to int, clamped to [0, 100].
5. **Overall score fallback** — Calculated from criteria when missing; also tries `score` / `overallScore` / `total_score` aliases.
6. **Passed fallback** — Derived from `overall_score >= 70`.
7. **Missing rubric criteria** — Filled from rubric with score defaulting to overall_score.
8. **Extra criteria filtered** — When rubric exists, non-rubric criteria are removed.
9. **Evidence default** — Safe text fallback when no evidence alias is present.
10. **reasoning_content stripped** — Removed from output dict.
11. **feedback field** — Built from first available criterion detail.
12. **List/coercion safety** — `strengths`, `weak_points`, `critical_errors` always lists.
13. **Confidence clamping** — Float clamped to [0.0, 1.0].

## Files Changed

| File | Change |
|---|---|
| `backend/app/ai_gateway/adapters/openai_adapter.py` | Added `_normalize_response()`, `_rubric_criteria()`, `_build_feedback()`, `_first_present()`, `_normalize_score()`, `_normalize_bool()`, alias tuples |
| `backend/tests/test_ai_gateway.py` | Added `TestDeepSeekSchemaNormalization` (27 tests), `TestDeepSeekValidatorContract` (4 contract tests) |

## Test Results

- **105 passed**, 3 skipped (frontend locale)
- 31 new DeepSeek-specific tests added:
  - 4 criterion_id alias tests
  - 4 evidence alias tests  
  - 6 score normalisation tests
  - 2 overall_score fallback tests
  - 2 passed derivation tests
  - 2 list field safety tests
  - 5 confidence tests
  - 2 reasoning_content tests
  - 3 full validation flow tests
  - 1 gateway service flow test
  - 3 contract validation tests
  - 1 dict-format criteria test
  - 1 missing rubric criterion fill test
- All existing tests remain green

## Schema Contract After Fix

```json
{
  "overall_score": 85,
  "passed": true,
  "criteria": [
    {
      "criterion_id": "structure",
      "score": 90,
      "evidence": "Well organized answer",
      "comment": "",
      "improvement": ""
    }
  ],
  "strengths": ["Good structure"],
  "weak_points": [],
  "critical_errors": [],
  "next_recommendation": {"action": "advance", "suggestion": "Proceed", "target_score": 90},
  "confidence": 0.88,
  "feedback": "Well organized answer"
}
```

## Deployment

Backend must be redeployed to Railway staging after merge. See:
[docs/deployment/real_llm_provider_staging_env_vars.md](real_llm_provider_staging_env_vars.md)
