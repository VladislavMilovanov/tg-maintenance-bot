# Frontend

Next.js web-клиент для ролей инженера и администратора. Frontend использует backend API и не дублирует бизнес-логику.

## Что находится в папке

- приложение: `frontend/src/app`
- UI-компоненты: `frontend/src/components`
- API client: `frontend/src/lib/api`
- auth context: `frontend/src/lib/auth`

## Зависимости

- Node.js `>=20`
- `pnpm`

## Установка

Из корня репозитория:

```bash
make web-install
```

Или напрямую:

```bash
cd frontend
pnpm install
```

## Окружение

Frontend читает:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Для локальной разработки можно использовать `frontend/.env.local`. Если переменная не задана, клиент всё равно по умолчанию смотрит в `http://localhost:8000`.

## Запуск

Из корня репозитория:

```bash
make web-dev
```

Или напрямую:

```bash
cd frontend
pnpm dev
```

Приложение будет доступно на `http://localhost:3000`.

## Что проверить вручную

После старта backend и frontend:

1. Открыть `http://localhost:3000`
2. Войти по Telegram username
3. Проверить страницы:
   - `/dashboard`
   - `/chat`
   - `/admin`

Если backend запущен на другом адресе, обновите `NEXT_PUBLIC_API_URL`.

## Проверки качества

```bash
make web-lint
make web-build
```

Линт использует `eslint`, а `web-build` проверяет, что приложение собирается.

## Тесты

Отдельный frontend test suite в текущем репозитории не настроен. Для web-слоя сейчас доступны только ручной smoke-check, `web-lint` и `web-build`.
