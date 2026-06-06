# Phase 1 Activity Contract — BA Trainer

## Conceptual Model

```json
{
  "id": "string (UUID, auto-generated)",
  "activity_id": "string (business key, e.g. 'ba_hr_q1_single')",
  "trainer_product_id": "string (FK to trainer_products.id)",
  "module_id": "string",
  "activity_type": "single_choice|multiple_choice|numeric|fill_blanks|matching",
  "evaluation_mode": "deterministic",
  "difficulty": "junior|middle|senior",
  "title_key": "string (i18n key)",
  "description_key": "string or null",
  "payload": "type-specific object (with correct answers for server-side validation)",
  "explanation_key": "string (i18n key)",
  "order": "integer",
  "version": "string (semver)"
}
```

## Type-Specific Payloads

### single_choice
```json
{"options": ["A", "B", "C"], "correct": "A"}
```

### multiple_choice
```json
{"options": ["A", "B", "C"], "correct": ["A", "B"]}
```

### numeric
```json
{"correct": 42, "tolerance": 0}
```

### fill_blanks
```json
{
  "template": "___ is a ___",
  "blanks": [{"id": "blank_0", "options": []}, {"id": "blank_1"}],
  "correct": ["value1", "value2"]
}
```

### matching
```json
{
  "left_items": ["A", "B"],
  "right_items": ["1", "2"],
  "pairs": [{"left": "A", "right": "1"}, {"left": "B", "right": "2"}]
}
```

## Validation Result Contract

```json
{
  "status": "correct|partial|incorrect",
  "score": "integer 0-100",
  "passed": "boolean",
  "feedback": "type-specific object (safe, no correct answers leaked)",
  "evaluation_mode": "deterministic",
  "validation_status": "validated"
}
```

## Backward Compatibility

- Existing `Scenario` model unchanged
- Existing `Attempt` model unchanged (new nullable columns added)
- Existing `Evaluation` / `DeterministicEvaluation` are separate tables
- QA Trainer uses old flow; BA Trainer uses new Activity model
- No schema migration required for existing QA data
