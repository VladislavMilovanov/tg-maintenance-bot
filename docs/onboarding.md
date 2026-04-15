# Onboarding

Пошаговый гайд для нового участника проекта. Цель документа: за один сеанс понять структуру системы, поднять полный локальный стек через Docker Compose, проверить работоспособность и знать, где читать код и документы дальше.

## 1. Что установить заранее

Основной full-stack путь требует:
- Docker и Docker Compose
- `make`

Для component-level host-run разработки дополнительно нужны:
- Python `3.12+`
- `uv`
- Node.js `>=20`
- `pnpm`

Проверить версии:

```bash
docker --version
docker compose version
make --version
python3 --version
uv --version
node -v
pnpm -v
```

## 2. Первый запуск полного стека

```bash
git clone <repo-url>
cd tg-maintenance-bot
cp .env.example .env
make stack-build
make stack-up
make stack-ps
make stack-health
```

Ожидаемый результат:
- `postgres` и `backend` становятся healthy;
- frontend доступен на `http://localhost:3000`;
- `http://127.0.0.1:8000/health` возвращает `{"status":"ok"}`.

Если нужен контейнер `bot`, после заполнения `TELEGRAM_BOT_TOKEN`:

```bash
make stack-build-bot
make stack-up-bot
```

Подробный operational runbook: [docker-compose-local.md](docker-compose-local.md).

## 2a. Когда использовать registry-образы

Основной first-run путь остаётся local-build через `make stack-build` и `make stack-up`.

Registry-run нужен, когда нужно:
- проверить опубликованные GHCR-образы без локальной сборки;
- воспроизвести запуск на том же image contract, который публикуется workflow;
- быстро поднять стек на машине, где исходники уже есть, но локальная сборка не нужна.

Базовые команды:

```bash
make stack-pull
make stack-up-registry
```

Если нужен `bot`:

```bash
make stack-up-registry-bot
```

По умолчанию используются образы:
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot/backend:main`
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot/frontend:main`
- `ghcr.io/vladislavmilovanov/tg-maintenance-bot/bot:main`

При необходимости можно переопределить `BACKEND_IMAGE`, `FRONTEND_IMAGE`, `BOT_IMAGE`.

## 3. Что лежит в `.env`

Создайте файл из шаблона:

```bash
cp .env.example .env
```

Минимум для default stack:
- стандартные `POSTGRES_*` можно не менять;
- `BACKEND_OPENROUTER_API_KEY` нужен только для штатного LLM flow без fallback;
- `NEXT_PUBLIC_API_URL` по умолчанию остаётся `http://localhost:8000`.

Дополнительно для `bot`:
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `WHISPER_MODEL` только для voice flow

## 4. Проверка, что всё работает

### Compose smoke-check

```bash
make stack-ps
make stack-health
```

Также должны открываться:
- `http://localhost:3000`
- `http://127.0.0.1:8000/ready`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Уточнение:
- `/health` должен возвращать `{"status":"ok"}` сразу после успешного старта backend;
- `/ready` возвращает `{"status":"ok"}` только если доступен PostgreSQL;
- если backend поднят, но БД недоступна, `/ready` вернёт `503 Service Unavailable`.

### Frontend smoke-check

1. Открыть `http://localhost:3000`
2. Убедиться, что root ведёт на `/dashboard`
3. Выполнить login по Telegram username
4. Проверить, что открываются `/dashboard`, `/chat`, `/admin`

### Telegram Bot smoke-check

1. Поднять стек с `make stack-up-bot`
2. Убедиться, что `bot` контейнер не падает
3. Отправить боту текстовое сообщение
4. При наличии `OPENAI_API_KEY` проверить voice message

### Какие проверки требуют секретов

- `make stack-up` не требует Telegram token;
- `make stack-up-bot` требует `TELEGRAM_BOT_TOKEN`;
- voice flow требует `OPENAI_API_KEY`;
- штатный backend assistant flow требует `BACKEND_OPENROUTER_API_KEY`, иначе будет fallback.

## 5. Host-run fallback для точечной разработки

Docker Compose является основным full-stack сценарием. Если нужно локально разрабатывать только один компонент, доступны host-run команды.

### Backend

```bash
make install
make db-up
make db-migrate
make db-import
make run-backend
```

### Frontend

```bash
make web-install
make web-dev
```

### Telegram Bot

```bash
make run
```

Исходный код Telegram-клиента находится в `src/maintenance_bot`. Папка `bot/` используется только для документации.

## 6. Куда смотреть в первую очередь

Документы:
- `README.md` — быстрый вход
- `docs/docker-compose-local.md` — source of truth для container workflow
- `docs/architecture.md` — high-level архитектура и runtime-потоки
- `docs/vision.md` — продуктовые границы
- `docs/tech/api-contracts.md` — entrypoint в общую документацию по API-контрактам
- `backend/docs/openapi.yaml` — API source of truth
- `backend/docs/api-contracts.md` — пояснения к контрактам

Кодовые entrypoints:
- `backend/src/maintenance_backend/app.py` — FastAPI application factory и middleware
- `backend/src/maintenance_backend/api/v1/router.py` — состав versioned API
- `src/maintenance_bot/main.py` — запуск Telegram-клиента
- `frontend/src/app` — маршруты и layouts frontend
- `frontend/src/lib/api` — frontend API layer

## 7. Рабочий процесс

В проекте принята схема проектирования и реализации через документы:
- `docs/plan.md` — roadmap на уровне крупных этапов;
- iteration/task `plan.md` — план конкретной итерации или задачи;
- iteration/task `summary.md` — итог выполненной работы.

Для первого входа используйте `README.md`, `docs/onboarding.md`, `docs/docker-compose-local.md`, `docs/architecture.md` и актуальные component README.

## 8. Как готовить изменения

Перед изменениями полезно сначала поднять локальный стек, а перед завершением прогнать проверки качества.

Если изменение затрагивает backend API, OpenAPI, auth flow, env-переменные, команды запуска или smoke-check, перед завершением работы нужно прогнать документарную сверку через локальный subagent `docs-updater`.

Минимальное правило:
- backend/API change -> проверить `backend/docs/api-contracts.md`, `docs/tech/api-contracts.md`, `docs/onboarding.md`;
- startup/env/workflow change -> проверить `README.md`, `backend/README.md`, `docs/onboarding.md`, `docs/docker-compose-local.md`.

Для image pipeline изменения дополнительно проверить:
- `.github/workflows/ghcr-images.yml`;
- `devops/compose/compose.registry.yaml`;
- команды `Makefile`, связанные с registry-run.

Пример prompt:

```text
Use $docs-updater to inspect the current diff, identify documentation drift, and update docs/tech/api-contracts.md plus any affected onboarding sections.
```

## 9. Проверки качества

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

Текущее состояние frontend quality strategy:
- отдельный automated test suite для frontend пока не настроен;
- текущие обязательные проверки — `web-lint`, `web-build` и ручной smoke-check.
