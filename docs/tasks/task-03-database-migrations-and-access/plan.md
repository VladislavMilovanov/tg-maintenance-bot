# Задача 03: ADR и выбор tooling для миграций и доступа к БД

## Цель

Зафиксировать единый stack для migration/data-access слоя PostgreSQL и прекратить считать runtime `ensure_schema()` основным механизмом изменения схемы.

## Контекст

- `ADR-001` уже фиксирует PostgreSQL как primary relational store.
- `docs/data-model.md` уже описывает target logical + physical schema.
- Текущий backend по-прежнему использует `asyncpg`, hand-written repositories и startup `ensure_schema()`.
- Для следующих задач нужен один approved workflow миграций, моделей и DB access.

## Решения

- Принять `SQLAlchemy 2.x Declarative ORM + Alembic + AsyncSession`.
- Оставить repository layer поверх session layer.
- Зафиксировать `ensure_schema()` как legacy-подход переходного периода.
- Держать краткую practical guide в корневом `README.md`.
- Зафиксировать соответствие выбранного stack фактической реализации в миграциях, DB tooling и backend data layer.

## Состав работ

- Подготовить `ADR-003` с описанием alternatives, chosen stack и границ ответственности.
- Обновить реестр ADR.
- Обновить README кратким daily workflow миграций и моделей.
- Зафиксировать итоговый migration/data-access workflow и его связь с реализованными артефактами репозитория.
- Обновить `docs/tasks/tasklist-database.md` реальными артефактами и прогрессом задачи.

## Артефакты

- `docs/adr/adr-003-database-migrations-and-access.md`
- `docs/adr/README.md`
- `README.md`
- `docs/tasks/task-03-database-migrations-and-access/summary.md`

## Definition of Done

- У проекта есть один недвусмысленный migration/data-access stack.
- README объясняет target DB workflow без чтения реализации.
- `tasklist-database.md` отражает реальные артефакты и фактический статус database stage.
