# Dynamic Item Bank Runtime — Known Issues

## Runtime Limitations

1. **Psychometric metrics are placeholder-only**: Difficulty and discrimination estimates are stored as nullable fields. Real psychometric calibration requires sufficient candidate response data which does not exist yet.

2. **No pilot data fabrications**: The runtime correctly marks psychometric metrics as unavailable rather than fabricating them. A future layer should integrate real candidate response data.

3. **Review SLA breach detection**: SLA breach detection is not yet implemented as a background process. Current governance summary returns 0 for SLA breaches. This requires a scheduled task that compares review timestamps against configured SLAs.

4. **Rotation policy defaults**: Default rotation policies use hardcoded values (100 max exposures, 30-day window, 7-day cooldown). These should be configurable per domain pack through the admin interface.

5. **Insufficient pool detection is advisory**: The rotation policy flags insufficient pool conditions but does not hard-block exam sessions. A future layer should add hard-block behavior.

## Controlled Exception

6. **Exception scope validated at grant-time**: Cross-item-version reuse checks happen when the gate service evaluates the exception, not when the exception is requested. This is safe but could be stricter.

## Migration Notes

7. **Migration 005 adds enhanced columns**: New columns added to `cert_item_rotation_policies` (enhanced policy inputs) and `cert_item_exception_approvals` (two-person control fields). Full upgrade/downgrade/upgrade cycle verified against real PostgreSQL 16.

## Integration Points

8. **Exam form assembly not yet connected**: The item-selection result is advisory/pool-query only. Full exam form assembly belongs in a future layer.

9. **BA/QA migration adapter ready but not executed**: The `ba_qa_adapter` exists but has not been run. BA/QA content remains separate from the certification item bank.

## Security

10. **Answer keys restricted**: Only `platform_admin` and `domain_owner` can read answer keys. All other roles (including `qa_reviewer`, `read_only_auditor`, and `guest`) cannot access answer keys.

## Resolved (this closeout)

- ✅ Rotation balance enforcement: all policy inputs produce verified decisions with reasons
- ✅ Controlled exception contract: two-person approval, expiration, self-approval prevention, audit
- ✅ Single exam-eligibility gate: all paths through one authoritative service
- ✅ Regression evidence: exact commands and results documented
- ✅ PostgreSQL migration 005 created and verified
- ✅ Migration 005 real PostgreSQL cycle: upgrade → downgrade → upgrade proven executed
- ✅ Migration 005 objects removed on downgrade and restored on second upgrade
