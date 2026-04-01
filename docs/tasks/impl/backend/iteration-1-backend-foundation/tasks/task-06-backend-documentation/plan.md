# Задача 06: Документация backend

## Цель

Финализировать backend foundation на уровне документации: зафиксировать единый сценарий локального запуска, актуальный набор env-переменных, способ просмотра OpenAPI и статус итерации без изменения backend-контрактов и логики.

## Scope

- синхронизация `README.md` как основного entrypoint для локального запуска backend;
- выравнивание корневого `.env.example` и `backend/.env.example` по фактическому runtime-контракту `maintenance_backend.config.Settings`;
- уточнение `docs/integrations.md` по thin-client взаимодействию bot/web с backend;
- обновление roadmap-статуса в `docs/plan.md` и tasklist-статуса в `docs/tasks/tasklist-backend.md`;
- оформление task-артефактов задачи 06.

Вне scope:
- изменение endpoint'ов, DTO, кодов ошибок и OpenAPI-контракта;
- рефакторинг Telegram-бота на backend API;
- добавление аутентификации между клиентами и backend.

## Состав работ

- Обновить `README.md`: запуск backend как отдельного процесса, шаги `make install` → `.env` → PostgreSQL → `make run-backend`, operational/OpenAPI URL и backend quality commands.
- Зафиксировать fallback-поведение assistant flow при отсутствии `BACKEND_OPENROUTER_API_KEY` или недоступности OpenRouter.
- Привести `.env.example` и `backend/.env.example` к одному backend-набору переменных без устаревших backend aliases.
- Уточнить в `docs/integrations.md` dev base URL `http://127.0.0.1:8000`, thin-client модель и отсутствие client-to-backend auth в MVP.
- Обновить `docs/plan.md`, итерационный summary и `docs/tasks/tasklist-backend.md` до статуса `Done`.
- Создать `plan.md` и `summary.md` задачи 06.

## Definition of Done

- Новый разработчик может поднять backend и найти OpenAPI, не читая код.
- Все документированные backend env keys совпадают с `backend/src/maintenance_backend/config.py`.
- `README.md`, `docs/integrations.md`, `docs/plan.md`, итерационный summary и `tasklist-backend.md` не расходятся по статусу iteration 1.
