# BA Phase 1 — Real Browser Acceptance Known Issues

## Open Items

### 1. Spurious CORS Errors During Automated Test Navigation

**Severity:** Cosmetic

The Playwright acceptance test generates 22 non-blocking console errors when
`page.evaluate` fetch requests are in-flight during page navigation. These are
`net::ERR_FAILED` / CORS policy errors caused by in-flight requests being
cancelled by the browser when the test navigates to a new page.

**Root cause:** Test automation pattern, not a real application defect. The
frontend operates without CORS issues under real user scenarios.

**Recommendation:** Accept as expected behavior for automated browser tests.
No code changes required.

### 2. Module Activity Titles Not Translated

**Severity:** Cosmetic

Module pages display `ba_hr_q1_title` style translation keys instead of the
Russian-language question text. This is because the frontend i18n system
does not have translations for all activity title keys.

**Root cause:** Missing locale entries for activity title keys in the
`ru-RU.json` locale file.

**Recommendation:** Complete i18n for activity titles in Phase 2 or a
dedicated i18n update task.
