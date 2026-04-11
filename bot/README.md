# Telegram Bot

Telegram-слой является thin client поверх backend API.

## Где находится код

В репозитории нет отдельной папки с исходниками `bot/`. Код клиента расположен в:

- `src/maintenance_bot`

Папка `bot/` используется только для документации и onboarding-навигации.

## Зависимости

- Python `3.12+`
- `uv`
- Telegram bot token

## Настройка

1. Из корня репозитория установить зависимости:

```bash
make install
```

2. Создать `.env`:

```bash
cp .env.example .env
```

3. Заполнить минимум:
- `TELEGRAM_BOT_TOKEN`
- `BACKEND_URL` если backend работает не на `http://127.0.0.1:8000`
- `BACKEND_TIMEOUT_SECONDS` при необходимости

Для voice flow дополнительно нужны:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `WHISPER_MODEL`

## Запуск

Перед запуском бота должен работать backend.

```bash
make run
```

Команда запускает модуль `maintenance_bot` из `src/maintenance_bot`.

## Smoke-check

1. Отправить боту текстовое сообщение
2. Убедиться, что ответ приходит через backend
3. При наличии `OPENAI_API_KEY` отправить голосовое сообщение и проверить транскрибацию

Если backend недоступен, бот должен вернуть сервисное сообщение, а не падать.

## Тесты и качество

```bash
make test
make lint
```
