.PHONY: install run run-backend backend-run lint lint-backend backend-lint format test test-backend backend-test

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
