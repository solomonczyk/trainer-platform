# TRAINER-PLATFORM-QUEST-UX-READABILITY-AND-IMMERSIVE-POLISH-010C

## Goal

Improve Quest Catalog and Quest Play readability and visual hierarchy without changing quest logic, backend scoring, provider calls, or content.

## Current Verified State

```json
{
  "layer_010": "IMPLEMENTED",
  "layer_010a": "IMPLEMENTED_WITH_KNOWN_CLIENT_ISSUE",
  "layer_010b": "IMPLEMENTED_AND_TECHNICALLY_ACCEPTED",
  "quest_play_browser_runtime": "PASSED",
  "undefined_message_error": "FIXED",
  "qa_browser_acceptance": "PASSED_FULL_COMPLETION",
  "ba_browser_acceptance": "PASSED_FULL_COMPLETION",
  "operator_experience_review": "REJECTED_UX_UNREADABLE",
  "production_accepted": false,
  "release_allowed": false
}
```

## Rejection Basis

Operator review of 010B found:
- Font sizes too small for comfortable reading (catalog cards, story text, options)
- Text contrast insufficient — disabled-looking options, low-contrast badges, muted progress labels
- Answer options not visually interactive — feel greyed out rather than clickable
- Quest cards lack visual hierarchy — don't read as primary selectable missions
- Quest Play container cramped — poor spacing, weak vertical rhythm
- Progress indicator is a bare thin bar — no readable step counter or mission context

## Scope

### Allowed

Modify any frontend component that affects Quest Catalog and Quest Play visual presentation:
- font sizes, weights, line heights
- color contrast, hover states, active states, focus rings
- card layout, padding, margins, borders, shadows
- option/button sizing, backgrounds, interactive indicators
- progress display (stepper vs bar, step count, labels)
- container width, spacing, vertical rhythm
- CSS classes, Tailwind utility classes
- ru-RU and en-US readability

### Forbidden

- Backend logic, scoring, evaluation, provider calls
- Quest content, step text, option text, translations
- Routing, navigation, page structure
- Quest engine, session management, state machine
- API contracts, request/response schemas
- New feature layers
- Production cutover or release
- Changing `production_accepted` or `release_allowed` to true

## Required Implementation

### 1. Quest Catalog Readability

| Requirement | Detail |
|---|---|
| Base font size | Increase readable size for quest cards — title, summary, metadata |
| Card layout | Cards should read as primary selectable missions — visual hierarchy with icon, title, summary, meta row, CTA button |
| Contrast | Improve contrast on card text, descriptions, badges, tags |
| Tags/badges | Interaction type badges should be readable, not washed out |
| Hover state | Cards should clearly respond to hover (lift, shadow, border) |
| Empty state | Empty catalog message must be centered and readable |

### 2. Quest Play Readability

| Requirement | Detail |
|---|---|
| Container width | Increase max-w for story text, interaction, debrief panels |
| Spacing/rhythm | Consistent vertical rhythm between story context, prompt, interaction, submit area |
| Narrative bars | Bars must have readable labels, min-height, contrast fill |
| Step header | Step count and progress must be clearly visible, not tiny gray text |
| Story context | Story block must be comfortably readable — not cramped or low-contrast |
| Prompt | Prompt text must visually lead the interaction — larger, bolder, clear hierarchy |

### 3. Answer Option Interactive Design

| Requirement | Detail |
|---|---|
| Single choice | Options must look clearly clickable — border, hover lift, selected state distinct |
| Multiple choice | Checkbox areas must be visible, text readable, selected state obvious |
| Evidence select | Cards must look interactive, not grayed out — clear selected/unselected contrast |
| Ordering | Item rows must have visible grab handles or move buttons, readable text |
| Matching | Dropdowns must be properly sized, text readable, mapping state visible |
| Decision | Decision cards should feel weighty — distinct styling from regular options |
| Dialogue | Character says box, option buttons, text area all must be readable |
| Free text | Textarea must have proper padding, font size, contrast, focus ring |
| Disabled state | Disabled options must not look like errors — subtle opacity only |

### 4. Progress Stepper / Mission Progress

| Requirement | Detail |
|---|---|
| Replace thin progress bar | Implement step-based visual progress (stepper or milestone display) |
| Step number | Current step / total steps must be prominently displayed |
| Step title | Each step's position in mission context should be visible |
| Narrative state | Narrative consequence bars should show immediately after submit |
| Completed steps | Visual indicator that a step was completed |

### 5. Outcome and Debrief

| Requirement | Detail |
|---|---|
| Outcome panel | Outcome title and summary must be readable, well-spaced |
| Narrative state | Final narrative display should match step-level quality |
| Debrief sections | Each debrief section (strengths, mistakes, skill profile) must have clear heading, readable text, proper spacing |
| Action buttons | Retry and back-to-catalog buttons must be clearly actionable |

### 6. Visual Regression Screenshots

Capture after deployment:

```
docs/simulator_engine/screenshots/010c-qa-quest-catalog.png
docs/simulator_engine/screenshots/010c-ba-quest-catalog.png
docs/simulator_engine/screenshots/010c-qa-quest-step1.png
docs/simulator_engine/screenshots/010c-qa-option-selected.png
docs/simulator_engine/screenshots/010c-ba-quest-step1.png
docs/simulator_engine/screenshots/010c-outcome-debrief.png
```

### 7. Browser Acceptance Tests

Minimum flows:
- Home → IT domain → QA trainer → Quest Catalog → verify readability
- Home → IT domain → BA trainer → Quest Catalog → verify readability
- Open QA quest → verify step 1 readability + option selection → submit → outcome
- Open BA quest → verify step 1 readability → submit → outcome
- Verify all interaction type renderers display properly

### 8. Fast-Path Test Policy

Same as 010B — run focused tests only during development:

- `npm run typecheck`
- `npx vitest run src/tests/normalize-error.test.ts src/tests/quest-play-rendering.test.tsx`
- `npm run build`
- `npx playwright test e2e/quest-play-010b.spec.ts` (reuse existing acceptance tests)

One full local frontend suite run before push.

### 9. Deployment

Same CI/deploy workflow as 010B. Target one implementation commit.

## Acceptance Criteria

```json
{
  "quest_catalog_readable": true,
  "quest_play_readable": true,
  "text_contrast_acceptable": true,
  "options_clearly_interactive": true,
  "progress_readable": true,
  "operator_visual_review": "ACCEPTED",
  "runtime_errors": 0,
  "production_accepted": false,
  "release_allowed": false
}
```

## Artifacts

```
docs/simulator_engine/010c_quest_ux_readability_and_immersive_polish.md  (this file)
docs/simulator_engine/010c_visual_regression_report.md
docs/simulator_engine/010c_acceptance_report.md
docs/simulator_engine/010c_known_issues.md
docs/proofs/proof_trainer_platform_quest_ux_readability_polish_010c.json
```

## Proof JSON Structure

```json
{
  "layer": "TRAINER-PLATFORM-QUEST-UX-READABILITY-AND-IMMERSIVE-POLISH-010C",
  "verdict": "TBD",
  "base_state": { "operator_experience_review": "REJECTED_UX_UNREADABLE" },
  "implementation": {
    "quest_catalog_readable": false,
    "quest_play_readable": false,
    "text_contrast_acceptable": false,
    "options_clearly_interactive": false,
    "progress_readable": false
  },
  "tests": { "focused_frontend_passed": 0, "browser_regression_passed": 0 },
  "github_actions": { "conclusion": "" },
  "operator_visual_review": "PENDING",
  "production_accepted": false,
  "release_allowed": false,
  "next_allowed_action": "TBD"
}
```

## Control Points

- `NEEDS OPERATOR ACTION` if screenshots cannot be captured or visual review credentials unavailable
- `NEEDS FIX` if any interaction type renders with unreadable text, low contrast, or non-interactive options
- `REJECTED` if backend logic, quest content, provider calls, or routing are changed without scope justification
