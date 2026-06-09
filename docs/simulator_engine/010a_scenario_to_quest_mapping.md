# 010a — Scenario-to-Quest Mapping

## Canonical Mapping

All mappings are defined in `backend/app/modules/scenarios/scenario_quest_mapping.py`.

### QA Scenarios

```json
{
  "qa_bug_report_structure_v1": {
    "quest_id": "qa_bug_report_structure_v1",
    "mode": "CONVERTED",
    "trainer_slug": "qa_engineer_interview_trainer",
    "reason": "Converted to mini-quest with 5 interaction types + debrief"
  },
  "qa_test_case_vs_checklist_v1": {
    "quest_id": "qa_payment_defect_release",
    "mode": "REDIRECTED",
    "trainer_slug": "qa_engineer_interview_trainer",
    "reason": "Maps to existing QA quest about test design and release decisions"
  },
  "qa_login_form_testing_v1": {
    "quest_id": "qa_payment_defect_release",
    "mode": "REDIRECTED",
    "trainer_slug": "qa_engineer_interview_trainer",
    "reason": "Maps to existing QA quest covering evidence collection and analysis"
  },
  "qa_regression_vs_retest_v1": {
    "quest_id": null,
    "mode": "HIDE_TEMPORARILY",
    "trainer_slug": "qa_engineer_interview_trainer",
    "reason": "No suitable quest equivalent yet"
  },
  "qa_self_presentation_v1": {
    "quest_id": null,
    "mode": "HIDE_TEMPORARILY",
    "trainer_slug": "qa_engineer_interview_trainer",
    "reason": "Generic self-presentation; no quest equivalent yet"
  }
}
```

### BA Scenarios

```json
{
  "ba_phase2_stakeholder_requirements": {
    "quest_id": "ba_payment_requirements_conflict",
    "mode": "REDIRECTED",
    "trainer_slug": "business_analyst_interview_trainer"
  },
  "ba_phase2_process_analysis": {
    "quest_id": null,
    "mode": "HIDE_TEMPORARILY",
    "trainer_slug": "business_analyst_interview_trainer"
  },
  "ba_phase2_documentation_artifacts": {
    "quest_id": null,
    "mode": "HIDE_TEMPORARILY",
    "trainer_slug": "business_analyst_interview_trainer"
  },
  "ba_phase2_conflict_resolution": {
    "quest_id": "ba_payment_requirements_conflict",
    "mode": "REDIRECTED",
    "trainer_slug": "business_analyst_interview_trainer"
  },
  "ba_phase2_traceability_impact": {
    "quest_id": null,
    "mode": "HIDE_TEMPORARILY",
    "trainer_slug": "business_analyst_interview_trainer"
  },
  "ba_phase2_real_case_analysis": {
    "quest_id": null,
    "mode": "HIDE_TEMPORARILY",
    "trainer_slug": "business_analyst_interview_trainer"
  }
}
```

## Validation

- All mapped quests exist in the quest registry
- No circular redirects (all quest_id values are different from scenario_id)
- Trainer slugs are consistent between mapping and quest definitions
- Hidden scenarios excluded from learner catalog listing
