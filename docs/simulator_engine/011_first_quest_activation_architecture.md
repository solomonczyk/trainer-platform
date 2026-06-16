# Layer 011 — First Quest Activation and Learning Loop

## Overview

This layer implements the first meaningful post-verification learner experience. After email verification is accepted, the user is guided into a recommended first quest with a complete learning loop: mission intro → varied quest steps → per-answer feedback → final debrief → mistakes review → next action.

## Flow

```
verified user
→ /domains
→ /domains/[slug]
→ /trainers/[slug] (enroll)
→ recommended first quest block on trainer page
→ /trainers/[slug]/quests/[questId] (mission intro)
→ quest play (varied interaction types)
→ per-answer learning feedback
→ quest completion → outcome
→ educational debrief
→ mistakes review
→ next recommended action
```

## Architecture

### Frontend Components Modified

1. `/trainers/[slug]/page.tsx` — Trainer detail page
   - Added recommended first quest section (shown after enrollment)
   - Primary CTA starts the recommended quest
   - Secondary CTA opens full catalog
   - Shows estimated time, steps count, skills trained, reason explanation

2. `/trainers/[slug]/quests/page.tsx` — Quest catalog page
   - Added recommended quest banner at top
   - Listed remaining quests below
   - Shows why this quest is recommended

3. `/trainers/[slug]/quests/[questId]/page.tsx` — Quest play page
   - Improved mission intro with skills, estimated time, feedback info
   - Added mistakes review mode
   - Improved final debrief with professional sample, skills summary
   - Added next action screen after debrief

### Frontend Components Referenced

- `LearningFeedbackPanel` — per-answer learning feedback
- `StatusMeter` — narrative state visualization
- Various step renderers (SingleChoiceRenderer, MultipleChoiceRenderer, etc.)

### Localization

All new UI strings added to both en-US and ru-RU locale files under these sections:
- `recommended_quest` — first quest recommendation
- `mission_intro` — mission intro enhancements
- `feedback_details` — feedback panel labels
- `mistakes_review` — mistakes review mode
- `debrief_enhanced` — debrief additions
- `next_action` — post-completion actions

## Key Design Decisions

### No Backend Changes Required
The frontend can reliably determine:
- Recommended first quest based on trainer slug (QA → bug_report quest, BA → payment_conflict quest)
- Learner progress state (from localStorage + backend quest progress API)
- Next suggested action (based on which quest was just completed)

### Professional Sample Content
Educational correct answers are shown because this is a simulator, not a certified exam. This follows the "no answer keys exposed" rule — professional examples are teaching aids, not hidden prompts.

### Mistakes Review
A separate review mode accessible from the debrief screen. Uses stored step_results from the session to show each step's result, explanation, and correct approach. Navigation between steps is manual (Previous/Next buttons).
