.PHONY: install run run-backend backend-run lint lint-backend backend-lint format test test-backend backend-test test-backend-integration backend-test-integration db-up db-down db-reset db-migrate db-downgrade db-import db-check db-psql web-install web-dev web-build web-lint

COMPOSE = docker compose
ALEMBIC = UV_CACHE_DIR=.uv-cache PYTHONPATH=backend/src uv run --no-sync alembic
DB_TOOL = UV_CACHE_DIR=.uv-cache PYTHONPATH=backend/src uv run --no-sync python -m

install:
	uv venv
	uv pip install -e ".[dev]"

run:
	PYTHONPATH=src uv run --no-sync python -m maintenance_bot

run-backend:
	PYTHONPATH=backend/src uv run --no-sync python -m maintenance_backend

backend-run: run-backend

lint:
	uv run --no-sync ruff check src/ tests/

lint-backend:
	uv run --no-sync ruff check backend/src/ backend/tests/

backend-lint: lint-backend

format:
	uv run --no-sync ruff format src/ tests/ backend/src/ backend/tests/

test:
	PYTHONPATH=src uv run --no-sync pytest tests/

test-backend:
	PYTHONPATH=backend/src uv run --no-sync pytest backend/tests/

backend-test: test-backend

test-backend-integration:
	BACKEND_DATABASE_URL=$${BACKEND_DATABASE_URL:-postgresql://postgres:postgres@localhost:55433/tg_maintenance} PYTHONPATH=backend/src uv run --no-sync pytest backend/tests_integration/

backend-test-integration: test-backend-integration

db-up:
	$(COMPOSE) up -d postgres

db-down:
	$(COMPOSE) down

db-reset:
	$(COMPOSE) down -v
	$(COMPOSE) up -d postgres

db-migrate:
	$(ALEMBIC) upgrade head

db-downgrade:
	$(ALEMBIC) downgrade -1

db-import:
	$(DB_TOOL) maintenance_backend.db_import

db-check:
	$(DB_TOOL) maintenance_backend.db_check

db-psql:
	$(COMPOSE) exec postgres psql -U postgres -d tg_maintenance

# ── Frontend ──────────────────────────────────────────────
web-install:
	cd frontend && pnpm install

web-dev:
	cd frontend && pnpm dev

web-build:
	cd frontend && pnpm build

web-lint:
	cd frontend && pnpm lint
