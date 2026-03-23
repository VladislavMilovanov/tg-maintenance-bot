.PHONY: install run lint format

install:
	uv venv
	uv pip install -e ".[dev]"

run:
	PYTHONPATH=src uv run python -m maintenance_bot

lint:
	uv run ruff check src/

format:
	uv run ruff format src/
