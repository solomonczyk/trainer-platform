# Analytics, Effectiveness and Evidence Model

**Document ID:** CGSF-EVIDENCE-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Measure item quality, learning gain, readiness accuracy and operational health while preserving privacy.

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

## Analytics categories

### Operational

- latency, failure rate, provider cost;
- session abandonment;
- autosave/recovery success;
- browser and API errors.

### Assessment quality

- item difficulty and discrimination;
- reliability and measurement error;
- form equivalence;
- rubric agreement;
- exposure and compromise signals.

### Learning effectiveness

- pre/post score change;
- competency mastery growth;
- retention after delay;
- completion and remediation uptake;
- pass probability calibration.

## Evidence of effectiveness

A simulator may be described as validated only after collecting evidence that:

- domain experts approve content coverage;
- score reliability is acceptable;
- item statistics behave as expected;
- AI scores agree with expert scoring within tolerance;
- readiness predictions are calibrated against later outcomes where available;
- learners demonstrate measurable improvement.

## Privacy-safe event example

```json
{
  "event": "exam_item_answered",
  "item_id": "...",
  "item_version": 7,
  "correct": false,
  "response_time_ms": 64000,
  "competency_ids": ["..."],
  "raw_answer": "FORBIDDEN"
}
```

## Reports

- item health dashboard;
- form equivalence report;
- rubric drift report;
- readiness calibration report;
- domain-pack effectiveness report;
- privacy and retention audit.
