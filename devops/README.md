# DevOps Artifacts

`devops/` хранит implementation-level Docker и Compose artifacts проекта.

## Структура

- `backend/` — Dockerfile и будущие backend-specific container helpers.
- `frontend/` — Dockerfile и будущие frontend-specific container helpers.
- `bot/` — Dockerfile и будущие bot-specific container helpers.
- `compose/` — shared Compose-related artifacts: override-файлы, env-шаблоны, compose-fragments и helper scripts.

## Правило размещения

В корне репозитория остаются только operator-facing entrypoints:

- `compose.yaml`
- `Makefile`
- `.env.example`
- `.dockerignore`

Все implementation-level Docker/Compose artifacts добавляются в `devops/` по принадлежности, а не в корень репозитория.

## Registry runtime

- `devops/compose/compose.registry.yaml` хранит registry override для запуска `backend`, `frontend` и `bot` на образах из GHCR.
- Root `compose.yaml` остаётся основным entrypoint; registry-mode включается только через compose merge или соответствующие `make`-команды.
