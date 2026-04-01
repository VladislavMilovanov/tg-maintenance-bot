# Задача 03: Каркас backend-сервиса

## Итог

Задача завершена в рамках итерации 1.

## Что сделано

- создан отдельный backend-сервис в `backend/` с `src`-layout и пакетом `maintenance_backend`;
- добавлены FastAPI app factory, env-конфиг, runtime entrypoint и базовый lifecycle приложения;
- введён versioned router `api/v1`, вынесены transport-схемы в `schemas/`, сервисы в `services/`, а dependency providers переведены на `app.state`;
- реализован `GET /health` и базовый тестовый каркас в `backend/tests/`;
- обновлены `pyproject.toml`, `Makefile`, `README.md` и `.env.example` под backend-first локальный запуск.

## Проверка

- `make lint-backend`
- `make test-backend`
- `make run-backend`
- HTTP smoke-check: `GET /health` возвращает `200 {"status":"ok"}`

## Принятые решения

- backend развивается как отдельный сервис в `backend/`, а не внутри bot-пакета;
- единый composition root остаётся в `maintenance_backend.app`;
- backend-команды выполняются через корневой `Makefile`, а `uv run` используется с `--no-sync`, чтобы не ломать локальный оффлайн workflow после установки зависимостей.
