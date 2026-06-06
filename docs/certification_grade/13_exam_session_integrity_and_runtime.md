# Exam Session Integrity and Runtime

**Document ID:** CGSF-SESSION-001  
**Status:** Proposed baseline for implementation  
**Version:** 1.0  
**Owner:** Trainer Platform Product & Architecture  
**Applies to:** All current and future simulator/domain packs  

## Purpose
Define secure, reliable and recoverable exam sessions with strict mode separation.

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

## Exam session states

```json
[
  "created",
  "identity_confirmed",
  "instructions_viewed",
  "started",
  "in_progress",
  "interrupted",
  "resumed",
  "submitted",
  "scoring",
  "scored",
  "invalidated",
  "appeal_pending",
  "closed"
]
```

## Runtime requirements

- server-authoritative timer;
- idempotent answer save;
- autosave and interruption recovery;
- immutable delivered form;
- no answer reveal before completion;
- explicit final submission confirmation;
- duplicate submission prevention;
- audit trail for navigation and state changes;
- controlled accommodation time;
- timezone-independent timestamps.

## Integrity controls by maturity

### Baseline

- authenticated session;
- randomized equivalent form;
- exposure controls;
- browser focus/interruption signals recorded, not automatically punished;
- rate limits and abuse monitoring.

### Advanced optional

- identity verification;
- secure browser;
- proctoring integration;
- plagiarism/similarity analysis;
- organization-specific invigilation.

## Failure handling

A provider or network failure must preserve answers and time policy. Blind re-scoring and duplicate billing are prohibited. Every retry requires idempotency key and reason code.
