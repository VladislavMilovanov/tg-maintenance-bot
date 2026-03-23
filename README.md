# maintenance-bot

Telegram-бот — помощник по состоянию оборудования для сотрудников и инженеров.

## Установка

```bash
make install
```

## Запуск

1. Скопируйте `.env.example` в `.env`
2. Заполните `TELEGRAM_BOT_TOKEN` и `OPENROUTER_API_KEY`
3. Запустите бота:

```bash
make run
```

## Разработка

- `make lint` — проверка линтером (ruff)
- `make format` — форматирование кода
