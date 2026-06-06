# Phase 1 Staging Smoke Report

## Staging Environment

| Service | Status |
|---|---|
| Backend | Deployed to Railway staging |
| Frontend | Deployed to Railway staging |
| PostgreSQL | Managed by Railway |

## Staging Checklist

| Check | Status | Notes |
|---|---|---|
| Catalog visible | ✅ | BA Trainer appears in IT domain |
| Trainer overview opens | ✅ | Modules displayed correctly |
| 10 modules shown | ✅ | All Phase 1 modules present |
| Single choice renders | ✅ | Radio buttons with options |
| Multiple choice renders | ✅ | Checkboxes for multi-select |
| Numeric input renders | ✅ | Number input field |
| Fill blanks renders | ✅ | Template with inline inputs |
| Matching renders | ✅ | Left/right dropdown pairs |
| Correct answer validated | ✅ | Server returns correct/score=100 |
| Incorrect answer validated | ✅ | Server returns incorrect/score=0 |
| Explanation after submit | ✅ | Shown in blue info box |
| Module progress updates | ✅ | Progress recalculated |
| Overall progress updates | ✅ | TrainerProgress updated |
| Refresh retains progress | ✅ | DB-backed persistence |
| Logout/login retains | ✅ | User-scoped data |
| User isolation | ✅ | User A cannot see User B's attempts |
| QA Trainer works | ✅ | Full scenario lifecycle intact |
| No localhost API calls | ✅ | Staging API URL used |
| No console errors | ✅ | Browser console clean |
