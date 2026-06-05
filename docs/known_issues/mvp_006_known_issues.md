# Known Issues - MVP-006 Real LLM Provider Staging Gate

## Selected Provider

DeepSeek

## 1. DeepSeek Staging Secret Missing

**Status**: OPEN

**Severity**: BLOCKER

**Description**: Railway staging backend does not currently have `DEEPSEEK_API_KEY` configured. The real LLM provider cannot be enabled or smoke-tested without this secret.

**Required action**: Operator must add `DEEPSEEK_API_KEY` as a Railway staging backend secret only. Do not commit it to the repository.

## 2. Required MVP-006 Variable Names Need Mapping Verification

**Status**: OPEN

**Severity**: BLOCKER BEFORE REAL SMOKE

**Description**: The MVP-006 task now specifies provider-neutral names such as `AI_PROVIDER`, `AI_MODEL_EVALUATOR`, `AI_PROVIDER_BASE_URL`, `AI_TIMEOUT_SECONDS`, and related names. The current backend settings use the existing AI Gateway path and must be verified or mapped safely before DeepSeek is enabled.

**Required action**: On rerun, verify the staging environment sets variables that the deployed backend actually reads, or add a safe compatibility mapping before enabling DeepSeek.

## 3. Real Provider Smoke Not Executed

**Status**: OPEN

**Severity**: BLOCKER

**Description**: The controlled real-provider smoke test was not executed because the key is unavailable.

**Required action**: After the staging secret is configured, rerun MVP-006 from the provider/model validation step.

## 4. OpenAI Explicitly Forbidden For MVP-006

**Status**: ACTIVE CONTROL

**Description**: Provider decision changed from OpenAI to DeepSeek. `OPENAI_API_KEY` must not be set for this gate, and OpenAI must not be enabled.

## Non-Issues

- No secret was printed or committed.
- OpenAI was not configured or enabled.
- DeepSeek was not enabled in staging or production because the staging secret is missing.
- Production acceptance and release allowance remain false.
