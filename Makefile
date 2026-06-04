.PHONY: help backend-setup backend-run backend-test backend-migrate backend-seed backend-validate backend-openapi frontend-setup frontend-run frontend-build frontend-test db-up db-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

db-up: ## Start PostgreSQL
	docker compose -f docker-compose.local.yml up -d

db-down: ## Stop PostgreSQL
	docker compose -f docker-compose.local.yml down

backend-setup: ## Setup backend Python venv and install deps
	cd backend && python -m venv .venest && .venv/Scripts/pip install -r requirements.txt

backend-migrate: ## Run Alembic migrations
	cd backend && .venv/Scripts/alembic upgrade head

backend-seed: ## Seed trainer packages
	cd backend && python scripts/seed_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer

backend-validate: ## Validate trainer package
	cd backend && python scripts/validate_trainer_package.py ../trainer_packages/qa_engineer_interview_trainer

backend-run: ## Start backend dev server
	cd backend && .venv/Scripts/uvicorn app.main:app --reload --port 8000

backend-test: ## Run backend tests
	cd backend && python -m pytest -v

backend-openapi: ## Export OpenAPI schema
	cd backend && python scripts/export_openapi.py

backend-rollback: ## Rollback last migration
	cd backend && .venv/Scripts/alembic downgrade -1

frontend-setup: ## Install frontend deps
	cd frontend && npm install

frontend-run: ## Start frontend dev server
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	cd frontend && npm run build

frontend-test: ## Run frontend tests
	cd frontend && npm test

frontend-lint: ## Lint frontend
	cd frontend && npm run lint

frontend-typecheck: ## TypeScript typecheck
	cd frontend && npm run typecheck

e2e-smoke: ## Run E2E smoke test
	cd backend && python tests/e2e/test_smoke.py

proof: ## Generate proof JSON
	python scripts/generate_proof.py

all: db-up backend-setup backend-migrate backend-seed frontend-setup ## Full setup
	@echo "Setup complete. Run 'make backend-run' and 'make frontend-run' in separate terminals."
