# Onboarding

Пошаговый гайд для нового участника проекта. Цель документа: за один сеанс понять структуру системы, подготовить окружение, поднять локальный стек, проверить работоспособность и знать, где читать код и документы дальше.

## 1. Клонирование и первичная настройка

```bash
git clone <repo-url>
cd tg-maintenance-bot
make install
cp .env.example .env
make web-install
```

Примечания:
- `make install` рассчитан на свежий клон. Если `.venv` уже существует, команда завершится ошибкой на шаге `uv venv`; в таком случае достаточно обновить зависимости командой `uv pip install -e ".[dev]"`.
- Перед `make db-up` должен быть запущен Docker daemon, иначе `docker compose` вернёт ошибку вида `Cannot connect to the Docker daemon`.

Что нужно установить заранее:
- Python `3.12+`
- `uv`
- Docker и Docker Compose
- Node.js `>=20`
- `pnpm`

Проверить версии:

```bash
python3 --version
uv --version
docker --version
docker compose version
node -v
pnpm -v
```

## 2. Настройка каждого компонента

### Backend

Заполнить в `.env` минимум:
- `BACKEND_DATABASE_URL`
- `BACKEND_OPENROUTER_API_KEY` только если нужен штатный LLM flow без fallback

Подготовить БД:

```bash
make db-up
make db-migrate
make db-import
make db-check
```

Запустить backend:

```bash
make run-backend
```

Backend слушает `http://127.0.0.1:8000`.

### Frontend

Frontend читает `NEXT_PUBLIC_API_URL`. Для локальной разработки можно использовать:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Эта переменная хранится в `frontend/.env.local`. Если её не задать, frontend всё равно по умолчанию обращается к `http://localhost:8000`.

Запуск:

```bash
make web-dev
```

Frontend слушает `http://localhost:3000`.

### Telegram Bot

Заполнить в `.env` минимум:
- `TELEGRAM_BOT_TOKEN`
- `BACKEND_URL` если backend работает не на `http://127.0.0.1:8000`
- `BACKEND_TIMEOUT_SECONDS` при необходимости

Для voice flow дополнительно нужны:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `WHISPER_MODEL`

Запуск:

```bash
make run
```

Исходный код Telegram-клиента находится в `src/maintenance_bot`. Папка `bot/` используется только для документации.
Команда требует непустой `TELEGRAM_BOT_TOKEN`; без него приложение завершится ошибкой валидации конфигурации.

## 3. Проверка, что всё работает

### Backend smoke-check

Проверить:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/ready
```

Ожидаемые ответы:

```json
{"status":"ok"}
```

Уточнение:
- `/health` должен возвращать `{"status":"ok"}` сразу после успешного старта backend;
- `/ready` возвращает `{"status":"ok"}` только если доступен PostgreSQL;
- если backend поднят, но БД недоступна, `/ready` вернёт `503 Service Unavailable` с телом `{"code":"service_unavailable","message":"Service is not ready.","details":null,"trace_id":null}`.

Также должны открываться:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

### Frontend smoke-check

1. Открыть `http://localhost:3000`
2. Убедиться, что root ведёт на `/dashboard`
3. Выполнить login по Telegram username
4. Проверить, что открываются `/dashboard`, `/chat`, `/admin`

Факт из кода:
- login выполняется через `POST /api/v1/auth/login`;
- backend возвращает bearer token как `access_token`;
- пользователь затем читается через `GET /api/v1/auth/me`.

### Telegram Bot smoke-check

1. Убедиться, что backend уже работает
2. Отправить боту текстовое сообщение
3. Проверить, что бот отвечает
4. При наличии `OPENAI_API_KEY` отправить voice message и проверить транскрибацию

Ожидаемое поведение:
- если backend недоступен, бот возвращает сервисное сообщение;
- если `BACKEND_OPENROUTER_API_KEY` не задан, assistant flow должен использовать fallback;
- если `OPENAI_API_KEY` не задан, voice flow недоступен, но текстовый сценарий остаётся рабочим.

### Какие проверки требуют секретов

- `make test-backend` не требует реальных Telegram/OpenRouter ключей
- `make test` для bot-тестов не требует реального Telegram runtime
- Telegram runtime требует `TELEGRAM_BOT_TOKEN`
- voice flow требует `OPENAI_API_KEY`
- штатный backend assistant flow требует `BACKEND_OPENROUTER_API_KEY`, иначе будет fallback

## 4. Куда смотреть в первую очередь

Документы:
- `README.md` — быстрый вход
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

## 5. Рабочий процесс

В проекте принята схема проектирования и реализации через документы:
- `docs/plan.md` — roadmap на уровне крупных этапов;
- iteration/task `plan.md` — план конкретной итерации или задачи;
- iteration/task `summary.md` — итог выполненной работы.

Важно:
- это исторические и проектные артефакты;
- они полезны для понимания эволюции системы;
- они не являются основным onboarding source of truth;
- для первого входа используйте `README.md`, `docs/onboarding.md`, `docs/architecture.md` и актуальные component README.

## 6. Как готовить изменения

Перед изменениями полезно сначала поднять локальный стек, а перед завершением прогнать проверки качества.

Если изменение затрагивает backend API, OpenAPI, auth flow, env-переменные, команды запуска или smoke-check, перед завершением работы нужно прогнать документарную сверку через локальный subagent `docs-updater`.

Минимальное правило:
- backend/API change -> проверить `backend/docs/api-contracts.md`, `docs/tech/api-contracts.md`, `docs/onboarding.md`;
- startup/env/workflow change -> проверить `README.md`, `backend/README.md`, `docs/onboarding.md`.

Пример prompt:

```text
Use $docs-updater to inspect the current diff, identify documentation drift, and update docs/tech/api-contracts.md plus any affected onboarding sections.
```

### Telegram-клиент

```bash
make lint
make test
```

### Backend

```bash
make lint-backend
make test-backend
BACKEND_DATABASE_URL=postgresql://postgres:postgres@localhost:55433/tg_maintenance make test-backend-integration
```

### Frontend

```bash
make web-lint
make web-build
```

Текущее состояние frontend quality strategy:
- отдельный automated test suite для frontend пока не настроен;
- текущие обязательные проверки — `web-lint`, `web-build` и ручной smoke-check.
