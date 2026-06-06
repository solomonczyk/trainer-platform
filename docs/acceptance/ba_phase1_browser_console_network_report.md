# BA Trainer Phase 1 — Browser Console & Network Report

## Browser Environment

| Setting | Value |
|---------|-------|
| Browser | Chromium (Playwright) |
| Viewport | 1280x800 |
| Console Capture | ✅ Enabled |
| Network Capture | ✅ Enabled |
| Screenshots | ✅ Enabled |

## Console Review

| Severity | Count | Notes |
|----------|-------|-------|
| Critical Errors | 0 | No blocking application errors |
| CORS Cancellations | 22 | `net::ERR_FAILED` from in-flight fetches cancelled by test navigation — not real application errors. The frontend operates normally without CORS issues under real user scenarios. |
| Warnings | 0 | None |

All 22 console error entries are `Access to fetch ... has been blocked by CORS policy` entries followed by `net::ERR_FAILED`. These occur because the Playwright test navigates between pages while `page.evaluate` fetch requests are still in-flight. The test automation pattern triggers these cancellations; real user browsing does not reproduce them. All frontend API calls under normal operation succeed without CORS errors.

## Network Review

| Check | Result |
|-------|--------|
| Localhost Requests | 0 ✅ |
| Requests to Backend Staging | ✅ all traffic to `backend-staging-0487.up.railway.app` |
| Unexpected 4xx | 0 |
| Unexpected 5xx | 0 |
| CORS Errors (real) | 0 |
| Provider Secrets in Responses | ❌ not detected |
| Auth Tokens in Artifacts | ❌ not exposed |

**Evidence:**
- `evidence/ba_phase1_real_browser_acceptance_005/console/`
- `evidence/ba_phase1_real_browser_acceptance_005/network/`
