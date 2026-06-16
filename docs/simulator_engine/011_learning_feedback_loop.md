# Learning Feedback Loop Specification

## Overview

After each quest step answer, the learner receives structured feedback before advancing. This turns each step into a learning moment rather than a test pass/fail.

## Feedback Panel Sections

### 1. Result Header
- Icon: CheckCircle (correct), AlertCircle (partial), XCircle (incorrect)
- Color: green (correct), amber (partial), red (incorrect)
- Text: "Correct!", "Partially correct", "Not quite right"
- Score display: `{score}/{max_score}`

### 2. Why Section (Explanation)
- Title: "Why?"
- Explanation of why the answer was correct/incorrect
- For correct answers: reinforcement of what was done right
- For incorrect answers: what was missed

### 3. Correct Approach
- Title: "Correct approach"
- Shown only when answer is wrong or partial
- Describes the professional approach

### 4. AI Feedback (for free-text/dialogue steps)
- Strengths list
- Weak points list
- Only shown when AI evaluation data is available

### 5. Practical Takeaway
- Title: "Takeaway"
- A concise, memorable lesson the learner can apply

### 6. Continue Button
- Manual continue — no auto-advance
- Button text: "Continue"
- ArrowRight icon

## States

| State | Display |
|-------|---------|
| Correct (score=100%) | Green header, reinforcement, takeaway, continue |
| Partial (0%<score<100%) | Amber header, why explanation, correct approach, takeaway, continue |
| Incorrect (score=0%) | Red header, why explanation (what was missed), correct approach, takeaway, continue |
| AI evaluated | Same as above + AI strengths/weak points |
| No feedback data | Result header only + continue button |
