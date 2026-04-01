# Итерация 0: Backend bootstrap

## Цель

Зафиксировать технологическую и архитектурную основу backend до начала проектирования API и реализации сервиса.

## Ценность

После завершения итерации команда использует единое решение по стеку, структуре репозитория и инженерным соглашениям для backend-first разработки.

## Scope

- backend-стек MVP и минимальный набор инструментов;
- ADR по стеку и границам ответственности backend;
- conventions для backend-first структуры репозитория;
- синхронизация roadmap и backend-tasklist с появлением итерации 0.

Вне scope:
- проектирование endpoint'ов и контрактов API;
- создание каталога `backend/` и исполняемого сервиса;
- тесты backend и рефакторинг Telegram-бота.

## Решения итерации

- Runtime: Python 3.12+.
- Управление окружением и запуском: `uv`.
- HTTP API framework: FastAPI.
- Конфигурация: `pydantic-settings`.
- Тестовый стек для backend: `pytest` + `httpx`/`TestClient`.
- Статический анализ и форматирование: `ruff`.
- Точка входа инженерных сценариев: `make`.

## Состав работ

- Создать `ADR-002` по backend-стеку и thin-clients подходу.
- Создать `.cursor/rules/conventions.mdc` под backend-first контур.
- Описать итерацию 0 и задачу 01 в структуре `docs/tasks/impl/backend/`.
- Синхронизировать `docs/plan.md`, `docs/vision.md`, `docs/adr/README.md` и `docs/tasks/tasklist-backend.md`.

## Задачи

- [Задача 01: Стек, ADR, conventions](tasks/task-01-backend-stack-conventions/plan.md)

## Артефакты

- `docs/adr/adr-002-backend-stack.md`
- `.cursor/rules/conventions.mdc`
- `docs/tasks/impl/backend/iteration-0-backend-bootstrap/tasks/task-01-backend-stack-conventions/plan.md`

## Критерии завершения

- Стек backend и границы ответственности backend зафиксированы без противоречий `vision.md`.
- `tasklist-backend.md` явно связывает задачу 01 с итерацией 0.
- В roadmap есть подготовительная итерация 0 перед `Backend foundation`.
