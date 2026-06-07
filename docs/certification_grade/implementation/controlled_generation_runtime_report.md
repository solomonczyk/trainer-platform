## Controlled Generation Runtime Report

### Implementation Summary

| Component | Status |
|-----------|--------|
| Generation request contract | IMPLEMENTED |
| Source binding | IMPLEMENTED |
| Prompt package construction | IMPLEMENTED |
| AI Gateway integration | IMPLEMENTED |
| Provider adapter (Mock) | IMPLEMENTED |
| Provider adapter (DeepSeek) | IMPLEMENTED |
| Raw response capture | IMPLEMENTED |
| Candidate normalization | IMPLEMENTED |
| Schema validation (V1) | IMPLEMENTED |
| Required field validation (V2) | IMPLEMENTED |
| Source citation validation (V3) | IMPLEMENTED |
| Competency alignment (V4) | IMPLEMENTED |
| Difficulty alignment (V5) | IMPLEMENTED |
| Item family compliance (V6) | IMPLEMENTED |
| Answer/options consistency (V7) | IMPLEMENTED |
| Rubric consistency (V8) | IMPLEMENTED |
| Ambiguity detection (V9) | IMPLEMENTED |
| Duplicate/similarity detection (V10) | IMPLEMENTED |
| Prohibited content/safety (V11) | IMPLEMENTED |
| Locale validation (V12) | IMPLEMENTED |
| Answer key leak detection (V13) | IMPLEMENTED |
| Provenance completeness (V14) | IMPLEMENTED |
| Pool mutation guard (V15) | IMPLEMENTED |
| Validation decision aggregation | IMPLEMENTED |
| Provenance record | IMPLEMENTED |
| Audit record | IMPLEMENTED |
| Review handoff | IMPLEMENTED |

### Real Generation Execution

- Provider: mock (DeepSeek configured via AI Gateway)
- Candidates requested: 1
- Candidates generated: 1
- Validation result: VALIDATION_FAILED (1 major, 1 warning)
- Reason: Missing source citations in generated mock item
- No automatic retry executed
- No exam assembly executed

### Audit Events Recorded

- generation_request_created
- generation_request_authorized
- generation_started
- provider_call_completed
- candidate_normalized
- candidate_validation_started
- candidate_validation_failed
- generation_request_completed

### RBAC Enforcement

- generation_operator role added
- Self-authorization blocked
- Content author authorization blocked
- Learner generation access blocked
- Learner answer-key access blocked
- Raw response access restricted
