# Итерация 0: Backend bootstrap

## Итог

Итерация завершена как подготовительный документарный слой перед `Backend foundation`.

## Что реализовано

- зафиксирован backend-стек MVP: Python 3.12+, `uv`, FastAPI, `pydantic-settings`, `pytest` + `httpx`/`TestClient`, `ruff`, `make`;
- создан `ADR-002` с описанием стека и границ backend-first ядра;
- создан `.cursor/rules/conventions.mdc` с правилами thin-clients архитектуры и зарезервированными backend-командами;
- `docs/plan.md` дополнен отдельной итерацией 0;
- `docs/tasks/tasklist-backend.md` явно связывает задачу 01 с итерацией 0.

## Ограничения

- backend-сервис и каталог `backend/` еще не реализованы;
- команды `make run-backend`, `make test-backend`, `make lint-backend` зафиксированы нормативно и должны появиться в задаче 03;
- API-контракты и реализация endpoint'ов остаются в итерации 1.
