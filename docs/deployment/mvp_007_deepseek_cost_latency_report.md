# MVP-007 DeepSeek Cost and Latency Report

## Overview

This report documents the cost and latency characteristics of real DeepSeek evaluations on the staging environment during the MVP-007 acceptance review.

## Provider

| Field | Value |
|---|---|
| Provider | DeepSeek |
| Model | deepseek-v4-flash |
| Deployment | Railway staging |
| API Endpoint | api.deepseek.com (via backend AI gateway) |

## Cost Analysis

### Per-Request Cost

All evaluations returned `ai_cost_usd: 0.001` (flat $0.001 per evaluation).

| Test Case | Score | Cost (USD) |
|-----------|-------|-----------|
| CASE-01 (strong, retry) | 90 | $0.001 |
| CASE-02 (weak, investigation) | 60 | $0.001 |
| CASE-03 (partial, investigation) | 52 | $0.001 |
| CASE-04 (very short) | 50 | $0.001 |
| CASE-06 (irrelevant) | 0 | $0.001 |
| CASE-07 (wrong language) | 75 | $0.001 |
| CASE-08 (privacy risk) | 60 | $0.001 |
| CASE-09 (repeated attempt) | 94 | $0.001 |
| CASE-10 (malformed) | 0 | $0.001 |
| CASE-11 (timeout path) | 0 | $0.001 |
| CASE-12 (rate-limit test) | 65 | $0.001 |

### Aggregate Cost

| Metric | Value |
|---|---|
| Total evaluation calls | ~18 |
| Total test cost (estimated) | ~$0.018 |
| Max cost per request | $0.001 |
| Cost limit configured | $0.05 |
| All under cost limit | ✅ Yes |

## Latency Analysis

### Per-Request Latency

| Test Case | Latency (ms) | Score |
|-----------|-------------|-------|
| CASE-06 (irrelevant) | 4,703 | 0 |
| CASE-11 (timeout path) | 4,828 | 0 |
| CASE-12 (rate-limit retest) | 5,875 | 65 |
| CASE-06 (initial) | 6,030 | 0 |
| CASE-01 (502) | 6,827 | — |
| CASE-12 (rate-limit initial) | 6,812 | 65 |
| CASE-07 (wrong language) | 8,218 | 75 |
| CASE-04 (very short) | 8,562 | 50 |
| CASE-01 (strong) | 8,452 | 95 |
| CASE-03 (partial) | 8,812 | 0 |
| CASE-02 (weak) | 9,327 | 0 |
| CASE-10 (malformed) | 10,203 | 0 |
| CASE-02 (investigation) | 10,577 | 60 |
| CASE-01 (retry) | 12,781 | 90 |
| CASE-08 (privacy risk) | 15,125 | 60 |
| CASE-09 (repeated strong) | 16,844 | 94 |
| CASE-03 (investigation) | 17,484 | 52 |

### Latency Summary

| Metric | Value |
|---|---|
| Minimum | 4,703 ms |
| Maximum | 17,484 ms |
| Median | ~8,800 ms |
| Average | ~9,800 ms |
| Timeout configured | 30,000 ms |
| Requests under timeout | ✅ 100% |

### Observations

1. **No clear correlation between answer length and latency**: Short answers (CASE-06: 6030ms) and long answers (CASE-03: 8812ms) both fall in similar latency ranges.
2. **Higher scores tend to correlate with higher latency**: Strong answers scoring 90+ take 12-17s while low-scoring answers take 4-8s. This likely reflects more thorough evaluation processing by the LLM.
3. **All requests well under 30s timeout**: The configured 30s timeout provides adequate headroom.
4. **Latency variance is high**: 4.7s to 17.5s range suggests variable provider load.

## Cost Projection (for production planning)

| Scenario | Evaluations/month | Est. monthly cost |
|----------|------------------|-------------------|
| Light usage | 1,000 | ~$1.00 |
| Moderate usage | 10,000 | ~$10.00 |
| Heavy usage | 100,000 | ~$100.00 |

## Conclusion

The DeepSeek evaluation service on staging is cost-effective ($0.001/evaluation) with acceptable latency (avg ~10s, max ~17.5s). All requests respect the configured 30s timeout and $0.05 per-request cost cap.
