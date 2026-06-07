## Generated Item Provenance Contract

### Lineage Requirements

Every generated candidate must have complete provenance tracking:

```
Generation Request
  → Source Versions (with checksums)
    → Prompt Version (with hash)
      → Policy Version
        → Provider
          → Model
            → Raw Response Hash
              → Normalized Candidate Hash
                → Validator Versions
                  → Validation Results
                    → Decision
                      → Review Handoff
```

### Provenance Record Fields

```json
{
  "provider": "deepseek",
  "model": "deepseek-v4-flash",
  "source_version_ids": ["uuid"],
  "source_checksums": ["sha256"],
  "prompt_template_version": "semver",
  "prompt_hash": "sha256",
  "generation_policy_version": "semver",
  "schema_version": "semver",
  "raw_response_hash": "sha256",
  "candidate_hash": "sha256",
  "validator_versions": {"V1": "1.0.0", "V2": "1.0.0", ...},
  "correlation_id": "uuid",
  "request_timestamp": "timestamp",
  "response_timestamp": "timestamp"
}
```

### Append-Only

All provenance records are append-only. No update or delete operations are permitted on provenance tables.

### Tables

- `cert_candidate_provenance` — main provenance record (1:1 with candidate)
- `cert_candidate_validation_runs` — validation run record
- `cert_candidate_validation_results` — individual validator results
