# Known Issues - MVP-006 Real LLM Provider Staging Gate

## Selected Provider

DeepSeek

## 1. DeepSeek Variables Present But Not Applied By Runtime

**Status**: RESOLVED

**Severity**: WAS BLOCKER

**Description**: Railway staging backend has the required DeepSeek variable names present. The backend AI Gateway compatibility mapping now applies those values at runtime, and the controlled smoke response reported `ai_model_used=deepseek-v4-flash`.

**Resolution**: Staging backend redeployed and real DeepSeek smoke passed.

## 2. Required MVP-006 Variable Names Need Mapping Verification

**Status**: RESOLVED

**Severity**: WAS BLOCKER BEFORE REAL SMOKE

**Description**: The MVP-006 task specifies provider-neutral names such as `AI_PROVIDER`, `AI_MODEL_EVALUATOR`, `AI_PROVIDER_BASE_URL`, `AI_TIMEOUT_SECONDS`, and related names. These are now mapped into the existing AI Gateway path.

**Resolution**: Sanitized provider validation confirmed provider `deepseek`, model `deepseek-v4-flash`, and base URL `https://api.deepseek.com`.

## 3. Real DeepSeek Smoke Failed Provider Assertion

**Status**: RESOLVED

**Severity**: WAS BLOCKER

**Description**: The controlled post-fix smoke proved DeepSeek usage because the returned model was `deepseek-v4-flash`.

**Resolution**: Smoke returned `validation_status=validated`, `overall_score=88`, and progress updated to total_attempts 1.

## 4. OpenAI Explicitly Forbidden For MVP-006

**Status**: ACTIVE CONTROL

**Description**: Provider decision changed from OpenAI to DeepSeek. `OPENAI_API_KEY` must not be set for this gate, and OpenAI must not be enabled.

## Non-Issues

- No secret was printed or committed.
- OpenAI was not configured or enabled.
- DeepSeek key presence was verified by name only; the key value was not exposed.
- Production acceptance and release allowance remain false.
