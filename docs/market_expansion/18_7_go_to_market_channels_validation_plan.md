# 18.7 Go-To-Market Channels & Validation Plan

**Project:** Trainer Platform  
**Version:** 1.0  
**Date:** 2026-06-05

---

## Goal

Define how to validate demand before scaling development.

---

## Main GTM principle

Do not scale engineering before proving that users complete simulations and value the feedback.

---

## Validation stages

### Stage 1 — Manual beta

Goal:

- 5–10 users;
- observe real behavior;
- collect feedback;
- find confusion points.

Success criteria:

```json
{
  "users_invited": 10,
  "users_completed_simulation": ">=5",
  "critical_bugs": 0,
  "ai_feedback_understood": true,
  "users_want_retry": true
}
```

### Stage 2 — Controlled public beta

Goal:

- 50–100 users;
- validate analytics;
- test conversion to waitlist or paid interest.

Success criteria:

```json
{
  "signups": ">=50",
  "simulation_completion_rate": ">=40%",
  "ai_eval_success_rate": ">=95%",
  "negative_feedback_rate": "<=15%",
  "willingness_to_pay_signal": true
}
```

### Stage 3 — B2B pilot

Goal:

- one organization or course group;
- group analytics;
- cohort report.

Success criteria:

```json
{
  "organization_signed": true,
  "participants": ">=10",
  "completion_rate": ">=50%",
  "manager_report_useful": true,
  "renewal_interest": true
}
```

---

## Channel list

### B2C

- Telegram communities;
- LinkedIn posts;
- Reddit/Discord communities where appropriate;
- job-seeker groups;
- IT bootcamp alumni;
- YouTube/short video demos;
- landing page SEO;
- partner newsletters.

### B2B

- IT schools;
- QA bootcamps;
- language schools;
- HR/recruiting agencies;
- corporate L&D;
- career centers;
- local tech communities.

---

## Validation assets

Required before outreach:

- short landing page;
- product demo video/GIF;
- example AI feedback screenshot;
- beta invitation text;
- feedback form;
- issue registry;
- FAQ;
- privacy/AI disclaimer.

---

## Metrics to track

```json
{
  "landing_opened": true,
  "signup_started": true,
  "signup_completed": true,
  "trainer_opened": true,
  "scenario_started": true,
  "answer_submitted": true,
  "evaluation_completed": true,
  "result_viewed": true,
  "retry_started": true,
  "feedback_submitted": true
}
```

---

## Do not do yet

Do not:

- buy paid ads before organic/manual validation;
- promise job results;
- launch too many trainers;
- start complex marketplace;
- overbuild B2B dashboards before one pilot confirms need.

---

## Output

Every GTM experiment must produce:

```json
{
  "experiment_id": "",
  "market_id": "",
  "target_segment": "",
  "channel": "",
  "users_reached": 0,
  "signups": 0,
  "completed_simulations": 0,
  "feedback_summary": "",
  "decision": "continue|iterate|stop"
}
```
