# Known Issues - MVP-006 Real LLM Provider Staging Gate

## Selected Provider

DeepSeek

## 1. DeepSeek Variables Present But Not Applied By Runtime

**Status**: OPEN

**Severity**: BLOCKER

**Description**: Railway staging backend has the required DeepSeek variable names present, but the controlled smoke response reported `ai_model_used=gpt-4o-mini` instead of `deepseek-v4-flash`.

**Required action**: Add or verify safe backend compatibility mapping from `AI_PROVIDER`, `AI_MODEL_EVALUATOR`, `AI_PROVIDER_BASE_URL`, `DEEPSEEK_API_KEY`, and related MVP-006 variables into the AI Gateway runtime settings. Then redeploy staging and rerun the DeepSeek smoke.

## 2. Required MVP-006 Variable Names Need Mapping Verification

**Status**: OPEN

**Severity**: BLOCKER BEFORE REAL SMOKE

**Description**: The MVP-006 task specifies provider-neutral names such as `AI_PROVIDER`, `AI_MODEL_EVALUATOR`, `AI_PROVIDER_BASE_URL`, `AI_TIMEOUT_SECONDS`, and related names. The current backend settings use the existing AI Gateway path and the smoke shows these values are not driving the deployed evaluator yet.

**Required action**: Implement or configure a safe compatibility mapping before accepting DeepSeek.

## 3. Real DeepSeek Smoke Failed Provider Assertion

**Status**: OPEN

**Severity**: BLOCKER

**Description**: The controlled smoke executed and passed structurally, but did not prove DeepSeek usage because the returned model was `gpt-4o-mini`.

**Required action**: Fix mapping/redeploy, then rerun MVP-006 provider validation and smoke.

## 4. OpenAI Explicitly Forbidden For MVP-006

**Status**: ACTIVE CONTROL

**Description**: Provider decision changed from OpenAI to DeepSeek. `OPENAI_API_KEY` must not be set for this gate, and OpenAI must not be enabled.

## Non-Issues

- No secret was printed or committed.
- OpenAI was not configured or enabled.
- DeepSeek key presence was verified by name only; the key value was not exposed.
- Production acceptance and release allowance remain false.
