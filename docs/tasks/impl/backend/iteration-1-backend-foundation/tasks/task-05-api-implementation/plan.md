# Задача 05: Реализация endpoint'ов и логики

## Цель

Довести backend foundation до рабочего API-поведения: подключить PostgreSQL для сценария фиксации состояния, реализовать assistant flow через backend-owned OpenRouter gateway с fallback и добавить readiness-check для operational use.

## Решения

- `POST /api/v1/assistant/messages` использует OpenRouter-compatible gateway и не требует прямого вызова LLM из клиентов.
- `conversation_id` управляется backend-ом через ephemeral in-memory store с TTL, без отдельного persistence-слоя истории.
- `POST /api/v1/equipment-state-records` валидирует `equipment_id` по PostgreSQL и поддерживает idempotency через `idempotency_key`.
- Минимальная схема PostgreSQL создаётся backend-ом на старте: `equipment` и `equipment_state_records`.
- `GET /health` остаётся liveness endpoint, `GET /ready` проверяет доступность PostgreSQL.
- Все бизнес-ошибки маппятся в единый `ErrorResponse`.

## Состав работ

- Добавить env-конфиг для PostgreSQL, timeout/system prompt OpenRouter и TTL conversation store.
- Реализовать database/repository слой, domain exceptions и app wiring через lifecycle.
- Реализовать assistant gateway, fallback и business-validation оборудования в assistant context.
- Реализовать persistence/idempotency для state records.
- Обновить backend API-тесты, README, `.env.example`, OpenAPI и проектные docs.

## Definition of Done

- `POST /api/v1/assistant/messages` возвращает штатный или fallback-ответ по контракту.
- `POST /api/v1/equipment-state-records` возвращает `201/404/409/422` в ожидаемых сценариях.
- `/ready` сигнализирует недоступность PostgreSQL, `/health` остаётся лёгким smoke endpoint.
- `make test-backend` и `make lint-backend` проходят локально.
