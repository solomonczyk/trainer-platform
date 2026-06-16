# Browser Acceptance Test Specification

## Prerequisites

- Clean browser session (incognito/private mode)
- Server running at staging URL
- Registered and verified user account
- Both QA and BA trainers available

## QA Flow

1. Navigate to staging URL
2. Log in with verified user
3. Verify redirect to domains page
4. Select IT domain
5. Verify QA Engineer Interview Trainer appears
6. Select QA trainer
7. Verify recommended first quest is visible (Bug Report Structure)
8. Primary CTA opens the recommended quest
9. Verify mission intro shows all required sections
10. Click "Start Mission"
11. Complete all quest steps:
    - Step 1: Multiple choice — select bug report fields
    - Step 2: Ordering — arrange bug report fields
    - Step 3: Single choice — severity vs priority
    - Step 4: Evidence select — identify bug report issues
    - Step 5: Free text — write bug report
12. After each step, verify feedback panel appears with:
    - Score and result
    - Explanation
    - Correct approach (if wrong)
    - Takeaway
    - Continue button (manual)
13. After final step, verify outcome screen
14. Click "View Educational Debrief"
15. Verify debrief sections:
    - Outcome summary
    - Final score
    - Strengths
    - Mistakes
    - Professional sample
    - Skills summary
    - Action buttons
16. Click "View Mistakes Review"
17. Review each step
18. Navigate between steps
19. Return to debrief
20. Click "Complete Review"
21. Verify next action screen with options

### Refresh Persistence Test
1. Complete quest, reach outcome
2. Refresh page
3. Verify outcome/debrief state is restored

## BA Smoke

1. Log in, navigate to BA trainer
2. Verify recommended quest is visible
3. Verify mission intro is visible
4. Complete at least first interaction
5. Verify feedback is visible
6. Verify no runtime crash

## Runtime Checks

During both flows, monitor:
- No white screen
- No infinite loader
- No React error #31
- No "undefined.message" errors
- No unexpected HTTP 5xx
- No raw i18n keys visible
