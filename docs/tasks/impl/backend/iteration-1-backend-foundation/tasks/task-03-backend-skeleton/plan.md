# Задача 03: Каркас backend-сервиса

## Цель

Поднять минимальный работоспособный backend-контур как отдельный сервис в `backend/`, чтобы команда могла локально запускать FastAPI-приложение, расширять его по контрактам задачи 02 и опираться на единые `make`-команды.

## Контекст

- В итерации 1 уже зафиксированы OpenAPI-контракты двух MVP-сценариев в `backend/docs/openapi.yaml`.
- Репозиторий изначально содержал только Telegram-бота в `src/maintenance_bot` и корневые команды для bot-first запуска.
- ADR-002 закрепил отдельный backend на FastAPI, env-конфигурацию через `pydantic-settings`, `uv` как toolchain и `make` как верхнеуровневую точку входа.

## Решения

- Backend оформляется как отдельный сервис в `backend/` с `src`-layout и пакетом `maintenance_backend`.
- Точка композиции приложения находится в `maintenance_backend.app:create_app`.
- Runtime и конфигурация backend отделены от бота: используются отдельные `BACKEND_*` env-переменные, но общий корневой `.env.example`.
- API собирается через versioned router `api/v1`, а transport-схемы и сервисный слой разделяются по подпакетам `schemas/` и `services/`.
- Инженерные команды backend фиксируются в корневом `Makefile`: `make run-backend`, `make lint-backend`, `make test-backend`.

## Состав работ

- Добавить зависимости backend-слоя в корневой `pyproject.toml` и зарегистрировать `maintenance-backend` entrypoint.
- Создать пакет `backend/src/maintenance_backend` с `config.py`, `app.py`, `main.py`, `dependencies.py`, `api/`, `schemas/`, `services/`.
- Реализовать базовый lifecycle FastAPI-приложения, `GET /health` и wiring для app state / dependency injection.
- Обновить `Makefile`, `README.md` и `.env.example` под локальный запуск backend рядом с существующим ботом.
- Подтвердить работоспособность каркаса через линт, тесты и локальный smoke-check `/health`.

## Артефакты

- `backend/src/maintenance_backend/`
- `backend/tests/test_health.py`
- `pyproject.toml`
- `Makefile`
- `README.md`
- `.env.example`

## Definition of Done

- Backend стартует локально как отдельный FastAPI-сервис и отвечает на `/health`.
- Конфигурация backend читается из env без конфликта с текущими bot-переменными.
- `make run-backend`, `make lint-backend`, `make test-backend` работают как стандартные команды разработки.
- Структура backend соответствует foundation-уровню и не смешивает app wiring, transport DTO и сервисный слой в одном модуле.
