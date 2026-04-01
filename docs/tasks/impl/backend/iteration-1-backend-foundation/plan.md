# Итерация 1: Backend foundation

## Цель

Сформировать backend как единое ядро бизнес-логики системы мониторинга: зафиксировать API-контракты, подготовить каркас сервиса, базовые тесты, основу для реализации endpoint'ов и финальный quality-baseline с синхронизацией документации.

## Ценность

После завершения итерации команда получает стабильный backend-контур, на который можно опирать Telegram-бота, будущий web-клиент и дальнейшие интеграции без дублирования доменной логики.

## Scope

- API-контракты двух MVP-сценариев: вопрос ассистенту и фиксация состояния оборудования;
- backend-каркас, конфигурация и make-команды;
- baseline API-тесты для обоих сценариев;
- реализация endpoint'ов и минимальной серверной логики;
- документация backend: запуск, env, OpenAPI и инженерные команды;
- финальная синхронизация quality-команд, operational endpoint'ов и roadmap-документов.

Вне scope:
- рефакторинг Telegram-бота на backend API;
- web-клиент и его контракты сверх двух базовых сценариев;
- глубокие интеграции с внешними источниками мониторинга и platform-governance слой.

## Решения итерации

- Источник истины для контрактов: `backend/docs/openapi.yaml`.
- Backend оформляется как отдельный FastAPI-сервис в `backend/` с `src`-layout и пакетом `maintenance_backend`.
- Базовые MVP endpoint'ы:
  - `POST /api/v1/assistant/messages`
  - `POST /api/v1/equipment-state-records`
- Assistant flow остаётся backend-owned: история диалога, fallback и вызов LLM управляются на стороне backend.
- State-record flow в MVP минимален: оборудование, статус, комментарий, время наблюдения, канал и автор.
- Единая форма ошибок API: `code`, `message`, `details?`, `trace_id?`.
- Инженерные команды backend фиксируются в корневом `Makefile`: `make run-backend`, `make lint-backend`, `make test-backend`.
- Финализация iteration 1 включает task 08: фиксацию текущего quality-baseline и docs sync без переноса этой части в `Platform readiness`.

## Состав работ

- Зафиксировать контракты сценариев и синхронизировать `data-model.md` и `integrations.md`.
- Подготовить backend-каркас и baseline API-тесты для новых endpoint'ов.
- Реализовать endpoint'ы и backend-логику по принятым контрактам, включая PostgreSQL-backed state-record flow, OpenRouter gateway, fallback и readiness-check.
- Обновить README, `.env.example`, OpenAPI-описание и backend-команды.
- Поддерживать `docs/tasks/tasklist-backend.md` синхронно с фактическим прогрессом задач итерации.
- Зафиксировать task 08 артефактами и синхронизировать iteration-level документы с фактическим quality-baseline.

## Задачи

- [Задача 02: API-контракты двух сценариев](tasks/task-02-api-contracts-two-scenarios/plan.md)
- [Задача 03: Каркас backend-сервиса](tasks/task-03-backend-skeleton/plan.md)
- [Задача 04: Базовые API-тесты backend](tasks/task-04-api-tests-baseline/plan.md)
- [Задача 05: Реализация endpoint'ов и логики](tasks/task-05-api-implementation/plan.md)
- [Задача 06: Документация backend](tasks/task-06-backend-documentation/plan.md)
- [Задача 08: Качество и синхронизация документации](../../task-08-quality-and-docs-sync/plan.md)

## Артефакты

- `backend/docs/openapi.yaml`
- `backend/docs/api-contracts.md`
- `backend/src/maintenance_backend/`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-02-api-contracts-two-scenarios/plan.md`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-03-backend-skeleton/plan.md`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-04-api-tests-baseline/plan.md`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-05-api-implementation/plan.md`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-05-api-implementation/summary.md`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-06-backend-documentation/plan.md`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-06-backend-documentation/summary.md`
- `docs/tasks/task-08-quality-and-docs-sync/plan.md`
- `docs/tasks/task-08-quality-and-docs-sync/summary.md`

## Критерии завершения

- Контракты двух сценариев, backend-каркас, baseline тесты, реализация и документация согласованы между собой.
- Backend становится единой точкой входа для thin clients по базовым MVP-сценариям.
- `tasklist-backend.md` и артефакты итерации 1 отражают одинаковый фактический прогресс.
- quality-baseline iteration 1 зафиксирован без переноса этой части в `Platform readiness`.

## Текущий статус

- ✅ Завершены задачи 02, 03, 04, 05, 06 и 08.
- ✅ Итерация 1 закрыта: backend documentation, quality baseline и roadmap-синхронизация согласованы между собой.
