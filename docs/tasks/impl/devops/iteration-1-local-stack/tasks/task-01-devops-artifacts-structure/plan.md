# Задача 01: Архитектура devops-артефактов и целевая структура `devops/`

## Цель

Зафиксировать единое место для Docker- и сопутствующих DevOps-артефактов проекта, чтобы дальнейшие задачи по образам и compose не разносили implementation-level файлы по корню репозитория.

## Ценность

После завершения задачи команда получает понятное соглашение: что запускается из корня, а что хранится в `devops/` как часть внутренней реализации контейнерного слоя.

## Scope

- фиксация структуры `devops/` и базовых подпапок по сервисам;
- выделение `devops/compose/` под shared Compose-helper artifacts;
- документирование root-level operational entrypoints;
- синхронизация DevOps-tasklist и roadmap с новой структурой.

Вне scope:
- переработка содержимого Dockerfile;
- изменение логики `compose.yaml`;
- расширение `Makefile` за пределы архитектурного описания;
- полная синхронизация общего onboarding и runtime-инструкций.

## Решения задачи

- `devops/backend/`, `devops/frontend/`, `devops/bot/` закреплены как service-specific container directories.
- `devops/compose/` закреплён как место для shared Compose-related artifacts: override-файлов, env-шаблонов, compose-fragments и helper scripts.
- В корне остаются только operator-facing entrypoints:
  - `compose.yaml`;
  - `Makefile`;
  - `.env.example`;
  - `.dockerignore`.
- Корневой `.dockerignore` не переносится в `devops/`, потому что текущая сборка использует `context: .` и ожидает root-scoped ignore rules.
- Параллельный `docker-compose.yml` не вводится, чтобы не создавать второй конкурирующий entrypoint.

## Состав работ

- Создать документационный каркас DevOps-итерации и task docs для задачи 01.
- Добавить `README`-описания для `devops/` и `devops/compose/`.
- Обновить `docs/tasks/tasklist-devops.md`: отметить задачу 01 завершённой и зафиксировать итоговую структуру.
- Обновить `docs/plan.md`, чтобы `Platform readiness` ссылалась на существующий `tasklist-devops.md`.

## Артефакты

- `devops/README.md`
- `devops/compose/README.md`
- `docs/tasks/impl/devops/iteration-1-local-stack/plan.md`
- `docs/tasks/impl/devops/iteration-1-local-stack/summary.md`
- `docs/tasks/impl/devops/iteration-1-local-stack/tasks/task-01-devops-artifacts-structure/summary.md`

## Критерии завершения

- Структура `devops/` однозначно покрывает `backend`, `frontend`, `bot` и shared Compose-artifacts.
- Для каждого root-level operational файла дано явное обоснование.
- Документация не противоречит фактическому состоянию репозитория: `devops/*/Dockerfile` уже существуют, `compose.yaml` остаётся корневым entrypoint, `.dockerignore` остаётся root-scoped.
