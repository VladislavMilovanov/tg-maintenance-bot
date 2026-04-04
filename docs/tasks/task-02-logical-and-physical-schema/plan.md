# Задача 02: Логическая и физическая схема данных, ER и schema review

## Цель

Перевести сценарную и доменную модель в проектную logical + physical schema spec для PostgreSQL и зафиксировать отдельный ER-артефакт вместе с обязательным schema review gate.

## Контекст

- Task 01 уже зафиксировал сценарии, роли и обязательные data requirements.
- В коде backend сейчас существует только минимальная runtime schema: `equipment` и `equipment_state_records`.
- Для следующих задач миграций и ORM нужен документированный целевой core domain schema design.

## Решения

- Ограничить physical scope core domain сущностями без conversation/auth/platform storage.
- Использовать одну таблицу `system_actors` для owner, author и reviewer.
- Использовать adjacency-list модель `locations`.
- Нормализовать sensor context через join tables.
- Хранить минимальный review inside `equipment_state_records`.
- Оставить отдельный physical ER-артефакт в `docs/diagrams/database-er.md`.
- Расширить `docs/adr/adr-001-database.md` как архитектурную опору, но не превращать ADR в схему.

## Состав работ

- Пересобрать `docs/data-model.md` как logical + physical schema spec.
- Зафиксировать таблицы, PK/FK, enum-наборы, индексы и legacy transition.
- Создать `docs/diagrams/database-er.md` с Mermaid ER-диаграммой.
- Добавить обязательный внешний review gate через `postgresql-table-design` и внутренний self-checklist.
- Синхронизировать `docs/adr/adr-001-database.md` с новой схемной стратегией.

## Артефакты

- `docs/data-model.md`
- `docs/diagrams/database-er.md`
- `docs/adr/adr-001-database.md`
- `docs/tasks/task-02-logical-and-physical-schema/summary.md`

## Definition of Done

- В `docs/data-model.md` есть logical и physical модель, пригодная для проектирования миграций.
- ER-диаграмма вынесена в отдельный артефакт и соответствует текстовой схеме.
- В документации явно зафиксирован внешний schema review gate.
- Целевая схема не конфликтует с текущими MVP API-контрактами и существующей minimal runtime schema.
