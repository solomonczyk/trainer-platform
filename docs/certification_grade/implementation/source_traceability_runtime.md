# Source Traceability Runtime

## Purpose

Every submitted item must reference at least one active or accepted knowledge source version. Source bindings are snapshotted at submission time so future source changes do not erase the evidence used when the item was reviewed.

## Validation Rules

| Check | Description |
|---|---|
| source_exists | Source must exist in registry |
| source_version_exists | Source version must match |
| source_status_allowed | Source must not be retired/suspended |
| source_not_retired | Retired sources cannot be bound |
| source_domain_matches | Source domain must align |
| source_reference_snapshot_saved | Binding snapshot is persisted |

## Traceability Snapshot Data

Each binding stores:
- Source registry ID
- Source version ID  
- Source content hash
- Source title
- Source URI/identifier
- Retrieved/approved date
- Applicable section reference
- Binding actor ID
- Binding timestamp

## Blocking Rules

Submission is blocked if:
- No source binding exists
- Source is suspended or retired
- Source version is missing
- Domain mismatch exists
- Source hash is unavailable
