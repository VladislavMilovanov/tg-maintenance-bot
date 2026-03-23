# Как получить токены для бота

Краткая инструкция по получению Bot Token (Telegram) и API Key (OpenRouter).

---

## 1. Токен Telegram-бота (BotFather)

1. Откройте Telegram и найдите **@BotFather** (официальный аккаунт с синей галочкой).
2. Отправьте команду `/newbot`.
3. Введите **имя бота** (любое, например «Мой помощник»).
4. Введите **username бота** — должен заканчиваться на `bot` или `_bot` (например, `my_helper_bot`).
5. BotFather пришлёт **токен** вида `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`.
6. Сохраните токен в `.env` в переменную `BOT_TOKEN`.

**Полезные команды BotFather:**
- `/token` — показать или перегенерировать токен
- `/mybots` — список ваших ботов
- `/revoke` — отозвать текущий токен (если он скомпрометирован)

**Официальная документация:** [core.telegram.org/bots](https://core.telegram.org/bots)

---

## 2. API Key OpenRouter

1. Перейдите на [openrouter.ai](https://openrouter.ai).
2. Нажмите **Sign in** и войдите через Google, Discord или email.
3. Откройте раздел **Keys** в личном кабинете или по ссылке: [openrouter.ai/keys](https://openrouter.ai/keys).
4. Нажмите **Create Key** (или аналогичную кнопку).
5. Задайте имя ключа (например, `tg-bot`) и при необходимости лимиты.
6. Скопируйте сгенерированный **API Key** — он показывается только один раз.
7. Сохраните ключ в `.env` в переменную `OPENROUTER_API_KEY`.

**Примечание:** OpenRouter даёт бесплатные кредиты для тестирования. Для продакшена может потребоваться привязка способа оплаты.

**Документация:** [openrouter.ai/docs](https://openrouter.ai/docs)

---

## Пример `.env`

```
BOT_TOKEN=ваш_токен_от_BotFather
OPENROUTER_API_KEY=ваш_ключ_от_OpenRouter
```

Не публикуйте `.env` в репозиторий — добавьте его в `.gitignore`.
