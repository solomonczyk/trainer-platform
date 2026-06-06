# Adaptive Learning and Readiness Prediction

**Document ID:** CGSF-ADAPTIVE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Convert assessment evidence into personalized practice while keeping exam mode secure and interpretable.

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

## Adaptive practice inputs

- competency mastery estimates;
- recent errors;
- item exposure history;
- response time;
- confidence/self-rating where used;
- prerequisite graph;
- forgetting interval;
- target exam date and blueprint.

## Selection policy

Prioritize:

1. critical weak competencies;
2. prerequisites blocking higher skills;
3. items near current ability;
4. spaced repetition due items;
5. under-sampled blueprint nodes;
6. varied item families and contexts.

## Readiness model

```json
{
  "overall_readiness": 0.73,
  "confidence_interval": [0.66, 0.79],
  "estimated_pass_probability": 0.76,
  "critical_domain_risk": ["stakeholder_analysis"],
  "evidence_volume": "moderate",
  "model_version": "readiness-1.0"
}
```

## Communication rules

Never present readiness as certainty. Reports must state evidence limitations, bank calibration status and difference between platform readiness estimate and official examination result.

## Exam-mode separation

Adaptive selection is permitted only if the target exam model supports adaptive testing. Otherwise exam simulation uses fixed blueprint-equivalent forms, while adaptation is limited to practice mode.
