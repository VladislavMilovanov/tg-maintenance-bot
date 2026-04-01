# Задача 05: Реализация endpoint'ов и логики

## Итог

Задача завершена в рамках итерации 1.

## Что сделано

- backend переведён с baseline stub/in-memory сервисов на production-oriented wiring через app state и lifecycle;
- добавлен PostgreSQL-backed слой хранения для `equipment` и `equipment_state_records`;
- реализована проверка `equipment_id`, idempotency по `idempotency_key` и контрактные ошибки `404/409`;
- assistant flow переведён на OpenRouter-compatible gateway с деградированным fallback и `503`, если не удалось вернуть даже fallback;
- добавлен `GET /ready` для readiness-check PostgreSQL при сохранении `GET /health` как liveness endpoint;
- синхронизированы `README.md`, `.env.example`, `backend/docs/openapi.yaml`, `docs/data-model.md`, `docs/integrations.md` и `docs/tasks/tasklist-backend.md`.

## Проверка

- `UV_CACHE_DIR=.uv-cache uv run --no-sync ruff check backend/src/ backend/tests/`
- `UV_CACHE_DIR=.uv-cache PYTHONPATH=backend/src uv run --no-sync pytest backend/tests/`

## Принятые решения

- conversation history не выносилась в PostgreSQL: для task 05 достаточно ephemeral conversation store с TTL;
- OpenRouter ключ остаётся optional для локального запуска: без него assistant flow отвечает fallback-ответом;
- минимальная схема PostgreSQL создаётся на старте backend без отдельного migration tool на этом этапе.
