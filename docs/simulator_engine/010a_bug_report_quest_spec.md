# 010a — Bug Report Quest Specification

## Overview

The legacy scenario `qa_bug_report_structure_v1` has been converted from a single-textarea interview question into a multi-step mini-quest with five interaction types and an educational debrief.

## Quest Metadata

| Field | Value |
|-------|-------|
| quest_id | `qa_bug_report_structure_v1` |
| trainer_slug | `qa_engineer_interview_trainer` |
| estimated_minutes | 15 |
| interaction_types_count | 5 |
| free_text_used_only_for_artifact | True |

## Steps

### Step 1: Multiple Choice — Required Fields
- **Type**: `multiple_choice`
- **Task**: Select all required fields of a professional bug report
- **Options**: 11 choices (8 correct, 3 distractors)
- **Evaluation**: Deterministic

### Step 2: Ordering — Bug Report Structure
- **Type**: `ordering`
- **Task**: Arrange bug report fields in logical sequence
- **Items**: 7 (Title → Environment → Preconditions → Steps → Actual → Expected → Attachments)
- **Evaluation**: Deterministic

### Step 3: Single Choice — Severity vs Priority
- **Type**: `single_choice`
- **Task**: Differentiate severity from priority
- **Options**: 3 (1 correct, 2 distractors)
- **Evaluation**: Deterministic

### Step 4: Evidence Select — Find Defects
- **Type**: `evidence_select`
- **Task**: Identify concrete defects in a poorly written bug report
- **Items**: 7 (5 defects, 2 non-defects)
- **Evaluation**: Deterministic

### Step 5: Free Text — Professional Artifact
- **Type**: `free_text`
- **Task**: Write a concise bug report using provided evidence
- **Min/Max**: 100/3000 characters
- **Evaluation**: AI rubric (4 criteria)
- **This is the only free-text step**

### Step 6: Debrief
- **Sections**: Strengths, mistakes, missed risks, correct structure, professional sample, lessons learned, skill profile

## Outcomes

| ID | Min Decision Quality | Min Evidence Quality |
|----|---------------------|---------------------|
| br_excellent | 70 | 70 |
| br_good (default) | 40 | 40 |
| br_needs_practice | 0 | 0 |

## Deterministic Scoring

Steps 1–4 are evaluated deterministically without AI provider calls. The free-text step 5 uses AI rubric evaluation.

## Debrief Content

The debrief provides:
- Correct bug report structure reference
- Professional sample bug report
- Lessons learned based on learner's choices
- Skill profile across 5 dimensions
