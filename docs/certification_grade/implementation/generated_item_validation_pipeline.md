## Generated Item Validation Pipeline

### Validator List

| Code | Name | Severity | Description |
|------|------|----------|-------------|
| V1 | Schema Validation | critical | Validates JSON structure against schema |
| V2 | Required Fields | critical | Checks all required fields present and non-empty |
| V3 | Source Citations | major | Validates source citation completeness |
| V4 | Competency Alignment | major | Validates competency and domain alignment |
| V5 | Difficulty Alignment | major | Validates difficulty level |
| V6 | Item Family Compliance | major | Validates item family binding |
| V7 | Answer/Options Consistency | critical | Validates MC options and answer key |
| V8 | Rubric Consistency | major | Validates rubric structure |
| V9 | Ambiguity Detection | minor | Detects ambiguous language |
| V10 | Duplicate/Similarity | major | Detects exact and near duplicates |
| V11 | Prohibited Content/Safety | critical | Detects unsafe content |
| V12 | Locale Validation | major | Validates locale match |
| V13 | Answer Key Leak | critical | Detects answer markers in learner text |
| V14 | Provenance Completeness | major | Validates provenance record |
| V15 | Pool Mutation Guard | critical | Blocks pool mutations |

### Decision Rules

- **REJECTED**: any critical failure → candidate rejected, no review handoff
- **VALIDATION_FAILED**: major failures but no critical → validation_failed, no handoff
- **READY_FOR_HUMAN_REVIEW**: no critical or major failures → handoff created
- Warnings alone do not block handoff

### Validation Result Format

```json
{
  "validator_code": "V1",
  "validator_version": "1.0.0",
  "status": "passed|failed|warning|not_run",
  "severity": "info|minor|major|critical",
  "reason_code": "string",
  "details": {},
  "executed_at": "timestamp"
}
```
