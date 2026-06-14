# 010D Known Issues

## Design System Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| Some pages still use hardcoded colors (review page, profile page, dashboard) | Low | Out of scope for this layer — focused on quest experience |
| Font loading flash (FOUT) possible with Google Fonts | Low | Inter loads async; preconnect could help but not critical |
| Dark mode not automatically enabled | Low | Infrastructure ready, waiting for toggle mechanism |
| Some inline SVGs remain instead of lucide icons | Low | Ordering/matching renderers use inline SVGs for move/clear arrows |

## Component Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| LocaleSwitcher component still not used in Header/Footer | Medium | Duplicated logic remains; Header/Footer inline their own locale switchers |
| LoadingSpinner component not adopted in all pages | Medium | Some pages still inline spinner SVGs (scenario, review, progress pages) |
| Badge component not adopted in all locations | Low | Some badge patterns remain hand-rolled (dashboard readiness, scenario difficulty) |

## Functional Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| No screenshots from VPS staging yet | High | Requires deployment and manual browser capture |
| VPS deployment not yet performed | High | Must deploy before browser acceptance |

## Out of Scope
- Review page UI (not part of quest experience)
- Dashboard/progress pages (not part of quest experience)
- Profile/admin pages (not part of quest experience)
- Backend code changes (forbidden)
- Production cutover (forbidden)
