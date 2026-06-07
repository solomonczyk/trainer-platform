## Generated Item Schema Contract

### Learner-Facing Schema

```json
{
  "candidate_id": "uuid",
  "item_type": "enum",
  "stem": "string",
  "options": [{"id": "string", "text": "string"}],
  "locale": "string",
  "difficulty": "enum"
}
```

**Excluded from learner view:**
- answer_key
- correct option indicators
- reviewer notes
- hidden rubric details
- raw provider response
- internal prompt
- provider reasoning content

### Admin/Reviewer Schema

```json
{
  "candidate_id": "uuid",
  "generation_request_id": "uuid",
  "item_family_id": "uuid",
  "domain_id": "uuid",
  "competency_id": "uuid",
  "difficulty": "enum",
  "locale": "string",
  "item_type": "enum",
  "stem": "string",
  "options": [{"id": "string", "text": "string"}],
  "answer_key": {"correct_option_id": "string"},
  "rationale": "string",
  "rubric": {"criteria": [...]},
  "source_citations": [...],
  "provider": "string",
  "model": "string",
  "raw_response_hash": "sha256",
  "normalized_payload_hash": "sha256",
  "status": "enum",
  "validation_status": "enum"
}
```

### Schema Validation Rules

- JSON parsability required
- Schema version required
- Exact item type (must be in allowed set)
- Required fields: item_type, stem, answer_key, rationale
- Enum values must be in defined sets
- Field lengths must not exceed limits
- Locale must match expected
- Answer structure must be valid
- Options cardinality: 2-5 for MC items
- Citation structure must be valid
- Rubric structure must be valid
