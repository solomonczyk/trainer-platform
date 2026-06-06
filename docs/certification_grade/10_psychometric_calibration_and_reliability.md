# Psychometric Calibration and Reliability

**Document ID:** CGSF-PSYCH-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Measure item difficulty, discrimination, reliability, fairness and equivalence instead of relying on author opinion.

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

## Minimum classical test theory metrics

```json
{
  "p_value_difficulty": 0.58,
  "discrimination_index": 0.34,
  "point_biserial": 0.31,
  "median_response_time_seconds": 72,
  "omit_rate": 0.03,
  "sample_size": 850
}
```

## Exam metrics

- Cronbach alpha or suitable reliability estimate;
- standard error of measurement;
- domain score reliability;
- form difficulty comparison;
- score distribution and floor/ceiling effects;
- decision consistency around pass score.

## Calibration phases

1. Expert difficulty prediction.
2. Unscored or low-stakes pilot.
3. Initial statistics.
4. Item review and correction.
5. Calibrated practice eligibility.
6. Exam eligibility after minimum evidence.
7. Continuous monitoring.

## Sample-size policy

Exact thresholds are domain-dependent. Until adequate data exists, the item remains provisional and must not be represented as fully calibrated.

## IRT roadmap

Later phases may implement 1PL/2PL/3PL or graded response models for:

- ability estimation;
- adaptive testing;
- form linking;
- item information;
- more precise readiness confidence.

## Automatic flags

- too easy or too hard;
- negative discrimination;
- time anomaly;
- option never selected;
- sudden performance shift;
- subgroup differential item functioning;
- excessive missing response.
