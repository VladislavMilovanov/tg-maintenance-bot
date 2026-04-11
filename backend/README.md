# Backend

FastAPI backend является единым ядром системы. Он обслуживает Telegram-бота и web-клиент, работает с PostgreSQL и выполняет LLM-интеграцию.

## Что относится к backend

- код: `backend/src/maintenance_backend`
- API-контракты: `backend/docs/openapi.yaml`, `backend/docs/api-contracts.md`
- тесты: `backend/tests`, `backend/tests_integration`
- runtime-конфиг: переменные окружения `BACKEND_*`

## Зависимости

- Python `3.12+`
- `uv`
- Docker и Docker Compose

## Настройка

1. Из корня репозитория установить Python-зависимости:

```bash
make install
```

2. Создать `.env` из корневого шаблона:

```bash
cp .env.example .env
```

3. Заполнить минимум:
- `BACKEND_DATABASE_URL`
- `BACKEND_OPENROUTER_API_KEY` только если нужен штатный LLM flow без fallback

`backend/.env.example` дублирует backend-only переменные как справочный файл, но основная точка входа для локального запуска остаётся корневой `.env.example`.

## Локальный DB workflow

```bash
make db-up
make db-migrate
make db-import
make db-check
```

По умолчанию PostgreSQL доступен по `postgresql://postgres:postgres@localhost:55433/tg_maintenance`.

Поддерживаемые DB-команды:
- `make db-up`
- `make db-down`
- `make db-reset`
- `make db-migrate`
- `make db-downgrade`
- `make db-import`
- `make db-check`
- `make db-psql`

## Запуск backend

```bash
make run-backend
```

Сервис стартует на `http://127.0.0.1:8000`.

## Smoke-check

После запуска проверьте:
- `GET /health`
- `GET /ready`
- `GET /docs`
- `GET /openapi.json`

`/health` используется как liveness-check и не зависит от БД.  
`/ready` проверяет доступность PostgreSQL.

## Тесты backend

Unit/API набор:

```bash
make test-backend
```

Integration-набор с реальной БД:

```bash
BACKEND_DATABASE_URL=postgresql://postgres:postgres@localhost:55433/tg_maintenance make test-backend-integration
```

Перед integration tests БД должна быть поднята и мигрирована.

## Проверки качества

```bash
make lint-backend
make test-backend
make test-backend-integration
```

## Контракты и документация

- hand-written OpenAPI source of truth: `backend/docs/openapi.yaml`
- текстовое пояснение к контрактам: `backend/docs/api-contracts.md`
- обзорная точка входа из общего docs tree: `docs/tech/api-contracts.md`
