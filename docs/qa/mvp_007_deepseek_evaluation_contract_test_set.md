# MVP-007 DeepSeek Evaluation Contract Test Set

## Purpose

Define the response contract that DeepSeek-backed staging evaluations must satisfy before MVP-007 can accept real AI behavior.

## Required Success Schema

Every accepted success-path evaluation must expose:

```json
{
  "score": "number",
  "passed": "boolean",
  "feedback": "present",
  "strengths": "array",
  "weak_points": "array",
  "criteria": "valid non-empty array",
  "ai_model_used": "deepseek-v4-flash",
  "validation_status": "validated"
}
```

## Field Requirements

| Field | Requirement |
|---|---|
| `score` or `overall_score` | Numeric, 0-100, public API field must be stable for MVP-007 evidence |
| `passed` | Boolean only |
| `feedback` | Present directly or represented by populated criterion comments/evidence in the public response |
| `strengths` | Array, may be empty only for invalid/empty answers if criteria still explain scoring |
| `weak_points` | Array |
| `criteria` | Non-empty array; each item has criterion id, numeric score, evidence, comment or improvement |
| `ai_model_used` | `deepseek-v4-flash` or clearly provider-reported DeepSeek equivalent |
| `validation_status` | `validated` for success path |
| `raw_ai_output` | May be stored server-side for audit, but must not leak secrets or be copied into proof logs |

## Contract Cases

| Case ID | Scenario | Required result |
|---|---|---|
| M7-CON-001 | good answer | Validated schema, high score, passed true, criteria non-empty |
| M7-CON-002 | weak answer | Validated schema, low or mid score, passed false, criteria non-empty |
| M7-CON-003 | empty answer | Pre-provider validation error or validated low score; no fake success |
| M7-CON-004 | malformed provider response | Safe failure or explicit fallback; not accepted as DeepSeek success |
| M7-CON-005 | provider returns reasoning-only content | Normalized into required JSON or rejected safely |
| M7-CON-006 | provider returns partial criteria | Blocker unless normalized to all required rubric criteria |
| M7-CON-007 | provider returns model alias | Accept only if alias is clearly a DeepSeek model equivalent |

## Rejection Cases

```json
{
  "validation_status_partial": "blocker",
  "criteria_empty": "blocker",
  "ai_model_used_not_deepseek": "blocker",
  "progress_not_updated": "blocker",
  "raw_answer_in_analytics": "rejected"
}
```

## Contract Acceptance Rule

MVP-007 may accept staging real AI only when success-path responses are validated, rubric criteria are non-empty, DeepSeek usage is proven, and progress/analytics behavior matches the matrix.

