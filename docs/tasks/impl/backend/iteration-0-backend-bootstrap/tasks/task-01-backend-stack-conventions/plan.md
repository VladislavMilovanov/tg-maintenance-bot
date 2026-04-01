# Задача 01: Стек, ADR, conventions

## Цель

Зафиксировать backend-стек MVP, оформить архитектурное решение в ADR и ввести conventions для последующих backend-задач.

## Контекст

- В репозитории уже реализован Telegram-бот на Python 3.12 с прямым вызовом OpenRouter.
- `backend/` как исполняемый сервис еще отсутствует.
- `docs/vision.md` уже фиксирует backend-first модель, но не закрепляет стек и инженерные соглашения.
- `.cursor/rules/conventions.mdc` в проекте отсутствует и должен быть создан с нуля.

## Решения

- Зафиксировать FastAPI как базовый framework для backend API.
- Зафиксировать `uv` как основной инструмент для установки зависимостей и запуска Python-команд.
- Зафиксировать `pydantic-settings` для env-конфигурации и `ruff` для линта/форматирования.
- Зафиксировать будущие команды `make install`, `make run-backend`, `make test-backend`, `make lint-backend` как стандартные точки входа.
- Зафиксировать thin-clients подход: `bot` и будущий `web` не держат доменную логику вне backend API.

## Состав работ

- Подготовить `ADR-002` со стеком, альтернативами и последствиями выбора.
- Создать `.cursor/rules/conventions.mdc` с правилами структуры, env-конфига и команд.
- Обновить `docs/vision.md` ссылкой на новый ADR backend-стека.
- Обновить `docs/plan.md` и `docs/tasks/tasklist-backend.md`, чтобы явно отразить итерацию 0.
- Добавить задачу 01 в структуру `docs/tasks/impl/backend/iteration-0-backend-bootstrap/`.

## Артефакты

- `docs/adr/adr-002-backend-stack.md`
- `.cursor/rules/conventions.mdc`
- `docs/tasks/impl/backend/iteration-0-backend-bootstrap/plan.md`

## Definition of Done

- `ADR-002` добавлен в реестр ADR и не конфликтует с `ADR-001`.
- `conventions.mdc` описывает backend-first структуру и согласованные инструменты.
- `plan.md`, `vision.md` и `tasklist-backend.md` используют одну и ту же трактовку итерации 0.
- Scope задачи ограничен bootstrap-уровнем и не включает реализацию endpoint'ов.
