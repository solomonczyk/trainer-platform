# VPS Browser Acceptance — 009

## Environment

- **Staging URL**: https://trainer.152.53.227.37.nip.io
- **Test User**: test@trainer.com / Test123!
- **Date**: 2026-06-09

## QA Flow (ru-RU)

| Step | Action | Result |
|------|--------|--------|
| 1 | Open home page | ✅ Russian locale, "Trainer Platform" branding |
| 2 | Login | ✅ Token-based auth works |
| 3 | Domains page | ✅ IT domain with 2 trainers visible |
| 4 | QA Trainer | ✅ "QA Engineer Interview Trainer" loads correctly |
| 5 | Scenario list | ✅ 5 QA scenarios visible in Russian |
| 6 | Scenario detail | ✅ "Структура баг-репорта" renders without errors |
| 7 | Start scenario | ✅ Session created via API |
| 8 | Submit answer | ✅ Answer saved successfully |
| 9 | Complete session | ✅ Session marked completed |
| 10 | DeepSeek evaluation | ✅ Score 85/100, passed=true |

## BA Flow (en-US)

| Step | Action | Result |
|------|--------|--------|
| 1 | Switch locale to en-US | ✅ All labels in English |
| 2 | BA Trainer | ✅ "Business Analyst Interview Trainer" loads |
| 3 | Scenario list | ✅ 6 BA scenarios visible in English |
| 4 | Start scenario | ✅ Session created |
| 5 | Submit + evaluate | ✅ Score 38/100 via DeepSeek |

## React Error #31

**Status**: ABSENT — verified on all pages (home, domains, trainer detail,
scenario list, scenario detail, runtime). No `target_skills` rendering issues.

## Raw i18n Keys

**Status**: ABSENT — all labels properly localized in both ru-RU and en-US.

## Progress Persistence

| Check | Result |
|-------|--------|
| QA trainer progress | ✅ 1 attempt, score 85, completed: 1 |
| Refresh persistence | ✅ Data persists after page reload |
| Readiness status | ✅ "developing" |

## Screenshots

- `docs/proofs/vps_home.png`
- `docs/proofs/vps_login_filled.png`
- `docs/proofs/vps_domains.png`
- `docs/proofs/vps_qa_trainer_detail.png`
- `docs/proofs/vps_qa_scenario_detail.png`
- `docs/proofs/vps_qa_evaluation_done.png`
- `docs/proofs/vps_ba_scenarios_en.png`
