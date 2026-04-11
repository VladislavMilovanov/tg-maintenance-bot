# Аудит документации

Живой аудит документации проекта с точки зрения нового участника или AI-агента. Источником истины для оценки считаются код, конфиги и реально существующие команды в репозитории.

## Текущий статус

Основной onboarding-контур теперь закрыт:
- есть компактный `README.md` как entrypoint;
- есть отдельные `docs/onboarding.md` и `docs/architecture.md`;
- есть component README по backend, frontend и Telegram-слою;
- согласованы auth flow, API navigation и high-level architecture;
- roadmap и data-model документы снабжены рамкой применения.

Открытые ограничения остались только там, где они действительно существуют в коде, а не в документации.

## Приоритеты

### P0 — Поддерживать актуальность

- Единый quickstart в `README.md` должен оставаться актуальным после любых изменений команд, env и структуры каталогов.
- `docs/onboarding.md` и `docs/architecture.md` должны обновляться вместе с изменениями runtime-потоков.
- `backend/README.md`, `frontend/README.md` и `bot/README.md` должны поддерживаться как component-level документация, а не заменяться task-архивом.
- `docs/tech/api-contracts.md` должен оставаться стабильной ссылкой из общей документации на backend API contracts.
- Любая новая env-переменная должна сразу попадать в `.env.example` или в component-specific env documentation.

### P1 — Оставшиеся реальные пробелы

- Добавить automated frontend test suite. Сейчас документация честно фиксирует его отсутствие, но это остаётся инженерным пробелом проекта.
- При дальнейшей эволюции auth и data layer поддерживать синхронность `backend/docs/api-contracts.md`, `backend/docs/openapi.yaml`, `docs/integrations.md` и `docs/architecture.md`.
- Если появится полноценный tasklist для platform readiness, обновить `docs/plan.md`, чтобы там не оставались placeholder-формулировки.

### P2 — Улучшения качества документации

- Убрать или игнорировать служебный мусор вроде `docs/.DS_Store`, чтобы docs tree выглядел чище для новых участников.
- Дальше удерживать низкий уровень дублирования между `README.md`, `docs/onboarding.md` и component README.
- При следующих изменениях API синхронно обновлять `backend/docs/api-contracts.md`, `backend/docs/openapi.yaml`, `docs/tech/api-contracts.md` и `docs/architecture.md`.

## Зафиксированные расхождения с кодом

### Исправлено

- `docs/architecture.md` отсутствовал.
- `docs/onboarding.md` отсутствовал.
- `backend/docs/api-contracts.md` описывал auth response через `token`, хотя код использует `access_token` и `token_type`.
- `docs/integrations.md` утверждал, что auth между thin clients и backend пока не введён, хотя в коде есть `POST /api/v1/auth/login`, `GET /api/v1/auth/me` и frontend login flow.
- `docs/plan.md` не обозначал себя явно как roadmap, а не operational entrypoint.
- `docs/data-model.md` не объяснял, что это project-level и частично опережающий документ.

### Остаётся открытым

- Frontend automated tests в репозитории не настроены.
- `docs/plan.md` остаётся roadmap-документом с частью плановых placeholder-формулировок для будущих этапов.
- `docs/data-model.md` по-прежнему не является runtime source of truth и должен читаться как проектная модель, а не как точная схема реализации.

## Реестр документации

| Файл | Описание | Статус | Проблемы |
|------|----------|--------|----------|
| `README.md` | Единая точка входа: структура проекта, системные зависимости, quickstart, smoke-check, тесты и quality checks | ✅ Актуально | Нет |
| `docs/onboarding.md` | Основной пошаговый onboarding-гайд: setup, запуск, smoke-check, рабочий процесс и quality checks | ✅ Актуально | Нет |
| `docs/architecture.md` | High-level архитектура, компоненты, runtime-потоки и ссылки на code/doc entrypoints | ✅ Актуально | Нет |
| `backend/README.md` | Backend-only инструкция: окружение, DB workflow, запуск, smoke-check, тесты и контракты | ✅ Актуально | Нет |
| `frontend/README.md` | Frontend-only инструкция: установка, `NEXT_PUBLIC_API_URL`, запуск, smoke-check, lint/build | ✅ Актуально | Нет |
| `bot/README.md` | Документация Telegram-слоя с явным указанием, что код расположен в `src/maintenance_bot` | ✅ Актуально | Нет |
| `docs/vision.md` | Продуктовое и архитектурное видение с актуальными путями `frontend/` и `src/maintenance_bot/` | ✅ Актуально | Нет |
| `docs/plan.md` | Дорожная карта проекта и статус крупных этапов | ✅ Актуально | Это roadmap, а не operational onboarding-документ |
| `docs/data-model.md` | Проектная модель core domain и рамка её применения | ✅ Актуально | Не является runtime source of truth и описывает частично целевую модель |
| `docs/tech/api-contracts.md` | Навигационная точка входа из общего docs tree к API-контрактам | ✅ Актуально | Нет |
| `backend/docs/api-contracts.md` | Поясняющий документ по MVP API-контрактам backend | ✅ Актуально | Нет |
| `.env.example` | Основной шаблон локального окружения для bot + backend | ✅ Актуально | Frontend env хранится отдельно через `frontend/.env.local` |
| `backend/.env.example` | Справочный backend-only набор переменных | ✅ Актуально | Не является основным entrypoint для локального запуска |
| `Makefile` | Нормативный интерфейс локальных команд: install, db, backend, bot, frontend | ✅ Актуально | Нет |
| `compose.yaml` | Локальный PostgreSQL для разработки | ✅ Актуально | Нет |
| `.cursor/rules/conventions.mdc` | Правила для агентской работы и архитектурных соглашений | ✅ Актуально | Нет |
| `frontend/AGENTS.md` | Короткое правило для агентов о работе с текущей версией Next.js | ✅ Актуально | Узкоспециализированный файл, не заменяет обычную пользовательскую документацию |
| `frontend/CLAUDE.md` | Указатель на `frontend/AGENTS.md` | ✅ Актуально | Очень минималистичен, полезен только как редирект |
| `docs/integrations.md` | Внешние интеграции, каналы взаимодействия и voice/text-to-sql потоки | ✅ Актуально | Нет |
| `docs/how-to-get-tokens.md` | Получение `TELEGRAM_BOT_TOKEN` и `BACKEND_OPENROUTER_API_KEY` для локального запуска | ✅ Актуально | Не нужен для запуска frontend/backend без Telegram и LLM |
| `docs/onboarding-audit.md` | Legacy audit, сохранённый как ссылка на актуальный `docs/doc-audit.md` | ✅ Актуально | Не использовать как основной audit-файл |
| `docs/tasks/tasklist-frontend.md` | Исторический tasklist frontend-направления | ⚠️ Устарело | Это архив реализации, а не onboarding-документ |
| `docs/tasks/tasklist-backend.md` | Исторический tasklist backend-направления | ⚠️ Устарело | Это архив реализации, а не onboarding-документ |
| `docs/tasks/tasklist-database.md` | Исторический tasklist database-направления | ⚠️ Устарело | Это архив реализации, а не onboarding-документ |

## Аудит запускаемости

| Пункт | Статус | Комментарий |
|------|--------|-------------|
| Установка системных зависимостей | есть | Описана в `README.md`: Python `3.12+`, `uv`, Docker, Node `>=20`, `pnpm` |
| Настройка окружения | есть | Описана в `README.md`, `bot/README.md`, `backend/README.md`, `frontend/README.md` |
| Запуск базы данных | есть | Полный flow есть в `README.md` и `backend/README.md`: `make db-up`, `make db-migrate`, `make db-import`, `make db-check` |
| Запуск backend | есть | Описан в `README.md` и `backend/README.md`: `make run-backend`, URL и smoke endpoints указаны |
| Запуск frontend | есть | Описан в `README.md` и `frontend/README.md`: `make web-install`, `make web-dev`, `NEXT_PUBLIC_API_URL`, `http://localhost:3000` |
| Запуск бота | есть | Описан в `README.md` и `bot/README.md`: `make run`, обязательные env и зависимость от backend |
| Запуск тестов | есть | Разделён по слоям в `README.md`, `docs/onboarding.md`, `backend/README.md`, `bot/README.md`; отдельно указано отсутствие frontend test suite |
| Проверка работоспособности | есть | Описан полный smoke-flow: `/health`, `/ready`, `/docs`, login во frontend, сообщение боту |
| Проверка качества кода | есть | Описаны `make lint`, `make lint-backend`, `make web-lint`, `make web-build` |
