# TG Maintenance Bot
Система мониторинга состояния оборудования для инженеров, операторов и ответственных за эксплуатацию.

## О проекте
Производственным командам сложно быстро понимать текущее состояние оборудования и приоритеты реакции.  
Проект решает это через единое backend-ядро с клиентами в Telegram и Web.  
Ключевые пользователи: инженер, пользователь системы мониторинга и админ.

## Архитектура
```mermaid
flowchart LR
    TG[Telegram-бот] --> BE[Backend]
    WEB[Web-приложение] --> BE
    BE --> DB[(Слой данных)]
    BE --> LLM[LLM]
    BE --> EXT[Внешние источники мониторинга]
```

## Статус
- ✅ Итерация 1: Backend foundation
- ✅ Итерация 2: Telegram MVP client
- 📋 Итерация 3: Web unified client
- 📋 Итерация 4: Monitoring and LLM integrations
- 📋 Итерация 5: Platform readiness

## Документация
- [Идея продукта](docs/idea.md)
- [Архитектурное видение](docs/vision.md)
- [Модель данных](docs/data-model.md)
- [Интеграции](docs/integrations.md)
- [План](docs/plan.md)
- [Задачи](docs/tasks/)

## Быстрый старт
Backend живёт в `backend/`, но поднимается из корня репозитория как отдельный процесс.

1. Создать окружение и установить зависимости: `make install`
2. Скопировать `.env.example` в `.env`
3. Заполнить минимум `TELEGRAM_BOT_TOKEN` и `BACKEND_DATABASE_URL`; для штатных LLM-ответов backend дополнительно задать `BACKEND_OPENROUTER_API_KEY`
4. Поднять локальную БД: `make db-up`
5. Применить baseline migration: `make db-migrate`
6. Импортировать sample data: `make db-import`
7. Проверить данные: `make db-check`
8. Запустить backend: `make run-backend`
9. Запустить Telegram-бота в отдельном процессе: `make run`

Дополнительно для acceptance-check доступны алиасы:
- `make backend-run`
- `make backend-lint`
- `make backend-test`

После старта backend доступны:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/ready`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

`/docs` и `/openapi.json` — runtime-проекция текущего backend API. Hand-written source of truth для контракта хранится в `backend/docs/openapi.yaml`.

Если `BACKEND_OPENROUTER_API_KEY` не задан или OpenRouter недоступен, assistant flow вернёт деградированный fallback-ответ с `meta.fallback_used=true`.
Backend больше не должен полагаться на runtime `ensure_schema()`/startup seed как на основной путь подготовки БД. Поддерживаемый workflow для локальной разработки: сначала `make db-migrate`, затем `make db-import`, и только после этого запуск backend.

`backend/.env.example` дублирует backend-only набор переменных как справочный файл. Основной локальный entrypoint для запуска из корня остаётся `.env.example`.

## Backend тесты

Запуск backend API-тестов:

```bash
make test-backend
```

Набор проверяет:
- `POST /api/v1/assistant/messages`
- `POST /api/v1/equipment-state-records`
- `/health` smoke-check
- `/ready` readiness-check

Тесты работают на in-process ASGI app и dependency overrides, поэтому реальные Telegram/OpenRouter ключи для этого набора не нужны.

## Проверка качества backend

- `make lint-backend`
- `make test-backend`
- `make test-backend-integration`
- `make backend-lint`
- `make backend-test`
- `make backend-test-integration`

Эти команды документируют текущий публичный интерфейс разработки для backend foundation и не требуют дополнительных make-целей сверх уже существующих.

Фиксация backend foundation в репозитории подтверждается следующими проверками:
- `make test-backend` -> `18 passed`
- `make test` -> `5 passed`
- локальный smoke-run backend с PostgreSQL и проверкой `GET /health`
- проверка business endpoint `POST /api/v1/assistant/messages`
- проверка runtime OpenAPI по `/openapi.json`

Процент покрытия отдельно не публикуется: в текущем репозитории не настроен `pytest-cov` или эквивалентный coverage tooling.

При HTTP-запросах backend пишет privacy-safe request logs: в них есть `chat_id` и размеры request/response, но нет текста переписки.

## DB Workflow

Для data layer проект использует следующий стек:
- `SQLAlchemy 2.x Declarative` для persistence models;
- `Alembic` для schema migrations;
- `AsyncEngine` и `AsyncSession` для runtime-доступа к PostgreSQL;
- repository layer поверх session layer.

Ежедневный локальный flow:
1. `make db-up` — поднять PostgreSQL через `compose.yaml`.
2. `make db-migrate` — применить миграции Alembic.
3. `make db-import` — загрузить sample dataset из `data/progress-import.v1.json`.
4. `make db-check` — убедиться, что ключевые таблицы заполнены и связи читаются.
5. `make run-backend` — запускать backend уже поверх мигрированной схемы.

Поддерживаемые DB-команды:
- `make db-up` — старт локального PostgreSQL.
- `make db-down` — остановка контейнера без удаления volume.
- `make db-reset` — пересоздание локальной БД в clean state через `docker compose down -v && up`.
- `make db-migrate` — `alembic upgrade head`.
- `make db-downgrade` — откат на одну ревизию назад.
- `make db-import` — импорт из `data/progress-import.v1.json`.
- `make db-check` — короткая проверка counts и импортированных связей.
- `make db-psql` — интерактивный `psql` в контейнере.

По умолчанию `compose.yaml` публикует PostgreSQL на `localhost:55433`, поэтому `.env.example` использует `postgresql://postgres:postgres@localhost:55433/tg_maintenance`.

Файл `data/progress-import.v1.json` является versioned template + sample dataset. Верхний уровень файла повторяет названия таблиц:
- `system_actors`
- `locations`
- `data_sources`
- `equipment`
- `sensors`
- `sensor_groups`
- `sensor_group_members`
- `equipment_state_snapshots`
- `equipment_state_snapshot_sensors`
- `equipment_state_snapshot_sensor_groups`
- `equipment_state_records`
- `equipment_state_record_sensors`
- `equipment_state_record_sensor_groups`
- `knowledge_items`
- `knowledge_item_equipment_types`
- `knowledge_item_sensor_types`
- `knowledge_item_sensor_group_types`

Обязательный маркер формата: `"schema_version": "progress-import.v1"`.

Если нужен ручной SQL-inspect после импорта:

```sql
SELECT equipment_id, name, current_status FROM equipment ORDER BY equipment_id;

SELECT record_id, equipment_id, status, observed_at
FROM equipment_state_records
ORDER BY observed_at DESC;

SELECT snapshot_id, equipment_id, status, effective_at
FROM equipment_state_snapshots
ORDER BY effective_at DESC;
```

Для проверки SQLAlchemy-backed persistence flow используйте отдельный integration набор:

```bash
BACKEND_DATABASE_URL=postgresql://postgres:postgres@localhost:55433/tg_maintenance make test-backend-integration
```

## Связка с Telegram-ботом

В итерации 2 Telegram-бот больше не вызывает LLM напрямую и работает только через backend API.

Последовательность локального запуска:

1. `make run-backend`
2. `make run`
3. Отправить сообщение боту в Telegram
4. Проверить assistant flow через backend endpoint `POST /api/v1/assistant/messages`

Bot runtime ожидает:
- `TELEGRAM_BOT_TOKEN`
- `BACKEND_URL` с default `http://127.0.0.1:8000`
- `BACKEND_TIMEOUT_SECONDS`

Если backend недоступен или вернул ошибку, бот отвечает единым сервисным сообщением и не пытается обходить backend прямым вызовом LLM.

## Проверка качества бота

- `make lint`
- `make test`
