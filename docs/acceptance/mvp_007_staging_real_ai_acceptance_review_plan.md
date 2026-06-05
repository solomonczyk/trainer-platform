# MVP-007 Staging Real AI Acceptance Review Plan

## Layer
TRAINER-PLATFORM-MVP-007-STAGING-REAL-AI-ACCEPTANCE-REVIEW

## Purpose

Prepare the final staging acceptance framework after DeepSeek schema validation is proven.

```json
{
  "purpose": "final staging acceptance after DeepSeek schema is validated",
  "entry_condition": "MVP-006C accepted with validation_status=validated",
  "exit_condition": "staging real AI accepted or rejected with blockers",
  "production_accepted": false,
  "release_allowed": false
}
```

## Scope

This plan is documentation, QA planning, and test dataset preparation only. It does not change backend code, frontend code, AI Gateway code, Railway variables, provider secrets, trainers, payments, production settings, or launch posture.

## Entry Conditions

MVP-007 review may begin only when all conditions are true:

| Condition | Required value |
|---|---|
| MVP-006C accepted | true |
| DeepSeek evaluation status | `validated` |
| Criteria schema contract | non-empty, rubric-aligned criteria array |
| Progress after real DeepSeek evaluation | verified |
| OpenAI enabled | false |
| Production accepted | false |
| Release allowed | false |

## Review Workflow

1. Confirm MVP-006C proof is accepted and includes `validation_status=validated`.
2. Run the MVP-007 real AI test matrix using staging-only synthetic users.
3. Verify each evaluation response satisfies the DeepSeek evaluation contract.
4. Verify progress updates only when an evaluation is accepted by the service.
5. Verify analytics events contain privacy-safe metadata and never store raw answers.
6. Verify timeout, fallback, rate-limit, and cost guardrails.
7. Record findings in the MVP-007 proof JSON and known issues file.
8. Decide one of: `ACCEPTED`, `ACCEPTED_WITH_BLOCKERS`, `REJECTED`, or `NEEDS_FIX`.

## Acceptance Criteria

MVP-007 is accepted only if:

| Area | Requirement |
|---|---|
| Real provider | `ai_model_used` is `deepseek-v4-flash` or a clearly provider-reported DeepSeek equivalent |
| Evaluation schema | `validation_status=validated`, score numeric, passed boolean, feedback present, strengths array, weak_points array, criteria non-empty |
| Progress | total attempts increments, average score updates, completed scenarios updates when passed |
| Analytics privacy | raw answer absent from analytics, secrets absent from proof/log excerpts |
| Guardrails | timeout, cost cap, rate limit, safe failure, and retry limits verified |
| OpenAI | absent/disabled |
| Production/release | `production_accepted=false`, `release_allowed=false` |

## Rejection Criteria

MVP-007 must be rejected if any of the following occur:

| Blocker | Decision |
|---|---|
| `validation_status=partial` for accepted success case | blocker |
| criteria missing or empty | blocker |
| `ai_model_used` is not DeepSeek | blocker |
| progress not updated after valid evaluation | blocker |
| raw answer appears in analytics | rejected |
| provider secret exposed | rejected |
| OpenAI enabled | rejected |
| production acceptance or release flag set true | rejected |

## Output Artifacts

MVP-007 review must produce:

- completed real AI test matrix
- completed DeepSeek evaluation contract results
- progress, analytics, and privacy verification results
- fallback, timeout, rate-limit, and cost guardrail evidence
- final MVP-007 proof JSON
- known issues and blocker disposition

## Current State

This pack is prepared before MVP-006C is accepted. The next allowed action is to wait for the MVP-006C result.

