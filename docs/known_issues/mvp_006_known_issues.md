# Known Issues - MVP-006 Real OpenAI Staging Gate

## 1. OpenAI Staging Secret Missing

**Status**: OPEN

**Severity**: BLOCKER

**Description**: Railway staging backend does not currently have `OPENAI_API_KEY` configured. Real OpenAI cannot be enabled or smoke-tested without this secret.

**Required action**: Operator must add `OPENAI_API_KEY` as a Railway staging backend secret only. Do not commit it to the repository.

## 2. Required MVP-006 Variable Names Need Mapping Verification

**Status**: OPEN

**Severity**: BLOCKER BEFORE REAL SMOKE

**Description**: The MVP-006 task specifies `AI_PROVIDER`, `AI_MODEL_EVALUATOR`, `AI_TIMEOUT_SECONDS`, and related names. The current backend settings use the existing AI Gateway names such as `AI_GATEWAY_PROVIDER`, `AI_GATEWAY_MODEL`, and `AI_GATEWAY_TIMEOUT_SECONDS`.

**Required action**: On rerun, verify the staging environment sets variables that the deployed backend actually reads, or add a safe compatibility mapping before enabling real OpenAI.

## 3. Real Provider Smoke Not Executed

**Status**: OPEN

**Severity**: BLOCKER

**Description**: The controlled real-provider smoke test was not executed because the key is unavailable.

**Required action**: After the staging secret is configured, rerun MVP-006 from the provider/model validation step.

## Non-Issues

- No secret was printed or committed.
- Real OpenAI was not enabled in staging or production.
- Production acceptance and release allowance remain false.
