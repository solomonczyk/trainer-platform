# Mission Intro Specification

## Purpose

The mission intro screen sets the context for the learner before they start a quest. It transforms a plain "start quest" action into a guided learning experience.

## Required Sections

### 1. Quest Title and Summary
- Display quest title from localization
- Display quest summary from localization

### 2. Quick Info Bar
- Estimated time (minutes)
- Number of steps
- Number of interaction types
- Displayed as pills/badges in a centered row

### 3. Role Context
- The learner's role in the scenario
- Visual: primary-colored block with target icon

### 4. Mission Statement
- The mission/objective the learner must accomplish
- Visual: purple-colored block with award icon

### 5. Setting/Story Context
- The scenario setting and situation
- Visual: muted-colored block with map icon

### 6. Characters (if applicable)
- Character cards showing name and role
- Grid layout (1 column mobile, 2 columns desktop)

### 7. Skills Trained
- Badge list of skills this quest practices
- Description: "Skills you will practice in this quest"

### 8. How Feedback Works
- Explains the per-answer feedback system
- Description: After each answer, results with explanation and takeaway; final debrief available

### 9. Narrative State
- Initial status meters showing starting state

### 10. Start Button
- Clear "Start Mission" CTA
- ChevronRight icon

## States

| State | Behavior |
|-------|----------|
| Loading | Full-page spinner |
| Quest not found | Error state with retry/back |
| Data loaded | Full intro with all sections |
