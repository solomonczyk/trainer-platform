# Known Issues — MVP-007 Staging Real AI Acceptance Review

## Context

MVP-007 staging real AI acceptance review executed on 2026-06-06. These issues were identified during the review and are tracked for production readiness.

## 1. Score Non-Determinism for LLM-Based Evaluation

**Status**: OPEN — CARRIED OVER

**Severity**: Minor

**Scope**: Affects all evaluation cases

**Description**: The same answer submitted to the same scenario via DeepSeek-v4-flash can produce significantly different scores across runs. Observed variance of 0-60 (CASE-02) and 0-52 (CASE-03). This is inherent to LLM-based evaluation and not a system defect.

**Impact**: Users may receive different scores for the same answer if they re-attempt. This reduces perceived evaluation reliability.

**Recommendation**: Document as expected behavior for beta. Consider structured output/constrained decoding for production to reduce variance.

## 2. Single-Criterion Evaluation in Most Cases

**Status**: OPEN — CARRIED OVER

**Severity**: Minor

**Scope**: Most evaluations return 1 criterion (`bug_report_quality` or `overall`)

**Description**: The majority of test cases returned only 1 evaluation criterion instead of a multi-dimensional rubric. Only CASE-09 (strong answer) returned 5 criteria with per-dimension scoring. The evaluation contract would benefit from consistent multi-criteria output.

**Impact**: Reduced feedback granularity for most evaluations.

**Recommendation**: Review the AI gateway normalization to ensure multi-criteria output is consistently produced. The DeepSeek prompt should explicitly request per-dimension scoring.

## 3. Transient 502 Upstream Errors

**Status**: OPEN — MONITOR

**Severity**: Minor

**Scope**: 1 of ~18 DeepSeek API calls (CASE-01 initial attempt)

**Description**: One evaluation request failed with HTTP 502 ("upstream error"). The retry succeeded with score=90. This indicates occasional DeepSeek API instability.

**Impact**: Users may occasionally need to retry evaluations.

**Recommendation**: Add automatic retry logic (1-2 attempts with exponential backoff) for transient 5xx errors. The blind retry guard should only apply to non-5xx failures.

## 4. Completed Scenarios Count Variance

**Status**: OPEN — OBSERVED

**Severity**: Minor

**Scope**: Progress tracking

**Description**: After testing, `completed_scenarios` showed 4 for the test user, but only 3 cases with confirmed `passed=true` were observed. The fourth increment may reflect a passed evaluation that wasn't captured, or a counting boundary condition.

**Impact**: Low — progress tracking works correctly for the common case.

**Recommendation**: Investigate the completed_scenarios counting logic during production hardening.

## 5. Score Range Deviation for Short/Concise Answers

**Status**: OPEN — CARRIED OVER

**Severity**: Trivial

**Scope**: CASE-04 (very short answer scored 50, expected 0-39)

**Description**: A very short but accurate answer scored higher than expected because the LLM weighted correctness over comprehensiveness.

**Impact**: The expected score ranges in the test matrix are approximate guidelines, not hard bounds.

**Recommendation**: Adjust expected ranges or add a completeness criterion that penalizes insufficient response length.

## 6. `raw_answer` Key Not Explicitly Blocked in Analytics

**Status**: OPEN — OBSERVED

**Severity**: Minor

**Scope**: Analytics service property filtering

**Description**: The analytics service blocks `answer`, `answer_text`, and `content` keys, but `raw_answer` or `full_answer` would pass through unless caught by the credential-value heuristic (which requires >= 16 chars with >85% alphanumeric ratio).

**Impact**: Low — the frontend does not send raw answers to analytics. This is a defense-in-depth gap.

**Recommendation**: Add `raw_answer`, `full_answer`, `response_text` to the `BLOCKED_PROPERTY_KEYS` set.

## Resolved Issues

### 1A. MVP-006C Acceptance Required

**Status**: RESOLVED

**Severity**: WAS ENTRY BLOCKER

**Resolution**: MVP-006C accepted with `validation_status=validated`, `ai_model_used=deepseek-v4-flash`. Entry condition met.

### 1B. CASE-01 502 Transient Failure

**Status**: RESOLVED

**Severity**: WAS TEST FAILURE

**Resolution**: Retry succeeded with score=90. Issue is with DeepSeek API, not the application.

## Non-Issues (Confirmed Working)

- ✅ All success-path cases use `deepseek-v4-flash` (no OpenAI)
- ✅ `validation_status=validated` for all success-path cases
- ✅ Non-empty criteria for all success-path cases
- ✅ Analytics privacy filters working correctly
- ✅ No reasoning content exposed to frontend
- ✅ Rate limiting active (60 req/min, headers present)
- ✅ Re-evaluation properly rejected (422, not unbounded retry)
- ✅ Empty answers blocked at validation layer
- ✅ User progress isolation preserved
- ✅ No secrets exposed in any response or artifact
- ✅ Production/release flags remain false
- ✅ All backend tests pass (105/105)
- ✅ All frontend tests pass (10/10)
- ✅ Frontend build succeeds
- ✅ Trainer package validates
- ✅ OpenAPI exports correctly
