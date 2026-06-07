## Generated Item Review Handoff Contract

### Handoff Trigger

A human review handoff is created only when a generated candidate passes required validation with decision **READY_FOR_HUMAN_REVIEW**.

### Handoff Package Contents

| Field | Description |
|-------|-------------|
| candidate_id | Unique candidate identifier |
| generation_request_id | Originating generation request |
| domain/competency | Content alignment metadata |
| difficulty/locale | Item specifications |
| item_family | Family binding |
| source versions | Trusted sources used |
| prompt/policy versions | Generation configuration |
| validation summary | All validator results aggregated |
| warnings | Non-blocking issues |
| answer/rubric package | For authorized reviewers only |
| learner-facing preview | What learners would see |
| provenance summary | Complete lineage |
| reviewer roles allowed | Which roles can review |
| forbidden actions | What reviewers cannot do |

### Handoff Statuses

- `pending_human_review` — awaiting reviewer action
- `in_review` — being reviewed
- `reviewed` — review completed
- `cancelled` — handoff cancelled

### Forbidden Actions (in this layer)

- Approve/publish generated item
- Add to pilot pool
- Add to exam-eligible pool
- Assemble into exam
- Accept as production-ready

### Reviewer Access Control

| Role | Access to answer key |
|------|---------------------|
| platform_admin | Yes |
| generation_operator | Yes |
| domain_owner | Yes |
| content_author | No |
| psychometric_reviewer | Yes |
| qa_reviewer | No (raw response only) |
| read_only_auditor | No |
| learner | No |

### Required Handoff State

```json
{
  "handoff_status": "pending_human_review",
  "human_review_completed": false,
  "human_accepted": false,
  "pilot_allowed": false,
  "exam_eligible_allowed": false,
  "publication_allowed": false
}
```
