# Задача 03: ADR и выбор tooling для миграций и доступа к БД

## Итог

Задача завершена.  
В проекте зафиксирован единый migration/data-access stack, и он подтверждён фактической реализацией Task 04 и Task 05.

## Что сделано

- добавлен `docs/adr/adr-003-database-migrations-and-access.md`;
- в ADR зафиксирован target stack `SQLAlchemy 2.x Declarative + Alembic + AsyncSession + repositories`;
- обновлён `docs/adr/README.md` и добавлен `ADR-003` в реестр;
- обновлён `README.md` кратким practical workflow по migration/data-access stack;
- зафиксированы границы ответственности между migrations, ORM-моделями, session layer, repositories и backend services;
- итоговый workflow подтверждён реализацией:
  - Alembic baseline migration и DB tooling из Task 04;
  - SQLAlchemy runtime data layer и repositories из Task 05;
- `tasklist-database.md` и iteration-level документы синхронизированы с фактическим состоянием репозитория.

## Принятые решения

- `ensure_schema()` больше не считается approved long-term workflow;
- schema lifecycle управляется через Alembic;
- runtime backend использует `AsyncEngine`/`AsyncSession` и repository layer;
- README и `Makefile` являются canonical entrypoint для локального DB workflow.

## Фактическое подтверждение решения

- `make db-migrate` применяет schema через Alembic;
- `make db-import` и `make db-check` подтверждают рабочий local DB workflow;
- `alembic check` не предлагает новых schema changes;
- backend persistence layer работает на PostgreSQL и проходит integration tests;
- после restart backend данные в PostgreSQL не теряются.

## Итоговый статус

- Стек выбран, задокументирован и реализован.
- Документация не противоречит коду.
- Дополнительных внешних блокеров для закрытия задачи не остаётся.
