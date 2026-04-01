# Задача 04: Базовые API-тесты backend

## Цель

Добавить базовый regression-слой для backend API поверх контрактов задачи 02 и app factory из backend-каркаса. Набор должен проверять assistant flow и ручную фиксацию состояния без Telegram Bot API и без реальных вызовов OpenRouter.

## Контекст

- В репозитории уже есть backend-каркас с `FastAPI`, `create_app()` и smoke-тестом `/health`.
- Контракты двух MVP-сценариев зафиксированы в `backend/docs/openapi.yaml`.
- Для задачи 04 важно проверять именно HTTP-поведение backend, а не внутренние функции Telegram-бота.

## Решения

- Использовать единый async test stack: `pytest` + `httpx.AsyncClient` + `ASGITransport`.
- Подключать тесты к приложению через `create_app()` и свежий экземпляр app на каждый тест.
- Добавить override-friendly dependency layer для assistant и state-record сервисов.
- Для assistant flow покрыть:
  - успешный ответ через deterministic stub;
  - деградированный fallback-ответ при отказе upstream assistant gateway.
- Для state-record flow покрыть:
  - успешное создание записи;
  - ошибку при отсутствии обязательного поля;
  - ошибку при недопустимом enum-значении.
- Нормализовать request validation errors в единый payload `ErrorResponse`, чтобы тесты и клиенты работали с одной формой ответа.

## Состав работ

- Добавить DTO и enum-модели для assistant/state-record сценариев.
- Добавить backend-роуты `POST /api/v1/assistant/messages` и `POST /api/v1/equipment-state-records`.
- Добавить простые сервисы по умолчанию, достаточные для тестового baseline и dependency overrides.
- Расширить `backend/tests/` новыми API-тестами.
- Синхронизировать `README.md` по команде `make test-backend` и отсутствию требований к реальным Telegram/OpenRouter ключам.

## Артефакты

- `backend/src/maintenance_backend/models.py`
- `backend/src/maintenance_backend/dependencies.py`
- `backend/src/maintenance_backend/services.py`
- `backend/src/maintenance_backend/api/assistant.py`
- `backend/src/maintenance_backend/api/equipment_state_records.py`
- `backend/tests/conftest.py`
- `backend/tests/test_assistant_api.py`
- `backend/tests/test_equipment_state_records_api.py`
- `README.md`

## Definition of Done

- `make test-backend` выполняет только backend-тесты и проходит локально.
- Assistant и state-record сценарии покрыты success/error путями на уровне HTTP API.
- Внешние вызовы не требуются: тесты работают на моках и in-process ASGI app.
- README объясняет, как запустить backend API-тесты локально.
