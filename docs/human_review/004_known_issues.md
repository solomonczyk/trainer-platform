# Known Issues — Human Review Layer 004

## Current

1. **No CI fast-path architecture**: The full test suite takes 12–15 minutes in CI. This is a pre-existing constraint outside this layer's scope.
2. **No email/push notification**: Reviewers are not automatically notified when assigned. This is a future enhancement.
3. **No SLA tracking**: Time-to-review metrics are not collected. The `opened_at` field is populated but not used for SLAs.
4. **Reviewer calendar integration**: Not implemented — scheduling is manual.
5. **Batch operations**: Creating review cases for multiple candidates from one generation request must be done individually.
6. **No mobile-optimized UI**: The frontend workspace is designed for desktop.

## Resolved during implementation

1. ~~Hash mismatch in tests~~ — Fixed by computing candidate hash from actual content rather than using a UUID.
2. ~~Idempotency check used wrong field~~ — Fixed by looking up handoff first, then comparing using DB ID.
3. ~~Frontend TypeScript error TS2367 (impossible comparison between `"APPROVED_FOR_PILOT_REVIEW"` and `"IN_REVIEW"`)~~ — Fixed in CI regression closeout by separating state domains (case status vs decision status).
4. ~~Backend migration tests fail after migration 007~~ — Fixed in CI regression closeout by updating head revision assertions (006→007) and table count expectations (60→63 total, 31→34 cert_).
