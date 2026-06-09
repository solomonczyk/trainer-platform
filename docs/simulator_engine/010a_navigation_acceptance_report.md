# 010a — Navigation Acceptance Report

## Primary Flow Changes

### QA Trainer
- **Before**: Primary CTA → `/trainers/qa_engineer_interview_trainer/scenarios` (legacy catalog)
- **After**: Primary CTA → `/trainers/qa_engineer_interview_trainer/quests` (quest catalog)

### BA Trainer
- **Before**: Primary CTA → `/trainers/business_analyst_interview_trainer/scenarios` (legacy catalog)
- **After**: Primary CTA → `/trainers/business_analyst_interview_trainer/quests` (quest catalog)

## Normal User Flow

```
Home → IT Domain → [QA|BA] Trainer → Quest Catalog → Quest → Outcome → Debrief
```

The normal user never encounters the legacy textarea-only scenario UI during this flow.

## Legacy Route Behavior

| Route | Before | After |
|-------|--------|-------|
| `/scenarios/qa_bug_report_structure_v1` | Textarea-only UI | Redirects to quest `qa_bug_report_structure_v1` |
| `/scenarios/qa_test_case_vs_checklist_v1` | Textarea-only UI | Redirects to quest `qa_payment_defect_release` |
| `/scenarios/qa_login_form_testing_v1` | Textarea-only UI | Redirects to quest `qa_payment_defect_release` |
| `/scenarios/qa_regression_vs_retest_v1` | Textarea-only UI | Loads legacy UI (hidden from catalog) |
| `/scenarios/qa_self_presentation_v1` | Textarea-only UI | Loads legacy UI (hidden from catalog) |

## Route Compatibility

- All old routes preserve authentication and locale
- Historical attempts and progress are preserved
- New attempts use quest engine
- Direct URL access to mapped scenarios redirects to correct quest
