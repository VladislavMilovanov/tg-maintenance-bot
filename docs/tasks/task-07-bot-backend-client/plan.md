# Задача 07: Рефакторинг Telegram-бота на backend API

## Цель

Убрать прямой вызов OpenRouter из Telegram-бота и перевести assistant flow на единый backend endpoint `POST /api/v1/assistant/messages` без потери текущего UX чата.

## Scope

- добавить async HTTP-клиент backend в runtime бота;
- перевести chat handler на backend API и хранение только `conversation_id` по `telegram user_id`;
- обновить env-contract и lifecycle бота под новый backend-first сценарий;
- добавить bot-тесты для client и handler flow;
- синхронизировать `README.md`, `.env.example`, `docs/integrations.md`, `docs/plan.md`, `docs/tasks/tasklist-backend.md`.

Вне scope:
- изменение backend DTO, endpoint'ов и OpenAPI;
- добавление auth между bot и backend;
- расширение Telegram UX beyond текущий текстовый assistant flow.

## Состав работ

- Добавить `maintenance_bot.backend_client.BackendClient` на `httpx.AsyncClient` с нормализацией timeout/network/http ошибок.
- Обновить `maintenance_bot.config.Settings`: ввести `BACKEND_URL`, `BACKEND_TIMEOUT_SECONDS`, удалить bot OpenRouter settings.
- Переподключить `maintenance_bot.handlers.chat` на backend client вместо `maintenance_bot.llm.client.complete`.
- Передавать backend client через dispatcher context и закрывать его при shutdown polling.
- Обновить корневой `README.md` и `.env.example` под связку `make run-backend` -> `make run`.
- Добавить bot-тесты и make-target `make test`.
- Зафиксировать завершение задачи 07 и iteration 2 в проектной документации.

## Definition of Done

- бот отвечает через backend на те же типы текстовых сообщений, что и до рефакторинга;
- прямой runtime-path bot -> LLM отсутствует;
- bot runtime env не требует OpenRouter keys;
- bot-тесты проходят, документация соответствует фактическому запуску.
