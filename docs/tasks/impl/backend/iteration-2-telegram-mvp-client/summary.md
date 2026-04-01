# Итерация 2: Telegram MVP client

## Итог

Итерация завершена. Telegram-бот переведён на backend API и оформлен как thin-client поверх уже зафиксированного backend foundation.

## Что реализовано

- добавлен `maintenance_bot.backend_client.BackendClient` и убран прямой runtime-path bot -> OpenRouter;
- `handlers/chat.py` переведён на backend-owned assistant flow с локальным хранением только `conversation_id`;
- bot lifecycle обновлён: backend client создаётся один раз на процесс и закрывается при остановке polling;
- добавлены bot-тесты `tests/test_backend_client.py` и `tests/test_chat_handler.py`;
- закреплены bot-команды качества `make lint` и `make test`;
- обновлены `README.md`, `.env.example`, `docs/integrations.md`, `docs/plan.md`, `docs/how-to-get-tokens.md`, `docs/tasks/tasklist-backend.md` в части Telegram client runtime;
- выполнена интеграционная smoke-проверка client -> backend через FastAPI app и `httpx.ASGITransport`.

## Проверка

- `make lint`
- `make test`
- in-process smoke для `BackendClient -> POST /api/v1/assistant/messages -> FastAPI app`

## Текущий прогресс

- ✅ Задача 07: Рефакторинг бота на backend API.

## Ограничения

- iteration 2 не вводит auth между bot и backend;
- continuity диалога держится на `conversation_id` и не использует persistent storage вне процесса бота;
- backend-quality baseline, docs sync iteration 1 и platform-governance остаются отдельными слоями roadmap.
