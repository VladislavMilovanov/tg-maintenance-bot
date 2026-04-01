# Задача 04: Базовые API-тесты backend

## Итог

Задача завершена в рамках итерации 1.

## Что сделано

- добавлены DTO и enum-модели для двух MVP API-сценариев backend;
- добавлены backend-роуты `POST /api/v1/assistant/messages` и `POST /api/v1/equipment-state-records`;
- добавлен override-friendly dependency layer и минимальные сервисы по умолчанию для тестового baseline;
- унифицирован request validation error payload до формы `code` / `message` / `details` / `trace_id`;
- расширен `backend/tests/` асинхронными API-тестами для assistant и state-record сценариев;
- README обновлён инструкцией по запуску `make test-backend` без реальных ключей Telegram/OpenRouter.

## Проверка

- `PYTHONPATH=backend/src uv run --no-sync pytest backend/tests/`
- `uv run --no-sync ruff check backend/src/ backend/tests/`

## Принятые решения

- async HTTP-тесты выполняются через `httpx.AsyncClient` и `ASGITransport`, без поднятия отдельного сервера;
- assistant failure-path реализован как деградированный ответ `200` с `meta.fallback_used=true`, а не как сетевой вызов наружу;
- baseline реализации остаются минимальными и deterministic, чтобы тесты не зависели от внешних систем.
