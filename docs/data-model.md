# Модель данных системы мониторинга оборудования

Документ фиксирует logical + physical schema spec для core domain задачи 02.  
Уровень описания: проектный, без миграций и ORM-реализации, но с достаточной детализацией для проектирования PostgreSQL-схемы.

Источником пользовательских потоков для этой модели является `docs/spec/user-scenarios.md`.

---

## Назначение документа

Этот документ нужен как единый источник проектных решений для:
- logical model предметной области;
- physical schema PostgreSQL для core monitoring domain;
- будущих миграций и repository/ORM слоя;
- сверки между `user-scenarios`, `api-contracts` и целевой схемой хранения.

Документ не меняет текущие HTTP DTO и не заменяет OpenAPI.  
Он фиксирует, какие таблицы, связи и ограничения должны появиться в data layer.

---

## Границы текущего этапа

В scope Task 02 входит только core domain:
- actors;
- locations;
- equipment;
- sensors и sensor groups;
- data sources;
- current state snapshots;
- state records;
- knowledge items.

Вне scope Task 02:
- assistant conversation persistence;
- auth/session storage;
- incident/case workflow;
- audit log;
- multi-step approval;
- raw telemetry/time-series storage;
- ORM-модели и миграции.

---

## Ключевые термины

### Current State Snapshot

Актуальное или историческое представление состояния оборудования, полученное из внешнего источника, импорта или backend-derived расчёта.  
Именно snapshot отвечает на вопрос "что происходит с оборудованием сейчас".

### State Record

Историческая запись наблюдения или оценки, созданная человеком или системой.  
Record входит в историю сопровождения и может иметь review-статус, но не подменяет snapshot-модель текущего состояния.

### Data Source

Происхождение состояния или записи: ручной ввод, внешний monitoring feed, импорт или расчёт backend-а.

---

## Logical Model

### Domain Entities

#### 1. System Actor

Единый actor-layer для `админ`, `engineer`, `operator`, `user`.

- Назначение: общий справочник участников системы для owner, author и reviewer.
- Ключевые поля:
  - `actor_id`
  - `external_id`
  - `display_name`
  - `role`
  - `activity_scope`
  - `is_active`

#### 2. Location

Иерархия размещения оборудования.

- Назначение: навигация по площадке, цеху, участку и другим зонам.
- Ключевые поля:
  - `location_id`
  - `name`
  - `location_type`
  - `parent_location_id`
  - `display_order`
  - `is_active`

#### 3. Equipment

Центральная единица мониторинга.

- Назначение: объект, у которого есть владелец, локация, текущее состояние, snapshots и history records.
- Ключевые поля:
  - `equipment_id`
  - `name`
  - `equipment_code`
  - `location_id`
  - `owner_actor_id`
  - `current_status`
  - `is_active`

#### 4. Sensor

Отдельная точка наблюдения по оборудованию.

- Назначение: базовый источник контекста для оценки состояния.
- Ключевые поля:
  - `sensor_id`
  - `equipment_id`
  - `name`
  - `sensor_type`
  - `data_source_id`
  - `is_primary_for_state`
  - `last_observed_at`
  - `is_active`

#### 5. Sensor Group

Логическое объединение датчиков.

- Назначение: группировка нескольких точек мониторинга в один аналитический контекст.
- Ключевые поля:
  - `sensor_group_id`
  - `equipment_id`
  - `name`
  - `group_type`
  - `data_source_id`
  - `is_used_for_state_assessment`
  - `is_active`

#### 6. Data Source

Справочник происхождения данных.

- Назначение: фиксирует, откуда пришло состояние, snapshot, sensor context или historical record.
- Ключевые поля:
  - `source_id`
  - `source_type`
  - `name`
  - `origin_semantics`
  - `trust_semantics`
  - `is_active`

#### 7. Equipment State Snapshot

Срез текущего или исторического состояния оборудования.

- Назначение: хранит агрегированный status и контекст sensor/group, из которого он получен.
- Ключевые поля:
  - `snapshot_id`
  - `equipment_id`
  - `status`
  - `severity`
  - `summary`
  - `observed_at`
  - `effective_at`
  - `data_source_id`
  - `created_at`

#### 8. Equipment State Record

Историческая запись наблюдения и сопровождения.

- Назначение: хранит manual/system record, автора, review-поля и idempotency-данные.
- Ключевые поля:
  - `record_id`
  - `equipment_id`
  - `author_actor_id`
  - `channel`
  - `status`
  - `comment`
  - `observed_at`
  - `created_at`
  - `source_type`
  - `review_status`
  - `reviewed_by_actor_id`
  - `reviewed_at`
  - `review_comment`
  - `idempotency_key`
  - `payload_hash`

#### 9. Knowledge Item

Справочный слой интерпретации.

- Назначение: хранит типовые объяснения и рекомендации по equipment/sensor/group типам.
- Ключевые поля:
  - `knowledge_item_id`
  - `title`
  - `body`
  - `is_active`

### Logical Relationships

- один `location` может содержать много дочерних `locations`;
- один `location` содержит много `equipment`;
- один `system_actor` может быть owner многих `equipment`;
- один `equipment` имеет много `sensors` и `sensor_groups`;
- одна `sensor_group` включает много `sensors` через membership;
- один `data_source` может поставлять данные для `sensors`, `sensor_groups` и `equipment_state_snapshots`;
- один `equipment` имеет историю `equipment_state_snapshots`;
- один `equipment` имеет историю `equipment_state_records`;
- один `system_actor` может быть author или reviewer многих `equipment_state_records`;
- snapshots и records могут ссылаться на sensor context через join tables;
- один `knowledge_item` может относиться к нескольким equipment/sensor/group типам через binding tables.

---

## Physical Schema (PostgreSQL)

### Naming Conventions

- таблицы: множественное число, `snake_case`;
- первичные ключи: `<entity>_id`;
- внешние ключи: `<referenced_entity>_id`;
- timestamps: `created_at` всегда обязательный, `updated_at` для mutable reference entities;
- join tables: `<left>_<right>` в порядке от более агрегированной сущности к более детальной.

### Project Enums / Lookups

#### `equipment_status`

- `normal`
- `warning`
- `critical`
- `unknown`

#### `actor_role`

- `admin`
- `engineer`
- `operator`
- `user`

#### `channel`

- `telegram`
- `web`

#### `data_source_type`

- `manual`
- `external_monitoring`
- `import`
- `backend_derived`

#### `review_status`

- `pending`
- `reviewed`
- `resolved`

### Tables

#### `system_actors`

Назначение: единый справочник участников системы.

- Primary key:
  - `actor_id`
- Columns:
  - `actor_id` `TEXT NOT NULL`
  - `external_id` `TEXT NOT NULL`
  - `display_name` `TEXT NULL`
  - `role` `actor_role NOT NULL`
  - `activity_scope` `TEXT NULL`
  - `is_active` `BOOLEAN NOT NULL DEFAULT TRUE`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - нет
- Unique constraints:
  - `external_id` unique
- Indexes:
  - unique index on `external_id`
  - index on `(role, is_active)`
- MVP/API mapping:
  - `author.external_id`, `author.display_name`, `author.role` из текущего API должны маппиться на эту таблицу в будущей реализации.

#### `locations`

Назначение: adjacency-list иерархия площадок и зон.

- Primary key:
  - `location_id`
- Columns:
  - `location_id` `TEXT NOT NULL`
  - `name` `TEXT NOT NULL`
  - `location_type` `TEXT NOT NULL`
  - `parent_location_id` `TEXT NULL`
  - `display_order` `INTEGER NOT NULL DEFAULT 0`
  - `is_active` `BOOLEAN NOT NULL DEFAULT TRUE`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `parent_location_id -> locations.location_id`
- Unique constraints:
  - нет обязательных глобальных unique кроме PK
- Indexes:
  - index on `parent_location_id`
  - index on `(location_type, is_active)`

#### `equipment`

Назначение: центральная reference-таблица оборудования.

- Primary key:
  - `equipment_id`
- Columns:
  - `equipment_id` `TEXT NOT NULL`
  - `name` `TEXT NOT NULL`
  - `equipment_code` `TEXT NULL`
  - `location_id` `TEXT NOT NULL`
  - `owner_actor_id` `TEXT NULL`
  - `current_status` `equipment_status NOT NULL DEFAULT 'unknown'`
  - `is_active` `BOOLEAN NOT NULL DEFAULT TRUE`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `location_id -> locations.location_id`
  - `owner_actor_id -> system_actors.actor_id`
- Unique constraints:
  - unique on `equipment_code` where not null
- Indexes:
  - index on `location_id`
  - index on `owner_actor_id`
  - index on `(current_status, is_active)`
- MVP/API mapping:
  - `equipment_id` из текущего API напрямую маппится в `equipment.equipment_id`.

#### `data_sources`

Назначение: справочник происхождения данных.

- Primary key:
  - `source_id`
- Columns:
  - `source_id` `TEXT NOT NULL`
  - `source_type` `data_source_type NOT NULL`
  - `name` `TEXT NOT NULL`
  - `origin_semantics` `TEXT NULL`
  - `trust_semantics` `TEXT NULL`
  - `is_active` `BOOLEAN NOT NULL DEFAULT TRUE`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - нет
- Unique constraints:
  - unique on `(source_type, name)`
- Indexes:
  - index on `source_type`

#### `sensors`

Назначение: отдельные точки мониторинга.

- Primary key:
  - `sensor_id`
- Columns:
  - `sensor_id` `TEXT NOT NULL`
  - `equipment_id` `TEXT NOT NULL`
  - `name` `TEXT NOT NULL`
  - `sensor_type` `TEXT NOT NULL`
  - `data_source_id` `TEXT NULL`
  - `is_primary_for_state` `BOOLEAN NOT NULL DEFAULT FALSE`
  - `last_observed_at` `TIMESTAMPTZ NULL`
  - `is_active` `BOOLEAN NOT NULL DEFAULT TRUE`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `equipment_id -> equipment.equipment_id`
  - `data_source_id -> data_sources.source_id`
- Unique constraints:
  - unique on `(equipment_id, name)`
- Indexes:
  - index on `equipment_id`
  - index on `data_source_id`
  - index on `(sensor_type, is_active)`

#### `sensor_groups`

Назначение: логические группы датчиков.

- Primary key:
  - `sensor_group_id`
- Columns:
  - `sensor_group_id` `TEXT NOT NULL`
  - `equipment_id` `TEXT NOT NULL`
  - `name` `TEXT NOT NULL`
  - `group_type` `TEXT NOT NULL`
  - `data_source_id` `TEXT NULL`
  - `is_used_for_state_assessment` `BOOLEAN NOT NULL DEFAULT FALSE`
  - `is_active` `BOOLEAN NOT NULL DEFAULT TRUE`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `equipment_id -> equipment.equipment_id`
  - `data_source_id -> data_sources.source_id`
- Unique constraints:
  - unique on `(equipment_id, name)`
- Indexes:
  - index on `equipment_id`
  - index on `data_source_id`
  - index on `(group_type, is_active)`

#### `sensor_group_members`

Назначение: many-to-many связь между группами и датчиками.

- Primary key:
  - composite primary key `(sensor_group_id, sensor_id)`
- Columns:
  - `sensor_group_id` `TEXT NOT NULL`
  - `sensor_id` `TEXT NOT NULL`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `sensor_group_id -> sensor_groups.sensor_group_id`
  - `sensor_id -> sensors.sensor_id`
- Unique constraints:
  - PK покрывает уникальность
- Indexes:
  - index on `sensor_id`

#### `equipment_state_snapshots`

Назначение: aggregated state snapshots для текущего состояния и истории.

- Primary key:
  - `snapshot_id`
- Columns:
  - `snapshot_id` `TEXT NOT NULL`
  - `equipment_id` `TEXT NOT NULL`
  - `status` `equipment_status NOT NULL`
  - `severity` `TEXT NULL`
  - `summary` `TEXT NULL`
  - `observed_at` `TIMESTAMPTZ NOT NULL`
  - `effective_at` `TIMESTAMPTZ NOT NULL`
  - `data_source_id` `TEXT NOT NULL`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `equipment_id -> equipment.equipment_id`
  - `data_source_id -> data_sources.source_id`
- Unique constraints:
  - нет обязательной уникальности кроме PK
- Indexes:
  - index on `equipment_id`
  - index on `data_source_id`
  - index on `(equipment_id, effective_at DESC)`
  - index on `(status, effective_at DESC)`

#### `equipment_state_snapshot_sensors`

Назначение: normalized sensor context для snapshots.

- Primary key:
  - composite primary key `(snapshot_id, sensor_id)`
- Columns:
  - `snapshot_id` `TEXT NOT NULL`
  - `sensor_id` `TEXT NOT NULL`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `snapshot_id -> equipment_state_snapshots.snapshot_id`
  - `sensor_id -> sensors.sensor_id`
- Indexes:
  - index on `sensor_id`

#### `equipment_state_snapshot_sensor_groups`

Назначение: normalized sensor-group context для snapshots.

- Primary key:
  - composite primary key `(snapshot_id, sensor_group_id)`
- Columns:
  - `snapshot_id` `TEXT NOT NULL`
  - `sensor_group_id` `TEXT NOT NULL`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `snapshot_id -> equipment_state_snapshots.snapshot_id`
  - `sensor_group_id -> sensor_groups.sensor_group_id`
- Indexes:
  - index on `sensor_group_id`

#### `equipment_state_records`

Назначение: historical records, включая manual фиксации и review.

- Primary key:
  - `record_id`
- Columns:
  - `record_id` `TEXT NOT NULL`
  - `equipment_id` `TEXT NOT NULL`
  - `author_actor_id` `TEXT NOT NULL`
  - `channel` `channel NOT NULL`
  - `status` `equipment_status NOT NULL`
  - `comment` `TEXT NULL`
  - `observed_at` `TIMESTAMPTZ NOT NULL`
  - `created_at` `TIMESTAMPTZ NOT NULL`
  - `source_type` `data_source_type NOT NULL`
  - `review_status` `review_status NOT NULL DEFAULT 'pending'`
  - `reviewed_by_actor_id` `TEXT NULL`
  - `reviewed_at` `TIMESTAMPTZ NULL`
  - `review_comment` `TEXT NULL`
  - `idempotency_key` `TEXT NULL`
  - `payload_hash` `TEXT NULL`
- Foreign keys:
  - `equipment_id -> equipment.equipment_id`
  - `author_actor_id -> system_actors.actor_id`
  - `reviewed_by_actor_id -> system_actors.actor_id`
- Unique constraints:
  - unique on `idempotency_key` where not null
- Indexes:
  - index on `equipment_id`
  - index on `author_actor_id`
  - index on `reviewed_by_actor_id`
  - index on `(equipment_id, observed_at DESC)`
  - index on `(review_status, created_at DESC)`
- MVP/API mapping:
  - `status`, `comment`, `observed_at`, `channel`, `idempotency_key` и `author.*` из текущего API маппятся сюда;
  - `payload_hash` сохраняется как обязательный idempotency-support field;
  - `review_*` поля не входят в текущий MVP contract, но включены в целевую physical schema.

#### `equipment_state_record_sensors`

Назначение: normalized sensor context для state records.

- Primary key:
  - composite primary key `(record_id, sensor_id)`
- Columns:
  - `record_id` `TEXT NOT NULL`
  - `sensor_id` `TEXT NOT NULL`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `record_id -> equipment_state_records.record_id`
  - `sensor_id -> sensors.sensor_id`
- Indexes:
  - index on `sensor_id`

#### `equipment_state_record_sensor_groups`

Назначение: normalized sensor-group context для state records.

- Primary key:
  - composite primary key `(record_id, sensor_group_id)`
- Columns:
  - `record_id` `TEXT NOT NULL`
  - `sensor_group_id` `TEXT NOT NULL`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - `record_id -> equipment_state_records.record_id`
  - `sensor_group_id -> sensor_groups.sensor_group_id`
- Indexes:
  - index on `sensor_group_id`

#### `knowledge_items`

Назначение: справочные материалы и интерпретации.

- Primary key:
  - `knowledge_item_id`
- Columns:
  - `knowledge_item_id` `TEXT NOT NULL`
  - `title` `TEXT NOT NULL`
  - `body` `TEXT NOT NULL`
  - `is_active` `BOOLEAN NOT NULL DEFAULT TRUE`
  - `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Foreign keys:
  - нет
- Indexes:
  - index on `is_active`

#### `knowledge_item_equipment_types`

Назначение: привязка knowledge item к equipment type.

- Primary key:
  - composite primary key `(knowledge_item_id, equipment_type)`
- Columns:
  - `knowledge_item_id` `TEXT NOT NULL`
  - `equipment_type` `TEXT NOT NULL`
- Foreign keys:
  - `knowledge_item_id -> knowledge_items.knowledge_item_id`

#### `knowledge_item_sensor_types`

Назначение: привязка knowledge item к sensor type.

- Primary key:
  - composite primary key `(knowledge_item_id, sensor_type)`
- Columns:
  - `knowledge_item_id` `TEXT NOT NULL`
  - `sensor_type` `TEXT NOT NULL`
- Foreign keys:
  - `knowledge_item_id -> knowledge_items.knowledge_item_id`

#### `knowledge_item_sensor_group_types`

Назначение: привязка knowledge item к sensor-group type.

- Primary key:
  - composite primary key `(knowledge_item_id, sensor_group_type)`
- Columns:
  - `knowledge_item_id` `TEXT NOT NULL`
  - `sensor_group_type` `TEXT NOT NULL`
- Foreign keys:
  - `knowledge_item_id -> knowledge_items.knowledge_item_id`

---

## Mapping To Current MVP API

### `POST /api/v1/equipment-state-records`

Текущие поля API должны маппиться так:
- `equipment_id` -> `equipment.equipment_id`
- `status` -> `equipment_state_records.status`
- `comment` -> `equipment_state_records.comment`
- `observed_at` -> `equipment_state_records.observed_at`
- `channel` -> `equipment_state_records.channel`
- `idempotency_key` -> `equipment_state_records.idempotency_key`
- payload canonical hash -> `equipment_state_records.payload_hash`
- `author.external_id`, `author.display_name`, `author.role` -> `system_actors`

### `POST /api/v1/assistant/messages`

`equipment_context.sensor_ids` и `equipment_context.sensor_group_ids` не должны трактоваться как сигнал к JSON-first persistence.  
В целевой физической модели эти идентификаторы опираются на normal form через `sensors`, `sensor_groups` и join tables snapshot/record context.

---

## Legacy Runtime Schema And Transition

Сейчас в backend-коде существуют только две runtime-created таблицы:
- `equipment`
- `equipment_state_records`

Также текущая реализация уже использует:
- `idempotency_key`
- `payload_hash`

Переход к целевой модели трактуется так:
- текущая схема является минимальной legacy-основой для MVP;
- она не покрывает actor layer, location hierarchy, data sources, snapshots, sensor groups и review-поля;
- `equipment` и `equipment_state_records` должны сохраниться как часть целевой модели, а не быть отброшены;
- целевая схема задачи 02 служит входом для следующих задач по миграциям и ORM.

---

## Follow-Up After Task 02

После внедрения web и внешних источников могут быть добавлены:
- отдельное persistence для assistant conversations;
- incident/case lifecycle;
- audit log;
- richer approval workflow;
- специализированное time-series storage для raw telemetry;
- поисковые и аналитические хранилища рядом с PostgreSQL.

Эти расширения не должны ломать текущую relational model core domain.

---

## Schema Review Gate

Перед началом миграций схема должна пройти внутреннюю проектную проверку на согласованность с `user-scenarios`, `api-contracts`, ER-артефактом и фактическим migration/data-access workflow.  
Внешний review является обязательным gate и не заменяется только внутренней проверкой.

### Internal Self-Checklist

- current state snapshots и historical state records разведены как разные таблицы;
- все many-to-many связи вынесены в join tables;
- обязательные FK не заменены текстовыми ссылками;
- `idempotency_key` и `payload_hash` сохранены в physical schema;
- owner/author/reviewer опираются на единый actor layer;
- `locations` использует adjacency-list модель с self-FK;
- naming везде остаётся в `snake_case`;
- для mutable reference entities предусмотрены `created_at` и `updated_at`;
- для history tables предусмотрены индексы по времени и equipment;
- `review_status`, `reviewed_by_actor_id`, `reviewed_at` не ломают текущий MVP flow благодаря nullable/non-nullable границам;
- текущий API-контракт фиксации состояния можно реализовать поверх `equipment_state_records` без изменения wire shape.

---

## Связанные артефакты

- `docs/spec/user-scenarios.md` — сценарии, из которых выведены требования.
- `backend/docs/api-contracts.md` — текущие MVP DTO и терминология.
- `docs/diagrams/database-er.md` — отдельная physical ER-диаграмма по этой схеме.
- `docs/adr/adr-001-database.md` — архитектурное решение о PostgreSQL и стратегии эволюции схемы.
