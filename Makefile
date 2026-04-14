.PHONY: install run run-backend backend-run lint lint-backend backend-lint format test test-backend backend-test test-backend-integration backend-test-integration db-up db-down db-reset db-migrate db-downgrade db-import db-check db-psql stack-build stack-build-bot stack-pull stack-up stack-up-bot stack-up-registry stack-up-registry-bot stack-down stack-clean stack-ps stack-logs stack-logs-% stack-health web-install web-dev web-build web-lint

COMPOSE = docker compose
REGISTRY_COMPOSE = docker compose -f compose.yaml -f devops/compose/compose.registry.yaml
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

stack-build:
	$(COMPOSE) build backend frontend

stack-build-bot:
	$(COMPOSE) build backend frontend bot

stack-pull:
	$(REGISTRY_COMPOSE) pull backend frontend

stack-up:
	$(COMPOSE) up -d postgres backend frontend

stack-up-bot:
	COMPOSE_PROFILES=bot $(COMPOSE) up -d postgres backend frontend bot

stack-up-registry:
	$(REGISTRY_COMPOSE) up -d postgres backend frontend

stack-up-registry-bot:
	COMPOSE_PROFILES=bot $(REGISTRY_COMPOSE) up -d postgres backend frontend bot

stack-down:
	$(COMPOSE) down

stack-clean:
	$(COMPOSE) down -v --remove-orphans

stack-ps:
	$(COMPOSE) ps

stack-logs:
	$(COMPOSE) logs -f --tail=200

stack-health:
	curl -fsS http://127.0.0.1:$${BACKEND_PORT:-8000}/health

stack-logs-%:
	$(COMPOSE) logs -f --tail=200 $*

# ── Frontend ──────────────────────────────────────────────
web-install:
	cd frontend && pnpm install

web-dev:
	cd frontend && pnpm dev

web-build:
	cd frontend && pnpm build

web-lint:
	cd frontend && pnpm lint
