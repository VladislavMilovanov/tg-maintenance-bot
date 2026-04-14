# Задача 06: Docs sync for compose-first local entrypoint

## Итог

Основные entrypoint-документы синхронизированы под новый compose-first workflow.

## Что изменено

- `README.md` теперь описывает `compose.yaml` как full-stack entrypoint, а не как PostgreSQL-only файл.
- Быстрый старт переведён на `make stack-build` / `make stack-up`.
- `docs/onboarding.md` выровнен под тот же основной сценарий.
- `backend/README.md` явно говорит, что host-run backend остаётся fallback для точечной разработки.
- Новый runbook `docs/docker-compose-local.md` добавлен как source of truth для container workflow.

## Что осталось доступным

- `run`, `run-backend`, `web-dev` не удалялись;
- host-run сценарии сохранены для component-level разработки и диагностики;
- default local full-stack path теперь один и тот же во всех основных документах.
