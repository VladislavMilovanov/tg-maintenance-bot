# TG Maintenance Bot

Система мониторинга состояния оборудования с единым backend-ядром и двумя клиентами:
- Telegram-бот для быстрых запросов;
- frontend-приложение для инженерного и административного сценариев.

## Архитектура

Высокоуровневое описание системы, runtime-потоки и диаграммы находятся в [docs/architecture.md](docs/architecture.md). Продуктовое видение и границы системы зафиксированы в [docs/vision.md](docs/vision.md).

```mermaid
flowchart LR
    TG["Telegram Bot"] --> BE["Backend"]
    FE["Frontend"] --> BE
    EXT["Monitoring Sources"] --> BE
    BE --> DB[("PostgreSQL")]
    BE --> LLM["OpenRouter / LLM"]
```

## Что находится в репозитории

```text
tg-maintenance-bot/
├── backend/            # FastAPI backend
├── frontend/           # Next.js web-клиент
├── src/maintenance_bot # Telegram-клиент
├── bot/                # документация Telegram-слоя
├── devops/             # Dockerfile и compose-related implementation artifacts
├── docs/               # архитектура, onboarding, runbooks, roadmap
├── compose.yaml        # основной local full-stack compose entrypoint
├── Makefile            # короткие operator-facing команды
└── .env.example        # шаблон локального окружения
```

## Prerequisites

Для основного локального цикла нужны:
- Docker и Docker Compose
- `make`

Для component-level host-run разработки дополнительно нужны:
- Python `3.12+`
- [`uv`](https://docs.astral.sh/uv/)
- Node.js `>=20`
- `pnpm`

Проверить версии можно так:

```bash
docker --version
docker compose version
make --version
python3 --version
uv --version
node -v
pnpm -v
```

## Быстрый старт

Основной локальный путь для полного стека:

```bash
cp .env.example .env
make stack-build
make stack-up
make stack-ps
make stack-health
```

Что это делает:
- `make stack-build` собирает контейнерные образы `backend` и `frontend`;
- `make stack-up` поднимает `postgres`, `backend`, `frontend`;
- `make stack-ps` показывает статусы контейнеров;
- `make stack-health` проверяет backend по `http://127.0.0.1:8000/health`.

Если нужен Telegram-бот в контейнере:

```bash
make stack-build-bot
make stack-up-bot
```

Для этого должен быть задан `TELEGRAM_BOT_TOKEN` в `.env`.

Подробный runbook локального container workflow: [docs/docker-compose-local.md](docs/docker-compose-local.md). Пошаговый onboarding: [docs/onboarding.md](docs/onboarding.md).

## GHCR Image Pipeline

Workflow публикации образов находится в [.github/workflows/ghcr-images.yml](.github/workflows/ghcr-images.yml).

Что он делает:
- на `pull_request` в `main` только проверяет сборку `backend`, `frontend`, `bot` без push;
- на `push` в `main` публикует теги `main` и `sha-*`;
- на semver tags `v*.*.*` публикует `<version>`, `latest` и `sha-*`.

Имена образов:
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot-backend`
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot-frontend`
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot-bot`

Базовый auth path для publish — `GITHUB_TOKEN` того же репозитория. Для работы workflow у GitHub Actions должны быть права на запись package artifacts в GHCR.

## Переменные окружения

Файл создаётся из шаблона:

```bash
cp .env.example .env
```

Минимум для default stack:
- дефолтные `POSTGRES_*` можно оставить как есть;
- `NEXT_PUBLIC_API_URL` по умолчанию остаётся `http://localhost:8000`;
- `BACKEND_OPENROUTER_API_KEY` нужен только для штатного LLM flow без fallback.

Дополнительно для `bot`:
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `WHISPER_MODEL` только для voice flow

## Проверка, что всё работает

После `make stack-up`:
- frontend должен открываться на `http://localhost:3000`;
- `http://127.0.0.1:8000/health` должен возвращать `{"status":"ok"}`;
- `http://127.0.0.1:8000/ready` должен возвращать `{"status":"ok"}` при доступной БД;
- `docker compose ps` должен показывать healthy `postgres` и `backend`.

Дополнительно для запуска с bot profile:
- контейнер `bot` не должен падать при валидно заданном `TELEGRAM_BOT_TOKEN`.

## Host-run fallback

Component-level host-run сценарии сохранены для точечной разработки:
- `make install`
- `make run-backend`
- `make run`
- `make web-install`
- `make web-dev`

Это не основной first-run путь полного стека. Используйте его только когда нужно разрабатывать или диагностировать конкретный компонент вне compose-сценария.

## Тесты и проверки качества

Telegram-клиент:

```bash
make lint
make test
```

Backend:

```bash
make lint-backend
make test-backend
BACKEND_DATABASE_URL=postgresql://postgres:postgres@localhost:55433/tg_maintenance make test-backend-integration
```

Frontend:

```bash
make web-lint
make web-build
```

Контейнерный smoke-check:

```bash
make stack-build
make stack-up
make stack-health
make stack-down
```

## Основные make-команды

Full-stack compose lifecycle:
- `make stack-build`
- `make stack-build-bot`
- `make stack-pull`
- `make stack-up`
- `make stack-up-bot`
- `make stack-up-registry`
- `make stack-up-registry-bot`
- `make stack-ps`
- `make stack-logs`
- `make stack-logs-backend`
- `make stack-health`
- `make stack-down`
- `make stack-clean`

Component-level fallback:
- `make install`
- `make run-backend`
- `make run`
- `make web-install`
- `make web-dev`

Database-only workflow:
- `make db-up`
- `make db-down`
- `make db-reset`
- `make db-migrate`
- `make db-downgrade`
- `make db-import`
- `make db-check`
- `make db-psql`

## Документация

- [docs/docker-compose-local.md](docs/docker-compose-local.md) — source of truth для container workflow
- [docs/onboarding.md](docs/onboarding.md) — пошаговый гайд для нового участника
- [docs/architecture.md](docs/architecture.md) — high-level архитектура и runtime-потоки
- [docs/vision.md](docs/vision.md) — продуктовое видение и границы системы
- [docs/plan.md](docs/plan.md) — roadmap проекта, а не operational entrypoint
- [docs/data-model.md](docs/data-model.md) — проектная модель данных и её границы
- [docs/integrations.md](docs/integrations.md) — внешние интеграции и протоколы
- [docs/tech/api-contracts.md](docs/tech/api-contracts.md) — точка входа к API-контрактам
- [docs/doc-audit.md](docs/doc-audit.md) — живой аудит документации и открытых несоответствий

Дополнительный registry-based запуск:

```bash
make stack-pull
make stack-up-registry
```

Если нужен `bot` на опубликованных образах:

```bash
make stack-up-registry-bot
```

Этот режим нужен для проверки опубликованных GHCR-образов и не заменяет основной first-run path с локальной сборкой.

## Документационный review

Если изменение затрагивает backend API, OpenAPI, env-переменные, startup flow, smoke-check или frontend/backend auth, перед завершением работы нужно проверить documentation drift через локальный subagent `docs-updater`.

Типовые триггеры:
- изменились endpoint, DTO, auth contract или error shape;
- изменились `backend/docs/openapi.yaml` или backend runtime-контракты;
- изменились команды запуска, порты, env-переменные или onboarding-шаги.

Точка входа и пример вызова описаны в [.agents/README.md](.agents/README.md).

## Источники истины

- Runtime API: `/docs`, `/openapi.json`
- Hand-written OpenAPI: `backend/docs/openapi.yaml`
- Backend contract notes: `backend/docs/api-contracts.md`
- Кодовые entrypoints:
  - `backend/src/maintenance_backend/app.py`
  - `backend/src/maintenance_backend/api/v1/router.py`
  - `src/maintenance_bot/main.py`
  - `frontend/src/lib/api/`
