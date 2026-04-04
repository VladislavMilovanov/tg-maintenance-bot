# ADR-003: Миграции и слой доступа к PostgreSQL

- **Статус:** Accepted
- **Дата:** 2026-04-04
- **Контекст:** переход от minimal PostgreSQL layer к управляемому data layer

---

## Контекст

После задач 01 и 02 в проекте уже зафиксированы:
- пользовательские сценарии и обязательные data requirements;
- logical + physical schema spec в `docs/data-model.md`;
- PostgreSQL как primary relational store в `ADR-001`;
- backend-first архитектура и базовый backend stack в `ADR-002`.

При этом текущая backend-реализация всё ещё использует legacy-подход:
- доступ к PostgreSQL идёт через `asyncpg`;
- схема создаётся на старте приложения через `ensure_schema()`;
- seed-справочник оборудования также создаётся в startup flow;
- SQL и persistence logic живут внутри hand-written repository adapters;
- схема не versioned через миграции и не управляется как отдельный lifecycle.

Такой подход был достаточен для bootstrap и MVP foundation, но больше не подходит как основной механизм развития схемы:
- physical schema из `docs/data-model.md` уже значительно шире текущей runtime schema;
- schema changes должны становиться повторяемыми, ревьюируемыми и откатываемыми;
- нужно разделить ответственность между schema evolution, model mapping и application services;
- проекту нужен один единый DB workflow для следующих задач.

---

## Рассмотренные альтернативы

### 1) Оставить `asyncpg + handwritten SQL + runtime schema creation`

**Плюсы:**
- минимальные изменения относительно текущего состояния;
- прозрачный SQL без дополнительного ORM abstraction layer;
- быстрый старт для маленькой схемы.

**Минусы:**
- schema evolution остаётся неуправляемой;
- миграции и rollback workflow отсутствуют;
- растёт риск drift между `docs/data-model.md`, реальной схемой и кодом;
- repository layer начинает совмещать слишком много ответственности;
- плохо масштабируется на target core domain schema.

### 2) `SQLAlchemy Core + Alembic`

**Плюсы:**
- управляемые миграции через Alembic;
- меньше ORM abstraction по сравнению с full Declarative ORM;
- удобно писать SQL-ориентированные запросы.

**Минусы:**
- менее естественное связывание целевой relational model с code-level entities;
- в проекте всё равно понадобится слой mapping и conventions поверх Core;
- для команды остаётся больше неоднозначности, где заканчивается schema layer и начинается persistence model.

### 3) `SQLAlchemy 2.x Declarative ORM + Alembic + AsyncSession`

**Плюсы:**
- даёт единый подход к моделям, связям и persistence mapping;
- хорошо сочетается с Alembic и async PostgreSQL workflow;
- естественно поддерживает repository layer поверх `AsyncSession`;
- лучше соответствует уже зафиксированной rich relational model в `docs/data-model.md`;
- упрощает постепенную замену current `asyncpg` adapters на единый ORM/session stack.

**Минусы:**
- увеличивает количество инфраструктуры и conventions;
- требует дисциплины, чтобы не смешивать ORM models и business logic;
- потребует миграции части существующего SQL-кода и startup flow.

---

## Решение

Выбираем следующий target stack для миграций и доступа к PostgreSQL:

- **SQLAlchemy 2.x Declarative ORM** как основной способ описания persistence models;
- **Alembic** как единственный approved механизм миграций схемы;
- **AsyncEngine** и **AsyncSession** для runtime-доступа к PostgreSQL;
- **repository layer** поверх session layer как стандартный способ инкапсуляции DB workflows.

Дополнительные правила:

- `ensure_schema()` на старте приложения больше не считается целевым механизмом изменения схемы;
- schema changes должны оформляться миграциями и проходить через versioned workflow;
- `docs/data-model.md` остаётся источником logical/physical schema spec, а модели и миграции должны ей следовать;
- новые schema changes после принятия ADR должны проектироваться уже под Alembic-based workflow, даже если legacy `asyncpg` слой ещё временно существует в коде.

---

## Границы ответственности

### ORM models

- описывают persistence shape, связи и column-level constraints на code level;
- не содержат бизнес-логику use case уровня;
- следуют schema spec из `docs/data-model.md`.

### Alembic migrations

- являются единственным механизмом versioned schema evolution;
- отвечают за upgrade/downgrade схемы;
- не подменяют собой domain documentation.

### Session layer

- предоставляет `AsyncEngine` и `AsyncSession`;
- инкапсулирует lifecycle подключения и транзакций;
- не содержит domain use case logic.

### Repository layer

- работает поверх `AsyncSession`;
- инкапсулирует запросы, агрегаты и persistence workflows;
- не дублирует бизнес-правила сервисов и не подменяет migration layer.

### Backend services

- реализуют business use cases;
- не работают с raw SQL и не управляют schema evolution;
- получают доступ к данным через repositories.

### App startup

- настраивает engine/session wiring;
- не должен создавать или менять production/dev schema ad hoc через runtime DDL как основной workflow.

---

## Практика перехода

Текущий код в `backend/src/maintenance_backend/database.py`, `backend/src/maintenance_backend/repositories.py` и `backend/src/maintenance_backend/app.py` считается legacy-слоем переходного периода.

Это означает:
- `asyncpg` может временно оставаться в зависимостях и коде;
- `ensure_schema()` и startup seed могут временно сосуществовать до задач 04 и 05;
- целевым направлением считается замена current approach на SQLAlchemy/Alembic stack;
- migration scaffolding, runtime wiring и code refactor выполняются следующими задачами, а не этим ADR.

---

## Обоснование

- Решение согласуется с `ADR-001`: PostgreSQL остаётся primary relational store.
- Решение согласуется с `ADR-002`: backend остаётся единым ядром, а DB tooling становится частью backend-first архитектуры.
- SQLAlchemy 2.x Declarative лучше всего подходит под уже зафиксированную relational model с actors, locations, snapshots, records и join tables.
- Alembic даёт управляемый workflow изменений схемы, которого сейчас в проекте нет.
- Async session model хорошо вписывается в текущий async FastAPI backend.
- Repository layer позволяет удержать SQL/persistence concerns отдельно от business services.

---

## Последствия

### Позитивные

- появляется единый approved DB workflow для всей команды;
- schema changes становятся versioned и reviewable;
- снижается риск drift между docs, code и реальной БД;
- следующая задача по инфраструктуре БД получает чёткую опору по tooling;
- Task 05 может реализовывать repositories и ORM models без повторного выбора стека.

### Негативные / компромиссы

- возрастёт инфраструктурная сложность backend data layer;
- часть текущего `asyncpg` кода станет transitional legacy;
- потребуются новые зависимости и conventions вокруг migrations/models/session lifecycle;
- команде придётся удерживать дисциплину, чтобы ORM models не превращались в место для бизнес-логики.

---

## Связанные документы

- `docs/adr/adr-001-database.md` — выбор PostgreSQL как основной СУБД.
- `docs/adr/adr-002-backend-stack.md` — backend stack и backend-first границы.
- `docs/data-model.md` — logical/physical schema spec для core domain.
- `README.md` — краткий daily workflow по новому DB подходу.

---

## План пересмотра

ADR пересматривается, если:

- проект отказывается от SQLAlchemy/Alembic как approved stack;
- backend перестаёт быть единым ядром persistence rules;
- появляется иное архитектурное решение для schema evolution;
- async session/repository модель перестаёт соответствовать масштабу и структуре backend.
