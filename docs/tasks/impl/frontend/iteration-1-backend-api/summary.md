# Iteration 01: Backend API for Frontend — Summary

## Что было сделано

### Расширение схемы БД
- Добавлены 3 новых колонки в таблицу `equipment`:
  - `image_url` — URL фотографии оборудования/узла
  - `maintenance_due_at` — плановая дата технического обслуживания
  - `maintenance_completed_at` — фактическая дата выполнения ТО
- Миграция `20260405_0002_frontend_schema_extensions.py` применена успешно

### Аутентификация
- `POST /api/v1/auth/login` — принимает Telegram username, возвращает Bearer-токен
- `GET /api/v1/auth/me` — возвращает данные текущего пользователя по токену
- In-memory хранилище токенов (`AuthService`) с поддержкой TTL

### 13 новых GET endpoint'ов

| Группа | Endpoint | Описание |
|--------|----------|----------|
| Dashboard | `GET /api/v1/dashboard/plant` | Агрегированный статус площадки + KPI |
| Dashboard | `GET /api/v1/dashboard/state-feed` | Лента изменений состояния оборудования |
| Dashboard | `GET /api/v1/dashboard/action-feed` | Лента действий с оборудованием |
| Equipment | `GET /api/v1/equipment` | Список всего оборудования |
| Equipment | `GET /api/v1/equipment/{id}` | Детали единицы оборудования |
| Equipment | `GET /api/v1/equipment/{id}/history` | История состояний и действий |
| Sensor Groups | `GET /api/v1/sensor-groups/{id}` | Детали узла (с AI-диагностикой) |
| Locations | `GET /api/v1/locations/tree` | Дерево локаций |
| Admin | `GET /api/v1/admin/dashboard` | KPI-дашборд для администратора |
| Admin | `GET /api/v1/admin/clients` | Список клиентов |
| Admin | `GET /api/v1/admin/events` | Лента последних событий |

### Mock-данные
Миграция `20260405_0003_mock_data.py` засеяла БД реалистичными данными:
- 8 единиц оборудования с разными статусами (normal/warning/critical)
- 14 групп датчиков с параметрами и фотографиями
- 22 снимка состояния за последние 14 дней
- 10 записей журнала действий
- 1 пользователь-администратор

### Тесты
- 40 новых unit-тестов добавлено к существующим 18
- **58 тестов — все проходят**
- 0 lint-ошибок (`ruff check` чист)

## Артефакты

### Новые файлы
| Файл | Описание |
|------|----------|
| `backend/src/maintenance_backend/api/dashboard.py` | Route-handlers для дашборда |
| `backend/src/maintenance_backend/api/equipment.py` | Route-handlers для оборудования |
| `backend/src/maintenance_backend/api/sensor_groups.py` | Route-handlers для узлов |
| `backend/src/maintenance_backend/api/locations.py` | Route-handlers для локаций |
| `backend/src/maintenance_backend/api/admin.py` | Route-handlers для панели админа |
| `backend/src/maintenance_backend/schemas/dashboard.py` | Response-схемы дашборда |
| `backend/src/maintenance_backend/schemas/equipment_read.py` | Response-схемы оборудования |
| `backend/src/maintenance_backend/schemas/sensor_groups.py` | Response-схемы узлов |
| `backend/src/maintenance_backend/schemas/locations.py` | Response-схемы локаций |
| `backend/src/maintenance_backend/schemas/admin.py` | Response-схемы панели админа |
| `backend/src/maintenance_backend/schemas/auth.py` | Схемы аутентификации |
| `backend/src/maintenance_backend/repositories_read.py` | PostgresReadRepository (11 методов) |
| `backend/src/maintenance_backend/services/auth.py` | AuthService (in-memory token store) |
| `alembic/versions/20260405_0002_frontend_schema_extensions.py` | Миграция расширения схемы |
| `alembic/versions/20260405_0003_mock_data.py` | Миграция mock-данных |
| `backend/tests/test_dashboard_api.py` | Тесты дашборда |
| `backend/tests/test_equipment_api.py` | Тесты оборудования |
| `backend/tests/test_sensor_groups_api.py` | Тесты узлов |
| `backend/tests/test_locations_api.py` | Тесты локаций |
| `backend/tests/test_admin_api.py` | Тесты панели админа |
| `backend/tests/test_auth_api.py` | Тесты аутентификации |

### Изменённые файлы
- `backend/src/maintenance_backend/app.py` — регистрация новых router'ов
- `backend/src/maintenance_backend/dependencies.py` — зависимости для read repository и auth
- `backend/src/maintenance_backend/api/router.py` — подключение новых маршрутов
- `backend/src/maintenance_backend/db_schema.py` — новые таблицы и колонки
- `backend/src/maintenance_backend/models.py` — 5 новых ORM-моделей
- `backend/tests/conftest.py` — фикстуры для новых endpoint'ов
- `backend/docs/api-contracts.md` — обновление с новыми контрактами
- `backend/docs/openapi.yaml` — обновление OpenAPI-спецификации

## Результаты верификации

| Проверка | Результат |
|----------|-----------|
| Unit-тесты | ✅ 58/58 проходят |
| Lint (ruff check) | ✅ 0 ошибок |
| Imports (ruff check --select I) | ✅ чисто |
| Соответствие OpenAPI-спецификации | ✅ все схемы соответствуют |

## Следующие шаги

**Итерация 02 — Каркас frontend-проекта (Next.js App Router):**
- Инициализация проекта: Next.js + TypeScript + shadcn/ui + Tailwind CSS + pnpm
- Настройка темы (dev-стиль по референсу tbench.ai)
- Реализация входа по Telegram username
- Базовый layout с навигацией и заглушкой чат-виджета
