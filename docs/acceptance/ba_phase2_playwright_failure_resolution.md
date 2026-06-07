# BA Phase 2 Playwright Failure Resolution

## Failed Test

| Field | Value |
|-------|-------|
| **Test name** | `BA Phase 2 Browser Acceptance > User can register and login` |
| **File** | `frontend/e2e/ba-phase2-acceptance.spec.ts` |
| **Failure type** | `test_defect` |
| **Root cause** | The test used `page.locator("h1, h2").first()` to find a heading on the registration page, but the page's `CardTitle` component renders as an `<h3>`, not an `<h1>` or `<h2>`. The locator timed out waiting for a non-existent element (2-minute timeout). |

## Root Cause Analysis

The registration page (`frontend/src/app/register/page.tsx`) uses the `CardTitle` UI component (`frontend/src/components/ui/Card.tsx`) for its page heading:

```tsx
<CardTitle className="text-2xl font-bold">{t("auth.registerTitle")}</CardTitle>
```

The `CardTitle` component renders as:

```tsx
function CardTitle({ children, className }) {
  return <h3 className={...}>{children}</h3>;
}
```

The Playwright test assumed a heading level of `h1`/`h2`, which was true for other pages but not the registration page.

Additional contributing issues in the `registerUser()` helper:
- `input[name="displayName"]` selector failed because the display name input uses `id="displayName"`, not `name`
- `waitForTimeout(2000)` after submit was unreliable — navigation could take longer
- No stable wait for form elements to render before filling

## Fix Applied

The `registerUser()` and `loginUser()` helper functions were updated in commit `77535d6`:

1. **Heading selector**: Replaced `h1, h2` with `h3, input[type='email'], form` to match actual page structure
2. **Field selectors**: Changed from type-based selectors to stable `#id` selectors (`#email`, `#password`, `#confirmPassword`, `#displayName`)
3. **Submit wait**: Replaced `waitForTimeout(2000)` with `waitForURL()` that waits for navigation away from `/register` or `/login`
4. **Form ready check**: Added `waitFor({ state: "visible" })` before filling fields to ensure client-side rendered form is ready

## Verification

```
npx playwright test --reporter=list

Running 9 tests using 1 worker

  ok 1 — Phase 2 scenarios visible on BA trainer page (3.9s)
  ok 2 — Phase 2 scenario list shows scenarios (2.9s)
  ok 3 — Phase 2 scenario detail loads (4.2s)
  ok 4 — User can register and login (4.0s)
  ok 5 — Phase 1 modules still accessible (regression) (3.5s)
  ok 6 — No raw i18n keys visible to user (3.6s)
  ok 7 — No localhost requests or unexpected 5xx (6.5s)
  ok 8 — No critical console errors (5.4s)
  ok 9 — QA Trainer page accessible (3.0s)

9 passed (38.5s)
```

## Product Code Change

No product code was changed. The fix is entirely in the test code (`frontend/e2e/ba-phase2-acceptance.spec.ts`).

## Test Code Changed

Yes — `frontend/e2e/ba-phase2-acceptance.spec.ts`

## Resolution Summary

| Check | Value |
|-------|-------|
| `failed_test_name` | `BA Phase 2 Browser Acceptance > User can register and login` |
| `failure_type` | `test_defect` — test selector didn't match DOM structure |
| `root_cause` | `CardTitle` renders as `<h3>`, test expected `<h1>/<h2>` |
| `fix` | Updated selectors to `#id` based, added `waitForURL()` for navigation |
| `product_code_changed` | `false` |
| `test_code_changed` | `true` |
| `playwright_total` | `9` |
| `playwright_passed` | `9` |
| `playwright_failed` | `0` |
| `playwright_skipped` | `0` |
