.PHONY: dev db.up db.migrate api web worker test lint typecheck seed

DEV ?= docker compose

# Run full stack in development mode
dev:
	$(DEV) up --build

# Start database and redis, then apply migrations
db.up:
	$(DEV) up -d db redis
	poetry run alembic upgrade head

# Create a new migration and apply it
# Usage: make db.migrate m="create users table"
db.migrate:
	poetry run alembic revision --autogenerate -m "$(m)"
	poetry run alembic upgrade head

# Run API service only
api:
	$(DEV) up api

# Run web frontend only
web:
	$(DEV) up web

# Run Celery workers only
worker:
	$(DEV) up worker

# Execute backend and frontend test suites
test:
	$(DEV) exec api pytest -q
	npm --prefix apps/web run test -- --run

# Lint Python and JS/TS codebases
lint:
	$(DEV) exec api ruff check .
	$(DEV) exec api black --check .
	npm --prefix apps/web run lint

# Static type checks for Python and TypeScript
typecheck:
	$(DEV) exec api mypy apps/api
	npm --prefix apps/web run typecheck

# Seed database with baseline data
seed:
	$(DEV) exec api python infra/db/seed.py
