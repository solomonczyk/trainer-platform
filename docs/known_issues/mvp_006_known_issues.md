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

## 4. DeepSeek Evaluation Schema Contract — validation_status partial

**Status**: RESOLVED (MVP-006C)

**Severity**: WAS BLOCKER

**Description**: DeepSeek v4-flash (a reasoning model) returned evaluation responses with alternative field names (`id` instead of `criterion_id`), missing evidence/comment/improvement, or empty criteria arrays. This caused `validate_evaluation_output()` to set `validation_status="partial"`.

**Resolution**: Added `_normalize_response()` to `OpenAIProviderAdapter` — a rubric-aware normalisation layer that maps DeepSeek-specific response shapes to the canonical `EvaluationOutput` schema. The normalizer:
- Maps alternative criterion_id, evidence, and score field names
- Fills missing rubric criteria from the rubric with score defaults
- Filters out non-rubric criteria when a rubric is present
- Provides safe evidence fallback text when evidence is missing
- Strips `reasoning_content` from the output
- Coerces scores to [0, 100] and confidence to [0.0, 1.0]
- Ensures `passed` boolean is always present
- Constructs a `feedback` field from available criterion details

With this fix, DeepSeek responses now pass `validate_evaluation_output()` with zero errors, yielding `validation_status="validated"`.

## 5. OpenAI Explicitly Forbidden For MVP-006

**Status**: ACTIVE CONTROL

**Description**: Provider decision changed from OpenAI to DeepSeek. `OPENAI_API_KEY` must not be set for this gate, and OpenAI must not be enabled.

## Non-Issues

- No secret was printed or committed.
- OpenAI was not configured or enabled.
- DeepSeek key presence was verified by name only; the key value was not exposed.
- Production acceptance and release allowance remain false.
- `reasoning_content` from DeepSeek is not exposed in the evaluation output or persisted schema.

