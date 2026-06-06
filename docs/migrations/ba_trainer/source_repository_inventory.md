# Source Repository Inventory — bi-trainer-local

## Repository

| Field | Value |
|---|---|
| URL | https://github.com/solomonczyk/bi-trainer-local |
| Deployment | https://bi-trainer-local.vercel.app/ |
| Branch audited | master |
| Audit date | 2026-06-06 |

## Technology Stack

| Layer | Technology |
|---|---|
| Framework | React 19 (JSX, Vite 8) |
| Language | TypeScript ~6.0 |
| Styling | Tailwind CSS 4 |
| Routing | react-router-dom v7 (6 routes) |
| State | Zustand 5 + persist (localStorage) |
| Build | Vite 8 + tsc |
| Backend | Vercel serverless functions (@vercel/node) |
| Database Schema | PostgreSQL (@vercel/postgres) |
| DnD | @dnd-kit/core, sortable |

## Project Structure

```
bi-trainer-local/
├── api/                    # Vercel serverless API
│   ├── modules.ts          # GET /api/modules
│   ├── questions.ts        # GET /api/questions
│   ├── questions/[id].ts   # GET /api/questions/:id
│   └── progress/           # Progress endpoints
├── db/                     # Database layer
│   ├── index.ts            # Vercel Postgres pool
│   └── schema.sql          # DDL (questions, progress, user_state)
├── public/                 # Static assets
│   ├── exam-btn.png        # 1.3 MB
│   ├── favicon.svg
│   ├── icons.svg
│   └── logo.png            # 1.6 MB
├── src/
│   ├── App.tsx             # Root routes
│   ├── main.tsx            # Entry point
│   ├── index.css           # Tailwind + custom styles
│   ├── components/
│   │   ├── Layout.tsx           # App shell, nav, header
│   │   ├── ModuleCard.tsx       # Module grid card
│   │   ├── AnswerReveal.tsx     # Post-answer feedback
│   │   ├── ProgressRing.tsx     # SVG progress ring
│   │   ├── Timer.tsx            # Countdown timer
│   │   ├── GalaxyBackground.tsx # Animated background
│   │   └── questions/           # 16 question type components
│   │       ├── QuestionRenderer.tsx
│   │       ├── RadioQuestion.tsx
│   │       ├── CheckboxQuestion.tsx
│   │       ├── TextareaQuestion.tsx
│   │       ├── NumberInputQuestion.tsx
│   │       ├── FillInBlanksQuestion.tsx
│   │       ├── FlashCardQuestion.tsx
│   │       ├── DragAndDropQuestion.tsx
│   │       ├── MatchingQuestion.tsx
│   │       ├── BranchingDialogue.tsx
│   │       ├── LikertScaleQuestion.tsx
│   │       ├── AudioRecordQuestion.tsx
│   │       ├── TableInputQuestion.tsx
│   │       ├── InteractiveBoard.tsx
│   │       └── ClickOnImageQuestion.tsx
│   ├── pages/
│   │   ├── DashboardPage.tsx    # Home / stats / module grid
│   │   ├── DiagnosticsPage.tsx  # 8-question diagnostic
│   │   ├── ModulePage.tsx       # Question list per module
│   │   ├── QuestionPage.tsx     # Single question with answer
│   │   ├── ExamPage.tsx         # Timed 25-question exam
│   │   └── ReportPage.tsx       # Full progress report
│   ├── data/
│   │   ├── modules.json         # 12 module definitions
│   │   └── questions.json       # 211 questions (305 KB)
│   ├── store/
│   │   └── useProgressStore.ts  # Zustand + localStorage
│   ├── lib/
│   │   ├── api.ts               # Vercel API client
│   │   ├── keywordMatcher.ts    # Keyword-based text evaluation
│   │   └── scoring.ts           # XP calculation helpers
│   └── types/
│       └── question.ts          # TypeScript type definitions
├── vercel.json              # Rewrites to /api/* and index.html
├── vite.config.ts           # Vite configuration
├── tsconfig.json
├── package.json
└── tsconfig.app.json
```

## Routing

| Route | Page | Purpose |
|---|---|---|
| `/` | DashboardPage | Welcome, stats, module grid, CTAs |
| `/diagnostics` | DiagnosticsPage | 8-question entry-level test |
| `/modules/:moduleId` | ModulePage | Question list for a module |
| `/modules/:moduleId/:questionId` | QuestionPage | Single question + answer + feedback |
| `/exam` | ExamPage | Timed 25-question exam |
| `/report` | ReportPage | Progress, scores, module breakdown |

## Module Inventory

| ID | Title | Question Count | Level |
|---|---|---|---|
| module-0 | Входная диагностика | 8 (hardcoded) | all |
| module-1 | Скрининг-интервью (HR) | 25 | all |
| module-2 | Основы BA и стейкхолдеры | 25 | all |
| module-3 | Сбор и анализ требований | 25 | all |
| module-4 | Документирование и артефакты | 25 | all |
| module-5 | Моделирование процессов и данных | 20 | all |
| module-6 | Методологии (Agile, Waterfall, Hybrid) | 20 | all |
| module-7 | Метрики, оценка, приоритизация | 20 | all |
| module-8 | Коммуникация и конфликты | 20 | all |
| module-9 | Технические аспекты (SQL, API, прототипы) | 25 | all |
| module-10 | Реальные кейсы | 6 | all |
| module-11 | Финальный экзамен | 25 (dynamic selection) | all |

## Question Type Inventory

| Type | Count | % Total | Data Payload | Validation |
|---|---|---|---|---|
| radio | 98 | 46.4% | `{options, correct}` | Deterministic exact match |
| checkbox | 44 | 20.9% | `{options, correct[]}` | Deterministic set match |
| textarea | 44 | 20.9% | `{keywords[], minMatch}` | Keyword-based heuristic |
| fill-blanks | 13 | 6.2% | `{template, blanks[], correct[]}` | Deterministic exact match |
| matching | 5 | 2.4% | `{pairs[]}` | Manual (no stored correct) |
| number | 4 | 1.9% | `{correct}` | Deterministic numeric compare |
| flashcard | 3 | 1.4% | `{}` | Self-assessed (known/unknown) |

**Total questions in JSON:** 211  
**Total with diagnostics (hardcoded):** 219  
**Unused type components:** drag-sort, drag-group, drag-swimlane, interactive-board, click-image, branching-dialogue, table-input, audio, likert

## State Management

- **Library:** Zustand 5 with `persist` middleware
- **Storage key:** `ba-trainer-progress` (localStorage)
- **State shape:**
  ```typescript
  {
    answers: Record<string, AnswerRecord>     // questionId → status/answer/attempts
    diagnosticsResult: DiagnosticsResult|null // level, scores
    examResult: ExamResult|null              // score, total, timeSpent
    xp: number                              // total XP
    lastActive: number                      // timestamp
  }
  ```
- **No user isolation** — single browser, single user
- **No cross-device sync**
- **Vercel Postgres API exists but unused** in the deployed version based on code inspection (api.ts client exists but pages use local questions.json directly)

## Backend / API

| Endpoint | Method | Purpose | Status |
|---|---|---|---|
| `/api/modules` | GET | Return all modules | Implemented |
| `/api/questions` | GET | Filter questions (moduleId, level) | Implemented |
| `/api/questions/:id` | GET | Single question | Implemented |
| `/api/progress` | GET/POST | Progress CRUD | Schema exists |
| `/api/progress/stats` | GET | Module stats | Schema exists |
| `/api/diagnostics` | POST | Save diagnostics | Schema exists |
| `/api/exam` | POST | Save exam result | Schema exists |

## Authentication

**Not present.** No login, no registration, no sessions, no user identity.

## Assets

| File | Size | Type |
|---|---|---|
| `public/logo.png` | 1.6 MB | PNG |
| `public/exam-btn.png` | 1.3 MB | PNG |
| `public/favicon.svg` | 9.5 KB | SVG |
| `public/icons.svg` | 5.1 KB | SVG |

## Content Quality Notes

- **All 211 questions have explanations** — no missing explanation fields
- **8 questions lack data.correct** — all are textarea type (keyword-based evaluation) or matching type (no stored correct answer), which is expected
- **No duplicate question IDs** — verified
- **Level distribution:** Junior 85 (40%), Middle 84 (40%), Senior 42 (20%)
- **No unsafe HTML/Markdown detected** in titles or explanations
- **Content is in Russian** — localized to ru-RU, no en-US variant
- **Module 10 (Real Cases)** has only 6 questions — notably sparse

## Key Findings

1. **Standalone SPA** — no dependency on the main Trainer Platform
2. **Single-user** — no auth, localStorage-based progress
3. **7 of 16 defined types used** — many components are placeholder-only/no data
4. **Deterministic validation for closed types** — radio, checkbox, number, fill-blanks
5. **Heuristic validation for textarea** — keyword matching with simple morphology
6. **Backend API exists but is secondary** — the app works fully offline with local data
7. **Russian-only content** — no English localization
8. **Large assets** — logo.png and exam-btn.png are ~3 MB combined
