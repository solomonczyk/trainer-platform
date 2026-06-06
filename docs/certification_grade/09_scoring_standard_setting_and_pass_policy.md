# Scoring, Standard Setting and Pass Policy

**Document ID:** CGSF-SCORING-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define defensible scoring, domain minimums, pass thresholds, partial credit and versioned policies.

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

## Scoring principles

- scoring logic is versioned;
- score calculation is deterministic after validated evaluation;
- item weights are blueprint-governed;
- open-response scores use approved rubrics;
- critical-domain failures may override overall score;
- pass thresholds are not arbitrary UI constants.

## Scoring policy

```json
{
  "policy_id": "ba.score.1.0",
  "scale": {"min": 0, "max": 100},
  "pass_score": 70,
  "critical_domain_minimums": {"requirements_analysis": 60},
  "negative_marking": false,
  "partial_credit": true,
  "rounding_rule": "half_up_one_decimal",
  "unscored_pilot_items_excluded": true
}
```

## Standard-setting options

- modified Angoff expert judgment;
- bookmark method;
- contrasting groups after pilot data;
- external target-exam pass standard where legally and methodologically appropriate.

## Required process

1. Define minimally competent candidate.
2. Expert panel estimates item success probability.
3. Aggregate and discuss variance.
4. Pilot against real candidate data.
5. Adjust with documented evidence.
6. Approve threshold and confidence interval.

## Score report

Must include:

- total score;
- pass/fail under policy version;
- domain scores;
- critical-domain status;
- confidence interval or measurement error;
- readiness interpretation;
- limitations and recommended remediation.
