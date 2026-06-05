# 18.8 Country / Market Launch Acceptance Gates

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define objective gates before launching Trainer Platform in a new market.

---

## Gate philosophy

A market launch is not accepted only because pages load.

A market launch is accepted when:

```text
product + localization + compliance + payments + QA + analytics + support are ready for that market level
```

---

# Gate 1 — Market Pack Gate

Accepted when:

```json
{
  "market_playbook_created": true,
  "target_users_defined": true,
  "first_trainer_selected": true,
  "pricing_hypothesis_defined": true,
  "launch_channels_defined": true,
  "market_risks_documented": true
}
```

Rejected when:

- target audience is vague;
- first trainer is not selected;
- market-specific assumptions are not documented.

---

# Gate 2 — Locale Pack Gate

Accepted when:

```json
{
  "ui_locale_complete": true,
  "scenario_locale_complete": true,
  "rubric_locale_complete": true,
  "human_localization_review_done": true,
  "mixed_language_errors_absent": true
}
```

Rejected when:

- only raw machine translation exists;
- scenario examples do not match local context;
- AI feedback uses wrong tone or language.

---

# Gate 3 — Trainer Pack Gate

Accepted when:

```json
{
  "trainer_pack_valid": true,
  "scenario_pack_valid": true,
  "rubric_pack_valid": true,
  "golden_answer_set_valid": true,
  "critical_errors_defined": true,
  "ai_behavior_contract_valid": true
}
```

---

# Gate 4 — Compliance / Privacy Gate

Accepted when:

```json
{
  "privacy_policy_ready": true,
  "terms_ready": true,
  "ai_disclaimer_ready": true,
  "data_retention_policy_ready": true,
  "delete_export_process_ready": true,
  "cookie_analytics_policy_ready": true,
  "legal_review_done_or_formal_beta_exception": true
}
```

---

# Gate 5 — Payment Gate

Required only for paid launch.

Accepted when:

```json
{
  "payment_provider_ready": true,
  "test_payments_passed": true,
  "refund_policy_ready": true,
  "tax_vat_review_done": true,
  "no_card_data_stored": true,
  "webhook_tests_passed": true
}
```

---

# Gate 6 — QA / AI Evaluation Gate

Accepted when:

```json
{
  "golden_answers_pass": true,
  "bad_answers_fail": true,
  "prompt_injection_blocked": true,
  "empty_answers_handled": true,
  "critical_errors_detected": true,
  "score_evidence_present": true,
  "no_invented_feedback": true
}
```

---

# Gate 7 — External Staging Gate

Accepted when:

```json
{
  "external_frontend_reachable": true,
  "external_backend_reachable": true,
  "database_ready": true,
  "migrations_applied": true,
  "trainer_seeded": true,
  "smoke_passed": true,
  "monitoring_ready": true
}
```

---

# Gate 8 — Launch Decision Gate

```json
{
  "market_id": "",
  "launch_type": "free_beta|paid_beta|b2b_pilot|production",
  "all_required_gates_passed": false,
  "production_accepted": false,
  "release_allowed": false,
  "launch_allowed": false,
  "accepted_by": "",
  "blockers": []
}
```

---

## Launch verdict rules

### ACCEPTED

Only if all required gates for that launch type pass.

### ACCEPTED_WITH_BLOCKERS

Allowed for internal beta if blockers are known and safe.

### REJECTED

If privacy/payment/AI safety/secret leakage/production gate is violated.

### NEEDS_FIX

If gate evidence is incomplete.
