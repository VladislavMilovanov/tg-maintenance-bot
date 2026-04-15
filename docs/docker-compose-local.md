# Local Docker Compose Runbook

Основной сценарий локального запуска полного проекта проходит через Docker Compose и `Makefile`. Host-run команды остаются только как fallback для точечной разработки отдельных компонентов.

## Prerequisites

Нужны:
- Docker и Docker Compose
- `make`
- свободные порты `3000`, `8000`, `55433`
- `TELEGRAM_BOT_TOKEN` только если нужен контейнер `bot`

Быстрая проверка:

```bash
docker --version
docker compose version
make --version
```

## Подготовка `.env`

Создайте локальный конфиг:

```bash
cp .env.example .env
```

Минимум для default stack:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` можно оставить по умолчанию;
- `BACKEND_OPENROUTER_API_KEY` нужен только для штатного LLM flow без fallback.

Дополнительно для запуска `bot`:
- `TELEGRAM_BOT_TOKEN`
- при необходимости `OPENAI_API_KEY` для voice flow

## Сборка образов

Default stack:

```bash
make stack-build
```

С bot profile:

```bash
make stack-build-bot
```

Сервисы iteration 1 работают в image-only режиме. Bind mounts не являются основным локальным сценарием.

## Запуск на опубликованных GHCR-образах

Registry runtime использует root `compose.yaml` вместе с override `devops/compose/compose.registry.yaml`. Это не второй основной entrypoint, а дополнительный режим запуска.

Подтянуть опубликованные образы:

```bash
make stack-pull
```

Запустить default stack на registry-образах:

```bash
make stack-up-registry
```

Запустить полный стек с bot profile на registry-образах:

```bash
make stack-up-registry-bot
```

По умолчанию используются теги `:main`:
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot/backend:main`
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot/frontend:main`
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot/bot:main`

Для запуска на другом published tag можно переопределить env-переменные:

```bash
BACKEND_IMAGE=ghcr.io/vladislavmilovanov/tg-maintenance-bot/backend:0.1.0 \
FRONTEND_IMAGE=ghcr.io/vladislavmilovanov/tg-maintenance-bot/frontend:0.1.0 \
BOT_IMAGE=ghcr.io/vladislavmilovanov/tg-maintenance-bot/bot:0.1.0 \
make stack-up-registry
```

## Запуск

Default stack поднимает `postgres`, `backend`, `frontend`:

```bash
make stack-up
```

Полный стек с bot profile:

```bash
make stack-up-bot
```

Reference-команды без `make`:

```bash
docker compose up -d
COMPOSE_PROFILES=bot docker compose up -d
```

## Проверка после старта

Статус сервисов:

```bash
make stack-ps
```

Backend smoke-check:

```bash
make stack-health
```

Ожидаемые URL:
- frontend: `http://localhost:3000`
- backend health: `http://127.0.0.1:8000/health`
- backend ready: `http://127.0.0.1:8000/ready`
- backend docs: `http://127.0.0.1:8000/docs`

Успешный запуск iteration 1 означает:
- `postgres` и `backend` имеют healthy status в `docker compose ps`;
- frontend открывается на `http://localhost:3000`;
- `make stack-health` возвращает `{"status":"ok"}`.

## Логи и диагностика

Логи всего стека:

```bash
make stack-logs
```

Логи конкретного сервиса:

```bash
make stack-logs-backend
make stack-logs-frontend
make stack-logs-postgres
make stack-logs-bot
```

## Остановка и очистка

Остановить стек без удаления volume:

```bash
make stack-down
```

Остановить стек и очистить named volumes:

```bash
make stack-clean
```

Повторный запуск после остановки:

```bash
make stack-up
```

Для registry-run после остановки используется тот же lifecycle, но повторный старт делается через `make stack-up-registry` или `make stack-up-registry-bot`.

Cold start после полной очистки:

```bash
make stack-clean
make stack-build
make stack-up
```

## Частые проблемы

### Docker daemon не запущен

Симптом: `docker compose` возвращает ошибку вида `Cannot connect to the Docker daemon`.

Действие: запустить Docker Desktop или другой Docker daemon и повторить `make stack-up`.

### Не задан `TELEGRAM_BOT_TOKEN`

Симптом: `bot` контейнер завершается сразу после старта.

Действие: либо добавить токен в `.env`, либо использовать default stack без бота через `make stack-up`.

### Backend не проходит readiness

Симптом: `backend` не становится healthy, `/ready` возвращает `503`.

Действие:
- проверить `make stack-logs-postgres`;
- проверить `make stack-logs-backend`;
- убедиться, что `BACKEND_DATABASE_URL` не переопределён на недоступный host.

### Frontend не достучался до backend

Симптом: UI открывается, но API-запросы падают.

Действие: проверить `NEXT_PUBLIC_API_URL` в `.env`. Для локального браузерного доступа значение по умолчанию должно оставаться `http://localhost:8000`.

### Порт уже занят

Симптом: один из контейнеров не стартует из-за bind error.

Конфликтующие порты:
- `55433` для PostgreSQL
- `8000` для backend
- `3000` для frontend

Действие: освободить порт или переопределить переменную в `.env` и перезапустить стек.

## GHCR workflow и теги

Workflow публикации образов: `.github/workflows/ghcr-images.yml`.

Правила:
- `pull_request` в `main` только проверяет сборку, не публикует образы;
- `push` в `main` публикует теги `main` и `sha-*`;
- `push` git tag вида `vX.Y.Z` публикует теги `X.Y.Z`, `latest` и `sha-*`.

Ожидаемый auth path для publish — `GITHUB_TOKEN` того же репозитория. Если repository/org policy блокирует GHCR publish, нужно отдельно включить package write permissions в настройках GitHub.
