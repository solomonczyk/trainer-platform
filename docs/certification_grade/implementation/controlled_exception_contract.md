# Controlled Exception Contract

**Layer:** TRAINER-PLATFORM-DYNAMIC-ITEM-BANK-RUNTIME-AND-GOVERNANCE-VERTICAL-LAYER-002
**Date:** 2026-06-07

## Rules Enforced

| Rule | Status | Verification |
|------|--------|-------------|
| Requester role: platform_admin | ✅ | Non-admin blocked with FORBIDDEN_ROLE |
| Reason required | ✅ | Whitespace-only reason blocked with REASON_REQUIRED |
| Expiration required | ✅ | Schema-enforced, service-double-checked |
| Expiration must be future | ✅ | Past expiration blocked with EXPIRATION_PAST |
| Second reviewer required | ✅ | Exception stays in `first_approved` until second approval |
| Second reviewer allowed roles | ✅ | psychometric_reviewer, qa_reviewer, domain_owner only |
| Requester cannot second-approve | ✅ | SELF_APPROVAL_BLOCKED |
| Author cannot approve | ✅ | AUTHOR_APPROVAL_BLOCKED |
| First approver cannot second-approve | ✅ | SINGLE_PERSON_EXCEPTION_BLOCKED |
| Expired exception rejected | ✅ | Checked at approval and gate entry |
| Revoked exception rejected | ✅ | Checked at gate entry |
| Scope limited to one item version | ✅ | Cross-version reuse blocked |
| Suspended item blocked | ✅ | ITEM_SUSPENDED |
| Retired item blocked | ✅ | ITEM_RETIRED |

## Non-bypassed Gates

The controlled exception may ONLY bypass the psychometric/pilot requirement.
The following gates are NEVER bypassed:
- ✅ Source traceability
- ✅ Expert review
- ✅ QA review
- ✅ Active item version
- ✅ Active rubric
- ✅ Suspension check
- ✅ Retirement check

## Audit Actions

- `exception_requested`
- `exception_first_approved`
- `exception_second_approved`
- `exception_rejected`
- `exception_revoked`
- `exception_expired` (auto on expiration check)
- Audit correlation ID linked to exception record

## Test Results

- ✅ 12 negative tests (all rule violations blocked)
- ✅ 2 positive tests (full workflow + audit verification)
- All 14 tests pass
