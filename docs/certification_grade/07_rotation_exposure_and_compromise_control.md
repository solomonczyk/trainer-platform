# Rotation, Exposure and Compromise Control

**Document ID:** CGSF-ROTATION-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Prevent memorization, overexposure, repeated forms and compromised questions while preserving comparability.

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

## Objectives

- reduce repeat exposure to the same candidate;
- control global exposure;
- rotate item families and contexts;
- detect leaked or compromised items;
- maintain blueprint and difficulty equivalence.

## Selection constraints

```json
{
  "same_user_repeat_cooldown_days": 90,
  "recent_item_window": 200,
  "max_same_family_per_form": 2,
  "max_form_overlap_percent": 25,
  "max_item_exposure_rate": 0.20,
  "exclude_suspected_compromised": true,
  "reserve_unscored_pilot_slots": 5
}
```

## Exposure metrics

- total deliveries;
- unique candidates;
- exposure rate by form/window;
- repeated exposure per candidate;
- family exposure;
- answer-pattern anomaly;
- external leak signal;
- performance shift after suspected publication.

## Rotation strategy

1. Select eligible items by blueprint node.
2. Exclude recent candidate history.
3. Exclude exposure-limit violations.
4. Balance item families.
5. Match target difficulty and time.
6. reserve pilot items where allowed.
7. record exact selection decision.

## Compromise response

```text
Detect signal -> suspend item -> invalidate future forms -> investigate
-> replace with equivalent item -> measure score impact -> document decision
```

Past candidate scores are not automatically invalidated. Impact analysis and governance decision are required.
