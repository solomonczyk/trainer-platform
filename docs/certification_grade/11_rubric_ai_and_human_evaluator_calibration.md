# Rubric, AI and Human Evaluator Calibration

**Document ID:** CGSF-RUBRIC-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Make open-response scoring reliable through explicit rubrics, anchor responses, human calibration and monitored AI agreement.

## Current strategic state
```json
{
  "product_type": "certification_grade_assessment_and_exam_simulation_platform",
  "official_certificate_issuer": false,
  "quality_target": "comparable_to_serious_professional_and_language_exams",
  "current_vertical_slice": "BA Trainer Phase 1 REAL_STAGING_ACCEPTED",
  "production_accepted": false,
  "release_allowed": false
}
```

## Principle

The LLM is an evaluator runtime, not the source of truth. Quality comes from rubric design, anchor examples, schema validation and agreement studies.

## Rubric structure

```json
{
  "rubric_id": "ba.user_story.1.0",
  "criteria": [
    {
      "criterion_id": "clarity",
      "weight": 0.20,
      "levels": {
        "0": "unusable or absent",
        "1": "major ambiguity",
        "2": "mostly understandable with gaps",
        "3": "clear and testable",
        "4": "precise, risk-aware and complete"
      }
    }
  ],
  "critical_errors": ["invented stakeholder approval", "untestable acceptance condition"]
}
```

## Anchor set

Every rubric requires:

- multiple weak responses;
- borderline responses;
- passing responses;
- excellent responses;
- expert scores and rationales;
- adversarial/irrelevant responses.

## AI evaluation contract

- provider and model recorded;
- deterministic structured schema;
- criterion scores bounded;
- total score consistent with weights;
- `validation_status=validated` required;
- reasoning content normalized and not exposed as hidden chain-of-thought;
- failure returns safe state, not fabricated score.

## Calibration metrics

- exact agreement rate;
- adjacent agreement rate;
- mean absolute score difference;
- weighted kappa/intraclass correlation where appropriate;
- pass/fail agreement;
- subgroup bias analysis;
- drift over model or prompt versions.

## Human review triggers

- borderline pass score;
- schema repair required;
- low confidence;
- critical error detected;
- AI/human disagreement beyond tolerance;
- candidate appeal;
- new rubric/model version.
