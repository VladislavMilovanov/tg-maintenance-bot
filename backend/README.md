# Backend Local DB Notes

Backend runtime больше не должен поднимать схему PostgreSQL через startup bootstrap. Поддерживаемый локальный путь:

1. Из корня репозитория выполнить `make db-up`.
2. Применить миграции: `make db-migrate`.
3. Загрузить sample data: `make db-import`.
4. Проверить состояние БД: `make db-check`.
5. Запустить backend: `make run-backend`.

Ключевая backend-переменная:

- `BACKEND_DATABASE_URL=postgresql://postgres:postgres@localhost:55433/tg_maintenance`

Локальный Postgres для проекта публикуется через `compose.yaml` на `localhost:55433`, чтобы не конфликтовать с другими контейнерами на стандартных портах.

Полезные команды:

- `make db-up` / `make db-down`
- `make db-reset`
- `make db-migrate`
- `make db-downgrade`
- `make db-import`
- `make db-check`
- `make db-psql`
- `make test-backend-integration`

Integration-набор использует реальную PostgreSQL-схему с Alembic migrations и SQLAlchemy runtime layer. Перед запуском backend и integration tests БД должна быть уже мигрирована, а для ручных сценариев обычно ещё и заполнена через `make db-import`.
