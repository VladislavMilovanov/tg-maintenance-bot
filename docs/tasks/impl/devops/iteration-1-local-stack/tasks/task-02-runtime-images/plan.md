# Задача 02: Runtime images and build contract

## Цель

Довести уже существующие Dockerfile `backend`, `frontend` и `bot` до зафиксированного local-runtime контракта и явно описать build assumptions iteration 1.

## Решения

- Использовать review-principles из skill `docker-expert`.
- Сохранить multi-stage подход:
  - `devops/backend/Dockerfile` и `devops/bot/Dockerfile` на `python:3.12-slim`;
  - `devops/frontend/Dockerfile` на `node:20-slim` с `Next.js standalone`.
- Финальные runtime stages запускаются под `appuser`.
- Build context остаётся root-scoped: `context: .`.
- Отдельные service-level `.dockerignore` не вводятся, потому что все сервисы собираются из общего root context.
- Runtime mode для `backend`, `frontend`, `bot` в iteration 1 остаётся image-only без bind mounts.

## Состав работ

- Проверить Dockerfile на cache behavior, runtime hygiene и отсутствие секретов.
- Уточнить root `.dockerignore` под текущий build contract.
- Зафиксировать service runtime contract в summary:
  - entrypoint;
  - exposed ports;
  - обязательные env variables;
  - image-only запуск.
- Отдельно зафиксировать, что `bot` остаётся optional через compose profile.

## Артефакты

- `devops/backend/Dockerfile`
- `devops/frontend/Dockerfile`
- `devops/bot/Dockerfile`
- `.dockerignore`

## Критерии завершения

- Все три образа собираются через root compose workflow.
- Root `.dockerignore` покрывает лишние build-context данные без перехода на service-level ignore files.
- Summary явно отражает review через `docker-expert` и service runtime contract.
