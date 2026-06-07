# Dynamic Item Bank Runtime — Known Issues

## Runtime Limitations

1. **Psychometric metrics are placeholder-only**: Difficulty and discrimination estimates are stored as nullable fields. Real psychometric calibration requires sufficient candidate response data which does not exist yet.

2. **No pilot data fabrications**: The runtime correctly marks psychometric metrics as unavailable rather than fabricating them. A future layer should integrate real candidate response data.

3. **Review SLA breach detection**: SLA breach detection is not yet implemented as a background process. Current governance summary returns 0 for SLA breaches. This requires a scheduled task that compares review timestamps against configured SLAs.

4. **Rotation policy defaults**: Default rotation policies use hardcoded values (100 max exposures, 30-day window, 7-day cooldown). These should be configurable per domain pack through the admin interface.

## Migration Notes

5. **Migration 004 creates 10 tables**: All new tables use the `cert_` prefix. No BA/QA tables are modified. The migration fully passes the upgrade/downgrade/upgrade cycle.

## Integration Points

6. **Exam form assembly not yet connected**: The item-selection result is advisory/pool-query only. Full exam form assembly belongs in a future layer.

7. **BA/QA migration adapter ready but not executed**: The `ba_qa_adapter` exists but has not been run. BA/QA content remains separate from the certification item bank.

## Security

8. **Answer keys restricted**: Only `platform_admin` and `domain_owner` can read answer keys. All other roles (including `qa_reviewer`, `read_only_auditor`, and `guest`) cannot access answer keys.
