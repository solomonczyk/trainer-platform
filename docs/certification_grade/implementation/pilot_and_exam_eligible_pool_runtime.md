# Pilot and Exam-Eligible Pool Runtime

## Pilot Pool

### Entry Requirements

An item may enter the pilot pool only when:
- Expert review passed
- QA review passed
- Source traceability valid
- Rubric version active
- Item version immutable

### Pilot States

- `pilot_ready` — Awaiting pilot entry
- `pilot_active` — Currently in pilot
- `pilot_suspended` — Pilot halted
- `pilot_completed` — Pilot finished
- `pilot_rejected` — Pilot failed

### Pilot Data

- Item version ID
- Entry date
- Exposure count
- Response count
- Difficulty estimate (placeholder — not fabricated)
- Discrimination estimate (placeholder — not fabricated)
- Incident count
- Flags
- Next review date

## Exam-Eligible Pool

### Entry Requirements

An item may become exam-eligible only if:
- Expert review passed
- QA review passed
- Pilot completed or formally waived
- Psychometric gate passed or controlled exception
- Source traceability valid
- Item version active
- Rubric version active
- Not suspended
- Not retired

### Controlled Exception

May bypass psychometric gate with:
- Platform admin authorization
- Documented reason
- Second reviewer approval
- Audit event
- Expiration date
- No self-approval

## Key Rules

- Pilot pool is NOT exam-eligible pool
- Pilot items are NOT certification items by default
- Pilot metrics are marked unavailable without real data
- Direct `draft → exam_eligible` is blocked
- Answer keys hidden from non-admin roles
