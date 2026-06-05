# 18.6 Payments & Pricing Market Strategy

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define payment and pricing strategy for future B2C/B2B launch across markets.

---

## Current rule

Payments are not part of the current MVP launch.

Before enabling payments:

```json
{
  "payment_provider_selected": false,
  "tax_vat_review_done": false,
  "refund_policy_ready": false,
  "checkout_security_review_done": false,
  "production_accepted": false
}
```

---

## Pricing models

### B2C

Possible models:

- free beta;
- one-time trainer pack purchase;
- monthly subscription;
- 7-day / 30-day interview prep pass;
- pay-per-simulation pack.

Recommended early model:

```json
{
  "model": "controlled beta → low-cost paid pilot",
  "reason": "validate willingness to pay before complex billing"
}
```

### B2B

Possible models:

- per seat per month;
- per cohort;
- per organization package;
- white-label trainer pack;
- expert/academy partnership.

Recommended B2B pilot:

```json
{
  "model": "fixed pilot fee for 1 cohort",
  "duration": "4-8 weeks",
  "includes": ["trainer access", "analytics report", "feedback summary"]
}
```

---

## Market pricing worksheet

For every market:

```json
{
  "market_id": "",
  "currency": "",
  "b2c_price_min": "",
  "b2c_price_target": "",
  "b2c_price_max": "",
  "b2b_pilot_price": "",
  "payment_provider_options": [],
  "tax_vat_review_required": true,
  "refund_policy_required": true,
  "local_affordability_notes": ""
}
```

---

## Payment provider planning

Possible providers to evaluate:

- Stripe;
- Paddle;
- Lemon Squeezy;
- local bank transfer for B2B;
- invoices for organizations.

Selection criteria:

- supported countries;
- supported currencies;
- tax/VAT handling;
- subscription support;
- refund support;
- webhook reliability;
- compliance burden;
- payout availability.

---

## Engineering requirements before payment

Required modules:

- plans;
- subscriptions;
- invoices;
- payment provider abstraction;
- webhook handling;
- entitlement system;
- refund state;
- billing audit log.

---

## Forbidden before payment launch

Do not:

- hardcode one payment provider into core domain logic;
- store card data directly;
- accept payments without refund policy;
- accept payments without Terms/Privacy/AI disclaimer;
- enable paid public launch without tax/VAT review;
- mix staging and production payment credentials;
- use production payment keys in development.

---

## Payment acceptance gate

```json
{
  "provider_selected": false,
  "provider_test_mode_passed": false,
  "webhook_tests_passed": false,
  "entitlement_tests_passed": false,
  "refund_policy_ready": false,
  "tax_vat_review_done": false,
  "no_card_data_stored": true,
  "payment_launch_allowed": false
}
```
