# Item Authoring and Review Workflow

## Controlled Authoring Flow

```
Create item family
→ Create item draft with full provenance
→ Bind knowledge sources (required)
→ Validate structure
→ Submit for review
```

### Item Draft Requirements

Every item draft must include:
- Domain pack reference
- Competency bindings
- Item family reference
- Item type
- Prompt/stem
- Response contract
- Answer key
- Rubric version reference
- Knowledge source references
- Difficulty target
- Locale and market
- Author identity
- Creation method (human_authored, llm_assisted, imported)
- Provenance documentation

### Creation Methods

- **human_authored**: Direct human authoring
- **llm_assisted**: AI-generated content with human oversight
- **imported**: Imported from external systems

Note: `llm_assisted` does NOT imply approval. All items must go through the full review workflow.

## Review Workflow

```
author_review_ready
→ expert_review
→ qa_review
→ psychometric_review_or_pilot_ready
```

### Reviewer Decisions

| Decision | Effect |
|---|---|
| approve | Item advances to next stage |
| reject | Item returned to draft |
| request_changes | Item returned to draft with comments |
| suspend | Item immediately suspended |

### Security Rules

- Author cannot review own item
- Domain owner cannot self-approve own authored item
- LLM actors cannot approve items
- Expert reviewer required before pilot entry
- QA reviewer required for ambiguity check
- Psychometric gate required before exam-eligible
