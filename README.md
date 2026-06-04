# Trainer Platform

Платформа самодостаточных профессиональных тренажеров (Trainer Platform) — MVP первого вертикального среза: Core Platform + QA Engineer Interview Trainer.

## Архитектура

```
Platform Core = общая инфраструктура и runtime
Domain = навигационная и продуктовая группировка (IT)
Trainer Product = самостоятельный тренажер (QA Engineer Interview Trainer)
Trainer Package = переносимый пакет тренажера
Scenario Runtime = механизм прохождения сценария
Evaluation Runtime = механизм оценки попытки по рубрике
Progress Engine = накопление прогресса пользователя
AI Gateway = единая точка доступа к LLM-провайдерам
```

## Стек

| Компонент | Технология |
|-----------|-----------|
| Frontend  | Next.js + TypeScript + Tailwind CSS |
| Backend   | FastAPI (Python) |
| Database  | PostgreSQL |
| AI Layer  | AI Gateway + Prompt Registry + rubric evaluation |
| Auth      | JWT-based |
| Tests     | pytest (backend), Vitest/React Testing Library (frontend) |

## Быстрый старт

### Предварительные требования

- Python 3.11+
- Node.js 18+
- Docker Desktop (для PostgreSQL)
- Make (опционально)

### 1. Запуск PostgreSQL

```bash
docker compose -f docker-compose.local.yml up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env    # настроить при необходимости
alembic upgrade head
python scripts/seed_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
```

### 4. Открыть в браузере

```
http://localhost:3000
```

## Команды

```bash
# Backend тесты
cd backend && python -m pytest

# Frontend сборка
cd frontend && npm run build

# Миграции
cd backend && alembic upgrade head

# Валидация пакета
cd backend && python scripts/validate_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer

# Сидирование
cd backend && python scripts/seed_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer

# Экспорт OpenAPI
cd backend && python scripts/export_openapi.py
```

## Структура проекта

```
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/          # config, logging, errors, security
│   │   ├── db/            # session, base, migrations
│   │   ├── modules/       # auth, users, domains, trainers, scenarios, runtime, evaluations, progress, analytics, admin
│   │   └── ai_gateway/    # service, adapters, prompts, schemas, validators
│   ├── scripts/           # seed, validate, export
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # UI, layout, trainer, scenario, evaluation, progress
│   │   ├── features/      # auth, trainers, runtime, evaluations, progress, analytics
│   │   └── lib/           # api client, i18n, errors
│   └── tests/
├── trainer_packages/
│   └── qa_engineer_interview_trainer/  # canonical trainer package
├── docs/
│   ├── implementation/
│   ├── proofs/
│   ├── release/
│   └── known_issues/
├── docker-compose.local.yml
└── .env.example
```

## MVP User Journey

1. Landing → Register/Login
2. Select locale (ru-RU / en-US) 
3. Open Domain Catalog → IT
4. Open QA Engineer Interview Trainer
5. Enroll
6. Open scenario list → Start Bug Report Structure
7. Submit text answer
8. System saves attempt → AI evaluates via rubric
9. See score, evidence, weak points, critical errors, recommendation
10. Retry or continue to next scenario

## Лицензия

MIT
