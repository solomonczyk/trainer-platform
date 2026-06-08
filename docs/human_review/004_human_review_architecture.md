# Human Review Vertical Layer — Architecture

## Layer ID
TRAINER-PLATFORM-CONTROLLED-GENERATED-ITEM-HUMAN-REVIEW-VERTICAL-LAYER-004

## Overview
The Human Review layer introduces a controlled, audited human review workflow for generated assessment-item candidates. It extends the existing generation pipeline and sits between automated validation and any future pilot/exam-eligible pool.

## Architecture Diagram

```
Generation Pipeline (existing)
  └─ Generation Request
     └─ Provider Call
        └─ Candidate Normalization
           └─ Validation Run (15 validators)
              ├─ REJECTED / VALIDATION_FAILED → terminal
              └─ READY_FOR_HUMAN_REVIEW
                 └─ Review Handoff (existing)

Human Review Layer (004 — NEW)
  └─ Review Case Creation (from handoff)
     └─ PENDING_ASSIGNMENT
        └─ Reviewer Assignment
           └─ ASSIGNED
              └─ Reviewer Claims
                 └─ IN_REVIEW
                    ├─ Evidence Inspection
                    │  ├─ Candidate Content
                    │  ├─ Validation Summary
                    │  ├─ Provenance
                    │  ├─ Source Bindings
                    │  ├─ Duplicate Detection
                    │  └─ Safety Gates
                    └─ Decision Submission
                       ├─ APPROVED_FOR_PILOT_REVIEW →
                       ├─ REJECTED → terminal
                       ├─ CHANGES_REQUESTED →
                       └─ ESCALATED →
```

## Database Schema (Migration 007)

### cert_human_review_cases
Tracks the review lifecycle for each candidate. Created from a valid review handoff.

### cert_reviewer_assignments
Tracks one active assignment per case (enforced by partial unique index).

### cert_human_review_decisions
Append-only immutable decision records. No update/delete supported.

## Key Design Decisions

1. **Idempotent case creation**: Multiple calls with the same handoff ID return the existing active case.
2. **Single active assignment**: The partial unique index on (`review_case_id`) WHERE `status IN ('ASSIGNED', 'CLAIMED')` enforces exactly one active reviewer at a time.
3. **Append-only decisions**: `HumanReviewDecision` has no `updated_at` column or update methods.
4. **Version tracking**: Each case transition increments `version`, enabling optimistic concurrency.
5. **Audit coupling**: Every action creates an append-only audit event via the existing `AuditService`.
