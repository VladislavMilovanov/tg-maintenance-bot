# Итерация: Database stage

## Цель

Перевести backend от минимального PostgreSQL layer с runtime schema creation к управляемому data layer: зафиксировать сценарии, logical/physical schema, DB tooling strategy, затем подготовить миграции, import/seed flow и завершить repository/ORM integration для runtime backend.

## Ценность

После завершения database stage команда получает единый и проверяемый persistence layer, который:
- согласован с пользовательскими сценариями и будущим web;
- опирается на документированную relational model;
- развивается через migrations, а не ad hoc DDL на старте приложения;
- готов к следующему этапу ORM/repository integration.

## Scope

- Task 01: сценарии и data requirements;
- Task 02: logical + physical schema, ER и review gate;
- Task 03: ADR и выбор migration/data-access tooling;
- Task 04: локальная DB infrastructure, migrations, import/seed, команды;
- Task 05: ORM models, repositories и замена current minimal layer.

Вне scope:
- auth/session storage;
- assistant conversation persistence;
- incident workflow и audit log;
- production-hardening beyond documented platform readiness boundaries.

## Решения итерации

- PostgreSQL остаётся primary relational store по `ADR-001`.
- Сценарным источником истины для data requirements является `docs/spec/user-scenarios.md`.
- Core monitoring domain фиксируется в `docs/data-model.md` и `docs/diagrams/database-er.md`.
- Целевой migration/data-access stack: `SQLAlchemy 2.x Declarative + Alembic + AsyncSession + repositories`.
- Runtime `ensure_schema()` считается legacy bootstrap-подходом переходного периода.
- Согласованный migration/data-access stack должен быть подтверждён реализацией в миграциях, DB tooling и backend persistence layer.

## Состав работ

- Зафиксировать сценарии, роли и обязательные представления данных.
- Перевести доменную модель в проектную relational schema и ER.
- Выбрать и задокументировать migration/data-access tooling.
- Подготовить локальный migration/import/seed workflow и developer commands.
- Реализовать ORM/repository layer поверх зафиксированной схемы и выбранного tooling.

## Задачи

- [Задача 01: Пользовательские сценарии и требования к данным](../../task-01-user-scenarios-and-data-needs/plan.md)
- [Задача 02: Логическая и физическая схема данных, ER и schema review](../../task-02-logical-and-physical-schema/plan.md)
- [Задача 03: ADR и выбор tooling для миграций и доступа к БД](../../task-03-database-migrations-and-access/plan.md)
- Задача 04: Инфраструктура БД, миграции, import/seed и локальные команды
- Задача 05: ORM-модели, репозитории и интеграция в backend вместо текущего minimal layer

## Артефакты

- `docs/spec/user-scenarios.md`
- `docs/data-model.md`
- `docs/diagrams/database-er.md`
- `docs/adr/adr-001-database.md`
- `docs/adr/adr-003-database-migrations-and-access.md`
- `docs/tasks/tasklist-database.md`
- `compose.yaml`
- `alembic.ini`
- `alembic/`
- `data/progress-import.v1.json`
- `backend/src/maintenance_backend/db_schema.py`
- `backend/src/maintenance_backend/db_import.py`
- `backend/src/maintenance_backend/db_check.py`
- `docs/tasks/impl/database/summary.md`

## Критерии завершения

- Сценарии, схема, ADR по tooling и инфраструктурный workflow не противоречат друг другу.
- У проекта есть versioned подход к schema evolution вместо runtime `ensure_schema()`.
- Локальный DB lifecycle, import/seed и ORM/repository integration документированы и реализованы.
- `tasklist-database.md` и iteration-level артефакты отражают одинаковый фактический прогресс.

## Текущий статус

- ✅ Завершены задачи 01 и 02.
- ✅ Задача 03 завершена: документарное решение по tooling принято и подтверждено реализацией migration/data-access workflow.
- ✅ Задача 04 реализована: локальный DB lifecycle, Alembic baseline migration, import/seed flow и команды проверки добавлены в репозиторий и проверены локально.
- ✅ Задача 05 реализована: backend runtime переведён на SQLAlchemy `AsyncEngine`/`AsyncSession` + repository layer, добавлены integration tests и подтверждён persistence flow через PostgreSQL.
