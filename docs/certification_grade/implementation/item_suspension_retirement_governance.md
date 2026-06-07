# Item Suspension, Retirement, and Governance

## Suspension

### Reasons

- source_invalidated
- answer_key_defect
- ambiguity
- bias_concern
- legal/compliance
- overexposure
- psychometric_concern
- reviewer_incident
- operator_decision

### Behavior

- Item removed from all active pools (pilot, exam-eligible)
- Governance incident created
- Audit event recorded

## Unsuspension

- Returns item to `under_review` status
- Does NOT automatically re-enter active pools
- Requires domain_owner or platform_admin role

## Retirement

- Permanent removal from all active pools
- Historical records preserved (item NOT deleted)
- Status set to `retired` (terminal lifecycle state)
- Governance incident created

## Supersession

- Links predecessor item to successor item
- Predecessor is retired automatically
- Historical link is preserved in the database
- Supports version replacement tracking

## Governance Dashboard

Provides summary statistics:
- Total drafts, submitted, awaiting review
- Pilot-ready, pilot-active, exam-eligible items
- Suspended, retired items
- Source-invalid items
- Overexposed items
- Items without active rubric
- Review SLA breaches
- Unresolved governance incidents

Supports domain and locale filters.
