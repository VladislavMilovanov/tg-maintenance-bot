# Задача 08: Качество и синхронизация документации

## Цель

Закрыть quality-baseline для `Backend foundation` без расширения scope итерации: зафиксировать актуальные команды проверки, уже реализованные operational endpoint'ы и привести roadmap-документы к фактическому состоянию репозитория.

## Scope

- подтверждение существующих quality-команд для bot и backend;
- фиксация минимальной наблюдаемости iteration 1: `GET /health`, `GET /ready`, privacy-safe request logging;
- синхронизация `docs/tasks/tasklist-backend.md`, `docs/plan.md`, iteration-1 plan/summary и task-08 артефактов;
- точечная сверка `README.md`, `docs/vision.md`, `docs/data-model.md`, `docs/integrations.md`, `.env.example` с текущим кодом.

Вне scope:
- новые backend endpoint'ы и изменение OpenAPI;
- CI, деплой и расширенная platform-observability;
- auth между bot и backend;
- рефакторинг bot runtime, относящийся к iteration 2.

## Состав работ

- Подтвердить публичные команды разработки: `make run-backend`, `make lint`, `make test`, `make lint-backend`, `make test-backend`.
- Зафиксировать, что `make lint` и `make test` относятся к bot/thin-client слою, а `make lint-backend` и `make test-backend` закрывают backend foundation.
- Подтвердить наличие и назначение `GET /health`, `GET /ready` и privacy-safe request logging без текста пользовательских сообщений.
- Обновить `docs/tasks/tasklist-backend.md`, `docs/plan.md`, `docs/tasks/impl/backend/iteration-1-backend-foundation/plan.md`, `docs/tasks/impl/backend/iteration-1-backend-foundation/summary.md`.
- Оформить `plan.md` и `summary.md` задачи 08 с follow-up checklist для следующих итераций.

## Definition of Done

- iteration 1 зафиксирована как завершённая с quality-baseline и docs sync без переноса этой части в `Platform readiness`;
- tasklist, roadmap и iteration-1 артефакты одинаково отражают место задачи 08;
- документы не обещают несуществующие команды, endpoint'ы или runtime-поведение;
- отсутствие отдельного unified root-level quality pipeline признано осознанным ограничением текущего этапа.
