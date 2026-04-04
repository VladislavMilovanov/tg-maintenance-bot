# Задача 02: Логическая и физическая схема данных, ER и schema review

## Итог

Задача завершена.

## Что сделано

- `docs/data-model.md` переведён в logical + physical schema spec для core monitoring domain;
- зафиксированы таблицы, PK/FK, enum-значения, join tables, базовые индексы и mapping к текущим MVP DTO;
- отдельно создана physical ER-диаграмма в `docs/diagrams/database-er.md`;
- добавлен раздел про legacy runtime schema и переход к целевой модели;
- добавлен обязательный schema review gate через `postgresql-table-design` и внутренний checklist;
- `docs/adr/adr-001-database.md` расширен как архитектурная опора для PostgreSQL как primary transactional store.

## Принятые решения

- physical scope ограничен core domain без conversation/auth/platform storage;
- actor layer проектируется через единую таблицу `system_actors`;
- иерархия локаций строится через `locations.parent_location_id`;
- sensor context для snapshots и records нормализован через join tables;
- review хранится минимально внутри `equipment_state_records` без отдельной review history table.
