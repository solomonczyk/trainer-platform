# Phase 1 Deterministic Validator Report

## Validator Registry

Location: `backend/app/modules/activities/validators/registry.py`

Maps activity types to validator functions:
- `single_choice` → `validate_single_choice`
- `multiple_choice` → `validate_multiple_choice`
- `numeric` → `validate_numeric`
- `fill_blanks` → `validate_fill_blanks`
- `matching` → `validate_matching`

## Validator Details

### single_choice
- **Strategy**: Exact trimmed string comparison
- **Case-sensitive**: Yes
- **Whitespace**: Trimmed before comparison
- **Partial score**: No (all-or-nothing)

### multiple_choice
- **Strategy**: Order-independent set comparison
- **Partial score**: Yes (correct_selected / total_correct × 100)
- **Extra options**: Strict rejection (score = 0)
- **Whitespace**: Trimmed per option

### numeric
- **Strategy**: Float comparison with configurable tolerance
- **Tolerance**: From payload (default 0)
- **Invalid input**: Caught safely (returns incorrect)

### fill_blanks
- **Strategy**: Ordered blank-by-blank comparison
- **Normalization**: Strip, collapse whitespace, lowercase
- **Partial score**: Yes (correct_blanks / total_blanks × 100)
- **Dropdown options**: Supported per blank

### matching
- **Strategy**: Order-independent pair mapping
- **Unknown keys**: Strict rejection (score = 0)
- **Partial score**: Yes (correct_pairs / total_pairs × 100)

## Security

- Correct answers stored in `payload.correct` (server-side only)
- Public API endpoints (`list`, `start`) strip correct answers
- Validator always uses server-side payload source
- Frontend cannot self-award pass

## Tests

48 validator tests covering:
- Correct/incorrect cases for all 5 types
- Partial scoring
- Malformed inputs
- Null/empty edge cases
- Whitespace normalization
- Tolerance boundaries
- Extra option rejection
- Unknown key rejection
- Registry dispatch
