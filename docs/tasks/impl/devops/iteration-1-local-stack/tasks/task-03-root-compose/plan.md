# Задача 03: Root compose as the only local full-stack entrypoint

## Цель

Закрепить `compose.yaml` в корне как единственный основной entrypoint локального полного стека и убрать устаревшее восприятие файла как DB-only.

## Решения

- Основной compose entrypoint остаётся `compose.yaml`.
- Новый `docker-compose.yml` не вводится.
- Default stack включает `postgres`, `backend`, `frontend`.
- `bot` остаётся optional service через profile `bot`.
- Startup ordering фиксируется только там, где нужен:
  - `backend` <- healthy `postgres`;
  - `frontend` <- healthy `backend`;
  - `bot` <- healthy `backend`.
- Healthchecks сохраняются для `postgres` и `backend`; для `frontend` и `bot` не добавляются.

## Состав работ

- Проверить фактический compose contract и его соответствие iteration 1.
- Обновить tasklist и docs, чтобы root compose больше не описывался как postgres-only.
- Явно зафиксировать default запуск и запуск с `COMPOSE_PROFILES=bot`.
- Зафиксировать, что registry-image mode остаётся scope iteration 2.

## Артефакты

- `compose.yaml`
- `docs/tasks/tasklist-devops.md`

## Критерии завершения

- `compose.yaml` однозначно описан как full-stack entrypoint.
- Нет конкурирующего main compose entrypoint.
- Docs и summary отражают default stack и bot profile как части одного контракта.
