# 010a — Known Issues

## Current

1. **Hidden scenarios still accessible via direct URL**: Legacy scenarios marked as HIDE_TEMPORARILY can still be loaded via direct `/scenarios/{id}` URL. This is intentional — they remain in the repository for internal access and historical attempt compatibility. They are not visible in the learner catalog.

2. **BA Phase 2 section remains**: The BA Phase 2 section on the trainer page still links to the legacy Phase 2 scenario list. This is because BA Phase 2 scenarios are not fully converted to quests yet. The primary CTA now leads to the quest catalog, and the Phase 2 section is secondary.

3. **No mechanism to prevent duplicate scenario usage**: Both old and new flows coexist for scenarios marked REDIRECTED. A user with a direct bookmark to a legacy scenario will be redirected, but the underlying DB scenario record is untouched.

4. **Limited quest inventory**: Only 3 quests exist (2 from Layer 010 + 1 mini-quest from 010a). The remaining 6 hidden scenarios will require quest conversion in future layers.

## Resolved

None yet — 010a is in initial implementation.
