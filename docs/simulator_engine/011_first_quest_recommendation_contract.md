# First Quest Recommendation Contract

## Overview

The first quest recommendation system guides newly verified learners to the most appropriate beginner quest for their chosen trainer.

## Recommendation Logic

### QA Engineer Trainer
- **Recommended Quest:** `qa.bug_report` (Bug Report Structure)
- **Reason:** Covers fundamentals every QA engineer needs: bug report structure, severity vs priority classification, and professional report writing
- **Skills Trained:** Bug report structure, severity vs priority, professional writing, evidence analysis
- **Interaction Types:** multiple_choice, ordering, single_choice, evidence_select, free_text
- **Steps:** 5
- **Estimated Time:** 15 min

### Business Analyst Trainer
- **Recommended Quest:** `ba.payment_conflict` (Conflicting Requirements for a Payment Feature)
- **Reason:** Covers core BA skills: stakeholder identification, conflict resolution, requirements prioritization, and writing acceptance criteria
- **Skills Trained:** Stakeholder analysis, conflict resolution, acceptance criteria, requirements documentation
- **Interaction Types:** multiple_choice, matching, ordering, single_choice, free_text, dialogue
- **Steps:** 6
- **Estimated Time:** 20 min

## API Contract (Frontend-Only)

The recommendation is determined entirely on the frontend:
- Trainer slug or `trainer_product_id` is checked for QA/BA identifier
- If QA → `qa.bug_report` is recommended
- If BA → `ba.payment_conflict` is recommended

## UI Requirements

1. Recommended quest must be visually distinct (elevated card, gradient background, star icon)
2. Must include explanation of why this quest is useful
3. Primary CTA must start the recommended quest
4. Secondary CTA must allow browsing all quests
5. Estimated time, step count, and skills must be visible

## States

| State | Behavior |
|-------|----------|
| Loading | Skeleton or spinner |
| Unauthenticated | Redirect to login |
| Not enrolled | Show enrollment prompt |
| Enrolled, no quests | Show empty state |
| Enrolled, quests exist | Show recommended + catalog |
| Quest in progress | Show continue button |
| Quest completed | Show next action screen |
