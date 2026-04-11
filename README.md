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
├── docs/               # архитектура, onboarding, roadmap, audit
├── data/               # sample dataset для локального запуска
├── compose.yaml        # локальный PostgreSQL
├── Makefile            # единые dev-команды
└── .env.example        # шаблон локального окружения
```

## Prerequisites

Для полного локального цикла нужны:
- Python `3.12+`
- [`uv`](https://docs.astral.sh/uv/)
- Docker и Docker Compose
- Node.js `>=20`
- `pnpm`

Проверить версии можно так:

```bash
python3 --version
uv --version
docker --version
docker compose version
node -v
pnpm -v
```

## Быстрый старт

Локальный порядок запуска без обращения к `docs/tasks/`:

```bash
make install
cp .env.example .env
make web-install
make db-up
make db-migrate
make db-import
make run-backend
make web-dev
make run
```

Примечания:
- `make install` рассчитан на свежий клон. Если `.venv` уже существует, команда завершится ошибкой на шаге `uv venv`; для повторной установки зависимостей используйте `uv pip install -e ".[dev]"`.
- Перед `make db-up` должен быть запущен Docker daemon, иначе `docker compose` вернёт ошибку вида `Cannot connect to the Docker daemon`.

Что это делает:
- `make install` создаёт `.venv` и ставит Python-зависимости;
- `make web-install` ставит frontend-зависимости;
- `make db-up` / `make db-migrate` / `make db-import` поднимают и подготавливают локальную БД;
- `make run-backend` запускает FastAPI backend на `http://127.0.0.1:8000`;
- `make web-dev` запускает frontend на `http://localhost:3000`;
- `make run` запускает Telegram-бота.

Подробный пошаговый гайд для нового участника находится в [docs/onboarding.md](docs/onboarding.md).

## Переменные окружения

### Обязательные для базового цикла

Файл создаётся из шаблона:

```bash
cp .env.example .env
```

Минимум для запуска:
- `TELEGRAM_BOT_TOKEN` — для Telegram-бота;
- `BACKEND_DATABASE_URL` — для backend и integration tests.

### Опциональные для backend

- `BACKEND_OPENROUTER_API_KEY` — нужен для штатного LLM flow;
- без него backend должен отдавать fallback-ответ там, где это предусмотрено assistant flow.

### Опциональные для голосового ввода в Telegram

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `WHISPER_MODEL`

### Frontend

Frontend использует:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Эта переменная хранится в `frontend/.env.local` и по умолчанию frontend уже смотрит в `http://localhost:8000`.

## Проверка, что всё работает

### Backend

После `make run-backend` доступны:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/ready`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Ожидаемые признаки успеха:
- `/health` возвращает `{"status":"ok"}`;
- `/ready` возвращает `{"status":"ok"}` при доступном PostgreSQL;
- `/ready` возвращает `503 Service Unavailable`, если backend поднят, но PostgreSQL недоступен;
- `/docs` и `/openapi.json` публикуют runtime API.

### Frontend

После `make web-dev`:
1. открыть `http://localhost:3000`;
2. убедиться, что root ведёт на `/dashboard`;
3. выполнить login по Telegram username;
4. проверить страницы `/dashboard`, `/chat`, `/admin`.

### Telegram-бот

После `make run`:
1. отправить сообщение боту в Telegram;
2. убедиться, что бот отвечает через backend;
3. при наличии `OPENAI_API_KEY` дополнительно проверить voice message.

Для самого запуска `make run` обязателен непустой `TELEGRAM_BOT_TOKEN`.

## Тесты

### Telegram-клиент

```bash
make test
```

### Backend

```bash
make test-backend
```

### Backend integration с PostgreSQL

```bash
BACKEND_DATABASE_URL=postgresql://postgres:postgres@localhost:55433/tg_maintenance make test-backend-integration
```

### Frontend

Отдельный automated test suite для frontend в текущем репозитории не настроен.

## Проверки качества

### Telegram-клиент

```bash
make lint
```

### Backend

```bash
make lint-backend
make test-backend
make test-backend-integration
```

### Frontend

```bash
make web-lint
make web-build
```

`web-build` используется как дополнительная smoke-проверка сборки.

## Документационный review

Если изменение затрагивает backend API, OpenAPI, env-переменные, startup flow, smoke-check или frontend/backend auth, перед завершением работы нужно проверить documentation drift через локальный subagent `docs-updater`.

Типовые триггеры:
- изменились endpoint, DTO, auth contract или error shape;
- изменились `backend/docs/openapi.yaml` или backend runtime-контракты;
- изменились команды запуска, порты, env-переменные или onboarding-шаги.

Точка входа и пример вызова описаны в [.agents/README.md](.agents/README.md).

## Основные make-команды

- `make install`
- `make run`
- `make run-backend`
- `make test`
- `make test-backend`
- `make test-backend-integration`
- `make lint`
- `make lint-backend`
- `make db-up`
- `make db-down`
- `make db-reset`
- `make db-migrate`
- `make db-downgrade`
- `make db-import`
- `make db-check`
- `make db-psql`
- `make web-install`
- `make web-dev`
- `make web-build`
- `make web-lint`

## Документация

- [docs/onboarding.md](docs/onboarding.md) — пошаговый гайд для нового участника
- [docs/architecture.md](docs/architecture.md) — high-level архитектура и runtime-потоки
- [docs/vision.md](docs/vision.md) — продуктовое видение и границы системы
- [docs/plan.md](docs/plan.md) — roadmap проекта, а не operational entrypoint
- [docs/data-model.md](docs/data-model.md) — проектная модель данных и её границы
- [docs/integrations.md](docs/integrations.md) — внешние интеграции и протоколы
- [docs/tech/api-contracts.md](docs/tech/api-contracts.md) — точка входа к API-контрактам
- [docs/doc-audit.md](docs/doc-audit.md) — живой аудит документации и открытых несоответствий
- [.agents/README.md](.agents/README.md) — локальные subagent'ы и пример запуска `docs-updater`

## Источники истины

- Runtime API: `/docs`, `/openapi.json`
- Hand-written OpenAPI: `backend/docs/openapi.yaml`
- Backend contract notes: `backend/docs/api-contracts.md`
- Кодовые entrypoints:
  - `backend/src/maintenance_backend/app.py`
  - `backend/src/maintenance_backend/api/v1/router.py`
  - `src/maintenance_bot/main.py`
  - `frontend/src/lib/api/`
