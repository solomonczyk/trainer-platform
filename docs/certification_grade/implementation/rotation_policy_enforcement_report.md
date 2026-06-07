# Rotation Policy Enforcement Report

**Layer:** TRAINER-PLATFORM-DYNAMIC-ITEM-BANK-RUNTIME-AND-GOVERNANCE-VERTICAL-LAYER-002
**Date:** 2026-06-07

## Policy Inputs Enforced

| Input | Status | Description |
|-------|--------|-------------|
| Locale | ✅ ENFORCED | `allowed_locales` in policy blocks items with non-matching locale |
| Domain balance | ✅ ENFORCED | `domain_balance_quotas` limits items per domain |
| Competency balance | ✅ ENFORCED | `competency_balance_quotas` limits items per competency |
| Difficulty balance | ✅ ENFORCED | `difficulty_balance_ratios` enforces mix ratios |
| Item family diversity | ✅ ENFORCED | `max_items_per_family` prevents family overuse |
| Recent-use exclusion | ✅ ENFORCED | `recent_use_window_days` excludes recently used items |
| Exposure threshold | ✅ ENFORCED | `max_total_exposures` / rolling window limits |
| Cool-down period | ✅ ENFORCED | `cooldown_until` blocks items in cool-down |
| Suspended/retired | ✅ ENFORCED | Blocked at service entry |
| Insufficient pool | ✅ ENFORCED | `min_pool_size` check on exam-eligible pool |

## Output Structure

Each eligibility check returns:
- `item_id`, `policy_id`, `policy_version`
- `eligible` boolean
- `cooling_down`, `exposure_limit_reached`, `wrong_locale`, etc.
- `decision_code`: "eligible", "blocked", "suspended", "retired", "item_not_found"
- `decision_reasons`: human-readable reasons list
- `evaluated_inputs`: policy context snapshot
- `timestamp`: evaluation timestamp

## Test Results

- ✅ 7 positive tests (policy match → eligible)
- ✅ 7 negative tests (policy mismatch → blocked with reasons)
- ✅ 2 additional verification tests (suspended, retired, decision reasons detail)

All 16 tests pass.
