# Dynamic Item Bank Runtime Architecture

## Overview

The Dynamic Item Bank Runtime layer implements the operational runtime on top of the certification-grade core contracts. It provides controlled authoring, review, publication, pilot governance, exposure tracking, rotation, suspension, retirement, traceability, and governance reporting.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Item Bank Runtime API                       │
│  /api/v1/certification-core/item-bank/                       │
│                                                              │
│  POST   /items                        Create item draft      │
│  PATCH  /items/{id}                   Update draft           │
│  POST   /items/{id}/submit            Submit for review      │
│  POST   /items/{id}/bind-source       Bind knowledge source  │
│  GET    /items/{id}/traceability      Get source bindings    │
│  GET    /reviews/queue                Review queue           │
│  POST   /items/{id}/review            Perform review         │
│  POST   /items/{id}/pilot             Enter pilot pool       │
│  POST   /items/{id}/pilot/complete    Complete pilot         │
│  POST   /items/{id}/exam-eligibility  Enter exam-eligible    │
│  POST   /items/{id}/exposure          Record exposure        │
│  GET    /items/{id}/exposure          Get exposure data      │
│  GET    /items/{id}/rotation-eligibility  Rotation check     │
│  POST   /items/{id}/suspend           Suspend item           │
│  POST   /items/{id}/unsuspend         Unsuspend item         │
│  POST   /items/{id}/retire            Retire item            │
│  POST   /items/{id}/supersede         Supersede item         │
│  GET    /pools/pilot                  Query pilot pool       │
│  GET    /pools/exam-eligible          Query exam-eligible    │
│  GET    /governance/summary           Governance dashboard   │
│  GET    /governance/incidents         Governance incidents   │
└─────────────────────────────────────────────────────────────┘
```

## Services

| Service | Responsibility |
|---|---|
| AuthoringService | Controlled item creation with validation |
| ReviewService | Review queue and decision management |
| PilotPoolService | Pilot pool entry and lifecycle |
| ExamEligiblePoolService | Exam-eligible pool with gating |
| ExposureService | Idempotent exposure tracking |
| RotationPolicyService | Rotation policy and eligibility |
| GovernanceService | Suspension, retirement, supersession |
| SourceTraceabilityService | Source binding and validation |

## Data Model

New runtime tables extend the core certification schema:

- `cert_item_source_bindings` — traceability snapshots
- `cert_item_reviews` — review records
- `cert_item_review_decisions` — immutable decision trail
- `cert_item_pool_memberships` — pilot / exam-eligible pool tracking
- `cert_item_exposure_events` — idempotent exposure log
- `cert_item_exposure_counters` — aggregated exposure counters
- `cert_item_rotation_policies` — rotation policy configuration
- `cert_item_governance_incidents` — governance flags
- `cert_item_supersession_links` — replacement tracking
- `cert_item_exception_approvals` — controlled exceptions

## Security

- Answer keys hidden from non-admin roles
- Author self-approval blocked
- Domain owner self-approval blocked
- LLM self-approval blocked
- All mutations audited (append-only)
- RBAC enforced on all endpoints
