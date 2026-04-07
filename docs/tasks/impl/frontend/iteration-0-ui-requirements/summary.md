# Итерация 0: Требования к UI и API-контракты — Summary

## Статус: ✅ Done

## Что сделано

- Зафиксированы функциональные требования к трём основным экранам web-клиента:
  - Экран 1 — Панель обзора площадки (`/dashboard`): индекс состояния, сводка по статусам, график за 14 дней, топ проблемного оборудования, ленты изменений и действий
  - Экран 2 — Панель обзора оборудования (`/dashboard/equipment/{id}`): статус, переключатель данных, прогресс ТО, топ-3 узлов, история
  - Экран 3 — Панель обзора узла (`/dashboard/equipment/{id}/nodes/{sensor_group_id}`): статус, фото, характеристики, AI-диагностика
- Зафиксированы требования к глобальному floating AI-чату на всех экранах
- Описано правило агрегации статусов: worst-status-wins снизу вверх (узел → оборудование → площадка)
- Зафиксирован стиль UI: светлая/тёмная тема, dev-стиль (референс tbench.ai), тёмная по умолчанию
- Зафиксирована временная схема входа через Telegram username
- Спроектированы и задокументированы 13 новых API endpoint'ов для всех экранов
- Определены требования к расширению схемы данных (3 новых поля: `image_url`, `maintenance_due_at`, `maintenance_completed_at`)

## Артефакты

- `docs/tasks/impl/frontend/iteration-0-ui-requirements/plan.md` — план и требования итерации
- `backend/docs/api-contracts.md` — обновлён: добавлены сценарии 3–8 (auth, dashboard, equipment, sensor-groups, locations, admin)
- `backend/docs/openapi.yaml` — обновлён: 13 новых endpoint'ов, 30+ новых схем, securitySchemes

## Новые API endpoint'ы

| Группа | Method | Path |
|--------|--------|------|
| Auth | POST | /api/v1/auth/login |
| Auth | GET | /api/v1/auth/me |
| Dashboard | GET | /api/v1/dashboard/plant |
| Dashboard | GET | /api/v1/dashboard/state-feed |
| Dashboard | GET | /api/v1/dashboard/action-feed |
| Equipment | GET | /api/v1/equipment |
| Equipment | GET | /api/v1/equipment/{id} |
| Equipment | GET | /api/v1/equipment/{id}/history |
| Nodes | GET | /api/v1/sensor-groups/{id} |
| Locations | GET | /api/v1/locations/tree |
| Admin | GET | /api/v1/admin/dashboard |
| Admin | GET | /api/v1/admin/clients |
| Admin | GET | /api/v1/admin/events |

## Что не входило в скоуп

- Реализация endpoint'ов (итерация 1)
- Миграции и mock-данные (итерация 1)
- Инициализация frontend-проекта (итерация 2)

## Следующий шаг

Итерация 1: Реализация API для frontend — реализовать все спроектированные endpoint'ы в backend, добавить миграции с mock-данными.
