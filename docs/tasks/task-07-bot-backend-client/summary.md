# Задача 07: Рефакторинг Telegram-бота на backend API

## Итог

Задача завершена. Telegram-бот переведён на thin-client модель и использует backend API как единую точку assistant flow.

## Что сделано

- добавлен `maintenance_bot.backend_client.BackendClient` на `httpx.AsyncClient` с базовым URL, timeout и нормализацией backend/network ошибок;
- `maintenance_bot.handlers.chat` больше не вызывает OpenRouter напрямую и отправляет сообщения в `POST /api/v1/assistant/messages`;
- локальное состояние бота сокращено до хранения backend-issued `conversation_id` по `telegram user_id`;
- bot runtime переведён на env `BACKEND_URL` и `BACKEND_TIMEOUT_SECONDS`; bot-specific OpenRouter settings удалены;
- lifecycle polling обновлён: backend client создаётся один раз на процесс и закрывается при shutdown;
- добавлены bot-тесты для backend client и chat handler, а также make-цель `make test`;
- синхронизированы `README.md`, `.env.example`, `docs/integrations.md`, `docs/plan.md` и `docs/tasks/tasklist-backend.md`.

## Проверка

- `make lint`
- `make test`
- `make test-backend`

## Принятые решения

- Telegram-бот не хранит локальную историю сообщений и не пересылает её в backend; continuity диалога держится на `conversation_id`;
- при недоступности backend бот отвечает единым сервисным сообщением и не пытается вызвать LLM напрямую;
- iteration 2 зафиксирована в `docs/plan.md` через текущий `tasklist-backend.md` до появления отдельного `tasklist-bot.md`.
