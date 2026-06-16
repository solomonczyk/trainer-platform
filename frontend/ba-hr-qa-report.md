# BA HR Screening — Content QA Report

**Date:** 2026-06-16
**Module:** ba_hr_screening (HR Screening & Self-Presentation)
**Total Questions:** 20
**Audit Scope:** question type, options, correct answer(s), explanation alignment, ru-RU/en-US semantic equivalence

---

## Q1 — Résumé Sections

| Field | Before | After |
|-------|--------|-------|
| **Question** | Какие основные разделы должны быть в резюме бизнес-аналитика? | _unchanged_ |
| **Type** | `single_choice` ❌ | `multiple_choice` ✅ |
| **Options** | 4 fragment options (Опыт работы, Хобби, Рекомендации, Фотография) | 8 individual section options (5 correct, 3 distractors) |
| **Correct** | "Опыт работы..." (1 option) | 5 options: Контактная информация + Summary, Опыт работы, Ключевые навыки, Образование + сертификации, Языки + курсы |
| **Explanation** | Full section set listed | _unchanged — matches new correct options_ |
| **Verdict** | ❌ INVALID — single_choice with 1 fragment as correct, but explanation lists multiple sections | ✅ FIXED |

---

## Q2 — Preferred Resume Format

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | PDF, DOCX (Word), HTML, TXT |
| **Correct** | "PDF" ✅ |
| **Explanation** | PDF preferred, ATS-compatible .docx also acceptable |
| **Verdict** | ✅ VALID |

---

## Q3 — Presenting Career Transition

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Structured story (past→transition→skills), Current duties only, All courses, Tech skills |
| **Correct** | "Структурированный рассказ: прошлый опыт → переход → текущие компетенции" ✅ |
| **Explanation** | Matches structured story approach |
| **Verdict** | ✅ VALID |

---

## Q4 — Key Qualities for BA

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Analytical thinking, Python, Photoshop/Figma, Linux admin |
| **Correct** | "Аналитическое мышление и внимание к деталям" ✅ |
| **Explanation** | Lists analytical thinking, communication, attention to detail, systems thinking |
| **Verdict** | ✅ VALID |

---

## Q5 — Resume Screening

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Resume screening, Deep technical interview, Test task, Soft skills assessment |
| **Correct** | "Быстрая проверка резюме рекрутером на соответствие базовым требованиям" ✅ |
| **Explanation** | Matches resume screening definition |
| **Verdict** | ✅ VALID |

---

## Q6 — Salary Expectations

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Name range, Name max, Refuse, Name min |
| **Correct** | "Назвать диапазон, ориентируясь на рынок, а не фиксированную сумму" ✅ |
| **Explanation** | Matches market-range approach |
| **Verdict** | ✅ VALID |

---

## Q7 — Motivation for BA Role

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Interest in biz analysis, High salary, Remote work, Short hours |
| **Correct** | "Интерес к решению бизнес-задач и работе на стыке бизнеса и IT" ✅ |
| **Explanation** | Matches intrinsic motivation for BA role |
| **Verdict** | ✅ VALID |

---

## Q8 — Company Research

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Products/services/culture, Internal dept structure, Leadership personal life, Financial reports |
| **Correct** | "Продукты, услуги, отрасль, новости и корпоративную культуру компании" ✅ |
| **Explanation** | Matches what to research before interview |
| **Verdict** | ✅ VALID |

---

## Q9 — Career Path

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Structured (education→current→future), Current duties only, All jobs no chronology, Only future plans |
| **Correct** | "Структурированно: от образования и первого опыта к текущей роли и планам" ✅ |
| **Explanation** | Matches structured career narrative |
| **Verdict** | ✅ VALID |

---

## Q10 — Stress & Deadlines

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | Prioritization/decomposition/breaks, 12h days, Ignore deadlines, Ask for help each step |
| **Correct** | "Приоритизация задач, декомпозиция, регулярные перерывы и тайм-менеджмент" ✅ |
| **Explanation** | Matches healthy coping strategies |
| **Verdict** | ✅ VALID |

---

## Q11 — Junior BA Salary Range

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | 60–100k RUB, 200k+ RUB, Minimal salary, Not important |
| **Correct** | "60,000 – 100,000 рублей в зависимости от компании и задач" ✅ |
| **Explanation** | Matches market range for Junior BA |
| **Verdict** | ✅ VALID |

---

## Q12 — Interview Preparation

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | BABOK/courses/practice, YouTube only, Theory only, Talk to friends |
| **Correct** | "Изучение BABOK, профильные курсы, практика написания use cases и user stories" ✅ |
| **Explanation** | Matches thorough preparation |
| **Verdict** | ✅ VALID |

---

## Q13 — BA Certifications

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | IIBA certs (ECBA/CCBA/CBAP), PMP/CSM/SAFe, CCNA/MCSA/AWS, TEFL/CMA/CFA |
| **Correct** | "ECBA, CCBA, CBAP — сертификации IIBA" ✅ |
| **Explanation** | Matches IIBA certification track |
| **Verdict** | ✅ VALID |

---

## Q14 — Significant Achievement (STAR)

| Field | Value |
|-------|-------|
| **Type** | `single_choice` ✅ |
| **Options** | STAR method with numbers, General description, Salary talk, Difficulties without results |
| **Correct** | "Кейс использования метода STAR для описания конкретного результата с цифрами" ✅ |
| **Explanation** | Matches STAR method (Situation, Task, Action, Result) |
| **Verdict** | ✅ VALID |

---

## Q15 — Job Offer Factors

| Field | Value |
|-------|-------|
| **Type** | `multiple_choice` ✅ |
| **Options** | Interesting tasks, High salary, Convenient office location, Professional growth |
| **Correct** | [Interesting tasks, High salary, Professional growth] ✅ (excludes "Convenient office location") |
| **Explanation** | Lists interesting tasks, growth, culture, salary, team — matches correct options |
| **Verdict** | ✅ VALID |

---

## Q16 — Questions for Employer

| Field | Value |
|-------|-------|
| **Type** | `multiple_choice` ✅ |
| **Options** | Methodology, Requirements process, Lunch break length, Tools |
| **Correct** | [Methodology, Requirements process, Tools] ✅ |
| **Explanation** | Lists methodology, requirements process, tools, onboarding, growth — excludes "lunch break" |
| **Verdict** | ✅ VALID |

---

## Q17 — Skills to Develop

| Field | Value |
|-------|-------|
| **Type** | `multiple_choice` ✅ |
| **Options** | Elicitation techniques, User stories, Deep C++ knowledge, Working with requirements |
| **Correct** | [Elicitation, User stories, Working with requirements] ✅ |
| **Explanation** | Matches BA skill focus (excludes C++) |
| **Verdict** | ✅ VALID |

---

## Q18 — Explaining Career Gap

| Field | Value |
|-------|-------|
| **Type** | `multiple_choice` ✅ |
| **Options** | Honestly explain, Hide dates, Lie, Emphasize development |
| **Correct** | [Honestly explain, Emphasize development] ✅ |
| **Explanation** | Matches honest + constructive approach |
| **Verdict** | ✅ VALID |

---

## Q19 — Preferred Role

| Field | Value |
|-------|-------|
| **Type** | `multiple_choice` ✅ |
| **Options** | Bridge between business & dev, Task executor, Tech lead, Analyst formalizing needs |
| **Correct** | [Bridge between business & dev, Analyst formalizing needs] ✅ |
| **Explanation** | Matches BA role description |
| **Verdict** | ✅ VALID |

---

## Q20 — How You Found the Vacancy

| Field | Value |
|-------|-------|
| **Type** | `multiple_choice` ✅ |
| **Options** | Targeted search (LinkedIn), Saw randomly, Apply to all, Interest in company/product |
| **Correct** | [Targeted search, Interest in company/product] ✅ |
| **Explanation** | Matches purposeful job search narrative |
| **Verdict** | ✅ VALID |

---

## Summary

| Metric | Value |
|--------|-------|
| Total HR questions | 20 |
| Questions with correct type-answer alignment | 20 (100%) after Q1 fix |
| Questions needing fix | 1 (Q1) |
| Fix applied | Q1: single_choice → multiple_choice, options redesigned |
| Locale labels updated | "ru-RU" → "RU", "en-US" → "US" |
| ru-RU / en-US semantic alignment | ✅ All explanations match between locales |
| Production accepted | ❌ (pending browser verification) |
| Release allowed | ❌ (pending browser verification) |
