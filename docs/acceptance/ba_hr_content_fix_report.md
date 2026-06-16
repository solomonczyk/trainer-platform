# BA HR Module Content Quality Fix Report

## Summary

All 20 questions in the BA HR screening module (`ba_hr_screening`) had
semantically invalid option/title pairs. The options for each question
did not answer the question being asked.

## Root Cause

The `activities.json` stored options that were shifted or mismatched
relative to their question titles. Explanations and titles were correctly
paired, but the options arrays and `correct` values were wrong for every
question (Q1–Q20).

## Fix Applied

### activities.json
- Replaced options arrays for all 20 HR activities with text that
  correctly answers each question.
- Updated `correct` field to match the new correct option.
- Each question now has 4 options where exactly 1 (single_choice) or
  2–3 (multiple_choice) are correct.

### Locale files (generated_activity_titles_*.json)
- Added 80 `ba_hr_q{N}_opt_{M}` keys (20 questions × 4 options) to
  both ru-RU and en-US generated locale files.
- Russian option text matches the activities.json payload.
- English option text provides localized display when locale is en-US.

### Frontend (ActivityRenderer)
- `SingleChoiceActivity` and `MultipleChoiceActivity` accept optional
  `activityId` prop.
- When `activityId` is provided, option text is looked up via `t()`
  using key pattern `{base_id}_opt_{index+1}`.
- Falls back to raw payload text when locale key is not found.
- `ActivityRenderer`, `ModuleQuizEngine`, and `ActivityRunnerPage`
  pass `activityId` through.

## Per-Question Audit

| Q  | Title (Russian) | Issue | Fix |
|----|-----------------|-------|-----|
| 1  | Какие основные разделы должны быть в резюме бизнес-аналитика? | Options were screening stages | Options now: resume sections (experience, hobbies, references, photo). Correct: experience with projects. |
| 2  | Какой формат резюме предпочтителен для IT-компаний? | Options were job roles | Options now: PDF, DOCX, HTML, TXT. Correct: PDF. |
| 3  | Как лучше всего презентовать свой опыт перехода в BA? | Options were roles | Options now: presentation approaches. Correct: structured story. |
| 4  | Какие качества наиболее важны для BA? | Options were interview types | Options now: BA qualities (analytical thinking, Python, Figma, Linux). Correct: analytical thinking. |
| 5  | Что такое скрининг резюме и как к нему подготовиться? | Options were HR eval criteria | Options now: screening definitions. Correct: quick recruiter check. |
| 6  | Как правильно отвечать на вопрос о зарплатных ожиданиях? | Options were STAR frameworks | Options now: salary answer approaches. Correct: market-range. |
| 7  | Почему вы хотите работать именно BA? | Options were SWOT | Options now: motivation types. Correct: business-IT interest. |
| 8  | Что вы знаете о нашей компании? | Options were document types | Options now: company research areas. Correct: products/culture. |
| 9  | Опишите ваш карьерный путь и планы на 3 года. | Options were skills | Options now: structure approaches. Correct: chronological story. |
| 10 | Как вы справляетесь со стрессом и дедлайнами? | Options were BA activities | Options now: stress management. Correct: prioritization. |
| 11 | Какую зарплату вы ожидаете на Junior BA? | Options were speech styles | Options now: salary ranges. Correct: 60-100k RUB range. |
| 12 | Как вы готовились к собеседованию на BA? | Options were employment types | Options now: preparation methods. Correct: BABOK+courses. |
| 13 | Какие сертификации по BA вы прошли? | Options were skill areas | Options now: cert types. Correct: IIBA (ECBA/CCBA/CBAP). |
| 14 | Расскажите о самом значимом достижении. | Options were BA activities | Options now: achievement description. Correct: STAR method. |
| 15 | Какие факторы влияют на решение принять оффер? | Options were qualities | Options now: decision factors. Correct: tasks+salary+growth. |
| 16 | Какие вопросы задать работодателю? | Options were interview stages | Options now: good questions. Correct: methodology+process+tools. |
| 17 | Какие навыки BA развивать в первую очередь? | Options partially matched | Options now: BA skills. Correct: elicitation+stories+stakeholders. |
| 18 | Как объяснить gap в резюме? | Options were skills | Options now: gap explanations. Correct: honest+development. |
| 19 | Какую роль в команде предпочитаете? | Options were skills | Options now: role types. Correct: bridge+analyst. |
| 20 | Как узнали о вакансии и почему откликнулись? | Options were qualities | Options now: discovery methods. Correct: search+interest. |

## Verification

- TypeScript build: ✅ clean
- All 80 new locale keys added to ru-RU and en-US
- Backend activities.json: all 20 Qs fixed
- Re-seed required: `python scripts/seed_ba_trainer.py`
- Browser check: verify first 5 questions in ru-RU and en-US
