# Итерация 2: Telegram MVP client

## Цель

Вывести Telegram-бота на работу через backend API: убрать прямой runtime-вызов LLM из bot-кода и сохранить UX диалога.

## Ценность

После завершения итерации Telegram становится первым thin client поверх backend-ядра: доменная логика и assistant flow централизованы в backend, а бот остаётся лёгким клиентским каналом.

## Scope

- рефакторинг bot runtime на вызов `POST /api/v1/assistant/messages`;
- локальное хранение только `conversation_id` по `telegram user_id`;
- async lifecycle backend client внутри aiogram polling;
- bot-тесты и smoke-проверка интеграции client -> backend;
- синхронизация `README.md`, `.env.example`, `docs/integrations.md`, `docs/plan.md`, `docs/tasks/tasklist-backend.md` только в части bot runtime.

Вне scope:
- новые backend endpoint'ы и изменение OpenAPI;
- аутентификация между bot и backend;
- web-клиент и интеграции внешних источников мониторинга.

## Решения итерации

- Telegram-бот не вызывает OpenRouter напрямую; весь assistant flow остаётся backend-owned.
- Bot runtime использует отдельный `maintenance_bot.backend_client.BackendClient` на `httpx.AsyncClient`.
- Непрерывность диалога обеспечивается backend-issued `conversation_id`, а не локальной историей сообщений в боте.
- Проверки качества bot runtime опираются на `make lint` и `make test`; backend-quality baseline остаётся частью iteration 1.
- Интеграционный smoke выполняется через in-process FastAPI app и `httpx.ASGITransport`, без отдельной сетевой инфраструктуры.

## Состав работ

- Реализовать HTTP-клиент backend в `src/maintenance_bot/` и переподключить chat handler на backend API.
- Обновить bot env-contract: `BACKEND_URL`, `BACKEND_TIMEOUT_SECONDS`; удалить bot-specific OpenRouter runtime settings.
- Добавить bot-тесты для client и handler flow.
- Синхронизировать README, `.env.example`, `docs/integrations.md`, `docs/plan.md` и `docs/tasks/tasklist-backend.md` в части Telegram client runtime.
- Зафиксировать task-артефакты задачи 07 и iteration-level summary.

## Задачи

- [Задача 07: Рефакторинг бота на backend API](../../task-07-bot-backend-client/plan.md)

## Артефакты

- `src/maintenance_bot/backend_client.py`
- `tests/test_backend_client.py`
- `tests/test_chat_handler.py`
- `docs/tasks/task-07-bot-backend-client/plan.md`
- `docs/tasks/task-07-bot-backend-client/summary.md`
- `docs/tasks/impl/backend/iteration-2-telegram-mvp-client/summary.md`

## Критерии завершения

- Telegram-бот отвечает на пользовательские сообщения через backend API без прямого вызова LLM.
- Команды качества bot runtime проходят на локальном окружении; backend-quality baseline уже зафиксирован в iteration 1.
- Документы и tasklist отражают закрытие iteration 2 без противоречий.

## Текущий статус

- ✅ Завершена задача 07.
- ✅ Итерация 2 закрыта: bot client работает через backend API и документирован как отдельный thin-client слой.
