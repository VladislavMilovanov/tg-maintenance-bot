# Iteration 01: Backend API for Frontend — Plan

## Цель

Реализовать все 13 read-only API endpoint'ов, спроектированных в Итерации 0, чтобы обеспечить полноценные данные для отрисовки всех трёх экранов frontend.

## Scope

### Расширение схемы БД
- 3 новых колонки: `image_url`, `maintenance_due_at`, `maintenance_completed_at`
- Alembic-миграция для расширения схемы (`20260405_0002_frontend_schema_extensions.py`)

### Аутентификация
- `POST /api/v1/auth/login` — вход по Telegram username, возвращает Bearer-токен
- `GET /api/v1/auth/me` — получение текущего пользователя по токену
- In-memory хранилище токенов (соответствует паттерну существующего conversation store)

### ORM-модели
5 новых моделей SQLAlchemy:
- `Location` — локация/площадка
- `Sensor` — датчик
- `SensorGroup` — группа датчиков (узел)
- `DataSource` — источник данных
- `EquipmentStateSnapshot` — снимок состояния оборудования

### Response Schemas
Response-схемы Pydantic, соответствующие OpenAPI-спецификации:
- Схемы дашборда (plant overview, state feed, action feed)
- Схемы оборудования (list, detail, history)
- Схемы узлов (sensor group detail)
- Схемы локаций (location tree)
- Схемы панели администратора (dashboard, clients, events)

### Read Repository
`PostgresReadRepository` в `repositories_read.py` — 11 query-методов:
- `get_plant_overview` — агрегированный статус площадки
- `get_state_feed` — лента изменений состояния
- `get_action_feed` — лента действий
- `get_equipment_list` — список оборудования
- `get_equipment_detail` — детали единицы оборудования
- `get_equipment_history` — история состояний и действий
- `get_sensor_group` — детали узла
- `get_location_tree` — дерево локаций
- `get_admin_dashboard` — KPI для панели администратора
- `get_admin_clients` — список клиентов
- `get_admin_events` — лента событий для администратора

### API Endpoints (13 новых)
Распределены по 5 route-файлам:
- **Dashboard** (`/api/v1/dashboard`): `/plant`, `/state-feed`, `/action-feed`
- **Equipment** (`/api/v1/equipment`): `/`, `/{id}`, `/{id}/history`
- **Sensor Groups** (`/api/v1/sensor-groups`): `/{id}`
- **Locations** (`/api/v1/locations`): `/tree`
- **Admin** (`/api/v1/admin`): `/dashboard`, `/clients`, `/events`

### Mock Data Migration
Миграция `20260405_0003_mock_data.py` с реалистичными фабричными данными:
- 8 единиц оборудования
- 14 групп датчиков
- 22 снимка состояния
- 10 записей журнала

### Admin User Migration
Миграция добавления пользователя-администратора в базу данных.

### Тесты
40 новых unit-тестов (58 всего, все проходят).

## Ключевые решения

| Решение | Обоснование |
|---------|-------------|
| In-memory token store | Соответствует паттерну существующего conversation store; для MVP не требуется персистентность токенов |
| SQLAlchemy Core для read-запросов | Отсутствие ORM overhead для операций чтения; прямой SQL с typesafe binding |
| Агрегация worst-status-wins на уровне БД | `CASE WHEN` в SQL-запросах — минимальная нагрузка на приложение |
| Отдельный `repositories_read.py` | Разделение ответственности read/write; упрощает тестирование и поддержку |

## Артефакты

- `backend/src/maintenance_backend/api/` — 5 новых route-файлов + обновления
- `backend/src/maintenance_backend/schemas/` — 5 новых schema-файлов
- `backend/src/maintenance_backend/repositories_read.py` — read repository
- `backend/src/maintenance_backend/services/auth.py` — auth service
- `alembic/versions/20260405_0002_frontend_schema_extensions.py` — миграция схемы
- `alembic/versions/20260405_0003_mock_data.py` — миграция mock-данных
- `backend/tests/` — 6 новых test-файлов
- `backend/docs/api-contracts.md` — обновление
- `backend/docs/openapi.yaml` — обновление
