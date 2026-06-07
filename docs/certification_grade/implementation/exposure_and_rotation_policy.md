# Exposure and Rotation Policy

## Exposure Tracking

### Counters

- Total exposure count
- Rolling window exposure count
- Last exposure timestamp
- Exposure threshold
- Cooldown until

### Rules

- Exposure increment is idempotent
- Duplicate session events are NOT double-counted
- Exposure limit is enforced
- Suspended items cannot be exposed
- Retired items cannot be exposed
- Exposure events do not contain answer keys

## Rotation Policy

### Configuration Parameters

| Parameter | Default | Description |
|---|---|---|
| max_total_exposures | 100 | Maximum lifetime exposures |
| rolling_window_days | 30 | Rolling window in days |
| min_cool_down_days | 7 | Minimum days between uses |
| min_pool_size | 5 | Minimum pool size |

### Eligibility Outputs

- `eligible` — Item can be used
- `temporarily_cooling_down` — In cool-down period
- `exposure_limit_reached` — Max exposures reached
- `suspended` — Item is suspended
- `retired` — Item is retired
- `insufficient_pool` — Pool too small

### Constraints

This layer does NOT assemble exam forms. It provides safe eligibility queries for a future exam assembly layer.
