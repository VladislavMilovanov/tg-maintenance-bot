# Итерация: Database stage

## Итог

Итерация завершена по implementation scope: завершены задачи 01, 02, 03, 04 и 05.  
Backend переведён на PostgreSQL-backed runtime data layer с управляемыми миграциями, import/seed workflow и SQLAlchemy repository integration.

## Что реализовано

- зафиксирован сценарный слой данных в `docs/spec/user-scenarios.md` и синхронизирован с `docs/vision.md`, `docs/data-model.md` и `backend/docs/api-contracts.md`;
- подготовлены logical + physical schema spec и отдельный ER-артефакт `docs/diagrams/database-er.md`;
- зафиксирован target stack в `docs/adr/adr-003-database-migrations-and-access.md`: `SQLAlchemy 2.x + Alembic + AsyncSession + repositories`;
- добавлены `compose.yaml`, `alembic.ini`, `alembic/` и baseline migration `20260404_0001` для physical schema из `docs/data-model.md`;
- добавлены `make`-команды `db-up`, `db-down`, `db-reset`, `db-migrate`, `db-downgrade`, `db-import`, `db-check`, `db-psql`;
- добавлен versioned import template/sample dataset `data/progress-import.v1.json`;
- добавлены DB tooling-модули `backend/src/maintenance_backend/db_schema.py`, `db_urls.py`, `db_import.py`, `db_check.py`;
- backend startup больше не использует runtime `ensure_schema()` и startup seed как основной механизм подготовки БД;
- backend runtime переведён на `AsyncEngine`/`AsyncSession` и SQLAlchemy ORM/repositories для `equipment`, `system_actors` и `equipment_state_records`;
- добавлены integration tests на реальной PostgreSQL-схеме для readiness и persistence сценариев;
- `db_schema.py` синхронизирован с baseline migration по индексам и `UniqueConstraint`, поэтому Alembic autogenerate/check больше не даёт ложных schema diff;
- обновлены `README.md`, `backend/README.md`, `.env.example`, `backend/.env.example` под новый DB/backend workflow.

## Что проверено

- `make db-up`
- `make db-migrate`
- `make db-downgrade`
- повторный `make db-migrate`
- `make db-import`
- `make db-check`
- `make backend-test`
- `make backend-lint`
- `make test-backend-integration`
- `alembic check` на локальной PostgreSQL: `No new upgrade operations detected`
- ручной `POST /api/v1/equipment-state-records` на работающем backend
- сохранность записи в `equipment_state_records` после restart backend

## Текущий прогресс

- ✅ Задача 01: Пользовательские сценарии и требования к данным.
- ✅ Задача 02: Логическая и физическая схема данных, ER и schema review.
- ✅ Задача 03: ADR и выбор tooling для миграций и доступа к БД.
- ✅ Задача 04: Инфраструктура БД, миграции, import/seed и локальные команды.
- ✅ Задача 05: ORM-модели, репозитории и интеграция в backend вместо текущего minimal layer.

## Ограничения

- assistant conversation storage по-прежнему реализован как in-memory TTL store и не входит в persistence scope текущего database stage;
- локальный `backend/.env` создан для runtime DSN, но остаётся git-ignored как локальный конфигурационный файл.

## Следующий фокус

- отдельно планировать follow-up задачи, если потребуется персистентное хранение assistant conversations или расширение ORM-покрытия на остальные таблицы physical schema.
