# Debrief and Mistakes Review Specification

## Final Debrief

After completing the quest, the learner sees an educational debrief with the following sections:

### Required Sections

1. **Outcome Summary** — The quest outcome title and description
2. **Final Score** — Average score across all steps
3. **Strengths** — List of what the learner did well
4. **Mistakes / Improvement Areas** — Areas where the learner can improve
5. **Missed Risks** — Risks the learner failed to identify
6. **Professional Sample** — A professionally written example of the expected artifact
7. **Skills Trained** — Skills practiced in this quest
8. **Skill Profile** — Detailed skill results from backend evaluation
9. **Narrative State** — Final status meters

### Action Buttons
- View Mistakes Review — opens detailed step-by-step review
- Try Again — restarts the quest
- Complete Review — advances to next action screen

## Mistakes Review

A separate review mode accessible from the debrief screen.

### Required Capabilities

1. **Step-by-step navigation** — Previous/Next buttons
2. **Each step shows:**
   - Step number and type badge
   - Story context (if any)
   - Step prompt
   - User's answer (from feedback_data)
   - Score and result badge (correct/partial/incorrect)
   - Explanation (what was missed)
   - Correct answer / correct approach
   - Practical takeaway
3. **Back to debrief** button

### States

| State | Display |
|-------|---------|
| No step results | "No mistakes to review — great job!" message |
| Step results available | Full navigation with step cards |
| Edge (first step) | Previous button disabled |
| Edge (last step) | Next button disabled |

## Next Action Screen

After debrief review, the learner sees a choice of next actions:

1. **Repeat This Quest** — Restart the current quest
2. **Start Next Quest** — Navigate to the next recommended quest
3. **Return to Catalog** — Browse all quests
4. **Continue {Trainer} Path** — Back to trainer detail page
