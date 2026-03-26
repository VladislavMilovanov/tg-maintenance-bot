# Backend Tasklist

## Обзор

Backend — единое ядро системы мониторинга, через которое проходят все клиентские каналы (Telegram и Web) и внешние интеграции. В рамках этого tasklist фиксируется последовательная подготовка backend-основы: от архитектурных решений и контрактов до запуска и актуализации правил взаимодействия.

## Связь с plan.md

- **Итерация 1: Backend foundation** — покрывается напрямую (архитектура, контракты, API-основа, единая точка входа).
- **Итерация 2: Telegram MVP client** — покрывается через задачу рефакторинга бота на работу через backend API.
- **Итерация 3: Web unified client** — покрывается через подготовку стабильных backend-контрактов для web-клиента.
- **Итерация 4: Monitoring and LLM integrations** — покрывается через подключение хранения и внешних интеграций в backend-поток.
- **Итерация 5: Platform readiness** — покрывается через соглашения API, обновление документации и сценарии локального запуска.

## Легенда статусов

- 📋 Planned - Запланирован
- 🚧 In Progress - В работе
- ✅ Done - Завершен

## Список задач

| Задача | Описание | Статус | Документы |
|--------|----------|--------|-----------|
| 01 | Выбор backend-стека и фиксация ключевого архитектурного решения (ADR). | 📋 Planned | [plan](tasks/task-01-backend-stack-adr/plan.md) \| [summary](tasks/task-01-backend-stack-adr/summary.md) |
| 02 | Генерация каркаса backend-проекта и базовой структуры модулей. | 📋 Planned | [plan](tasks/task-02-backend-bootstrap/plan.md) \| [summary](tasks/task-02-backend-bootstrap/summary.md) |
| 03 | Проектирование и базовое документирование API-контрактов для клиентов и интеграций. | 📋 Planned | [plan](tasks/task-03-api-contracts/plan.md) \| [summary](tasks/task-03-api-contracts/summary.md) |
| 04 | Реализация API по контрактам с базовыми валидациями и обработкой ошибок. | 📋 Planned | [plan](tasks/task-04-api-implementation/plan.md) \| [summary](tasks/task-04-api-implementation/summary.md) |
| 05 | Подключение хранения и интеграций (источники мониторинга, LLM, PostgreSQL) по логике плана. | 📋 Planned | [plan](tasks/task-05-storage-integrations/plan.md) \| [summary](tasks/task-05-storage-integrations/summary.md) |
| 06 | Подготовка backend как единой точки входа для bot/web и внешних источников данных. | 📋 Planned | [plan](tasks/task-06-unified-entrypoint/plan.md) \| [summary](tasks/task-06-unified-entrypoint/summary.md) |
| 07 | Рефакторинг бота: перенос прямой бизнес-логики на взаимодействие через backend API. | 📋 Planned | [plan](tasks/task-07-bot-refactor-api/plan.md) \| [summary](tasks/task-07-bot-refactor-api/summary.md) |
| 08 | Актуализация соглашений API: форматы запросов, коды ошибок, версионирование. | 📋 Planned | [plan](tasks/task-08-api-governance/plan.md) \| [summary](tasks/task-08-api-governance/summary.md) |
| 09 | Актуализация `vision.md`, `data-model.md`, `integrations.md` по фактической backend-реализации. | 📋 Planned | [plan](tasks/task-09-docs-alignment/plan.md) \| [summary](tasks/task-09-docs-alignment/summary.md) |
| 10 | Описание команд и сценариев локального запуска всей системы через backend-first поток. | 📋 Planned | [plan](tasks/task-10-local-run-scenarios/plan.md) \| [summary](tasks/task-10-local-run-scenarios/summary.md) |

---

## Задача 01: Backend stack и ADR 📋

### Цель

Зафиксировать backend-стек MVP и ключевое архитектурное решение, определяющее базовую траекторию реализации.

### Состав работ

- [ ] Согласовать runtime, фреймворк API и базовый набор backend-зависимостей.
- [ ] Зафиксировать архитектурное решение в ADR с аргументацией и ограничениями.
- [ ] Сверить выбор с принципом backend-first из `vision.md`.

### Артефакты

- `docs/adr/adr-00x-backend-stack.md` - решение по backend-стеку и границам ответственности.
- `docs/tasks/task-01-backend-stack-adr/plan.md` - план реализации задачи.
- `docs/tasks/task-01-backend-stack-adr/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-01-backend-stack-adr/plan.md)
- 📝 [Summary](tasks/task-01-backend-stack-adr/summary.md)

---

## Задача 02: Каркас backend-проекта 📋

### Цель

Подготовить стартовый шаблон backend-проекта для быстрой итеративной разработки API и интеграций.

### Состав работ

- [ ] Сгенерировать структуру backend-пакета и модулей.
- [ ] Подключить конфигурацию окружений и базовый lifecycle приложения.
- [ ] Подготовить минимальные make/uv-команды для разработки backend.

### Артефакты

- `backend/` - каркас backend-проекта.
- `docs/tasks/task-02-backend-bootstrap/plan.md` - план реализации задачи.
- `docs/tasks/task-02-backend-bootstrap/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-02-backend-bootstrap/plan.md)
- 📝 [Summary](tasks/task-02-backend-bootstrap/summary.md)

---

## Задача 03: API-контракты 📋

### Цель

Определить и задокументировать базовые API-контракты backend для сценариев из `vision.md`.

### Состав работ

- [ ] Описать ключевые endpoint-группы для bot/web и интеграций.
- [ ] Зафиксировать входные/выходные форматы и обязательные поля.
- [ ] Согласовать базовую модель ошибок на уровне контрактов.

### Артефакты

- `backend/docs/api-contracts.md` - базовое описание API-контрактов.
- `docs/tasks/task-03-api-contracts/plan.md` - план реализации задачи.
- `docs/tasks/task-03-api-contracts/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-03-api-contracts/plan.md)
- 📝 [Summary](tasks/task-03-api-contracts/summary.md)

---

## Задача 04: Реализация API 📋

### Цель

Реализовать API-слой backend по согласованным контрактам с базовыми проверками корректности запросов.

### Состав работ

- [ ] Реализовать основные endpoint для пользовательских сценариев MVP.
- [ ] Добавить базовые валидации входных данных и обработку типовых ошибок.
- [ ] Проверить соответствие фактического API зафиксированным контрактам.

### Артефакты

- `backend/` - реализованные API-обработчики и схемы.
- `docs/tasks/task-04-api-implementation/plan.md` - план реализации задачи.
- `docs/tasks/task-04-api-implementation/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-04-api-implementation/plan.md)
- 📝 [Summary](tasks/task-04-api-implementation/summary.md)

---

## Задача 05: Хранение и интеграции 📋

### Цель

Подключить слой хранения и внешние интеграции в единый backend-поток обработки состояния оборудования.

### Состав работ

- [ ] Настроить подключение к PostgreSQL и базовую схему хранения MVP.
- [ ] Подключить интеграцию с источниками мониторинга и LLM-сервисом.
- [ ] Определить fallback-поведение при недоступности внешних зависимостей.

### Артефакты

- `backend/` - конфигурация хранения и интеграционных модулей.
- `docs/tasks/task-05-storage-integrations/plan.md` - план реализации задачи.
- `docs/tasks/task-05-storage-integrations/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-05-storage-integrations/plan.md)
- 📝 [Summary](tasks/task-05-storage-integrations/summary.md)

---

## Задача 06: Единая точка входа backend 📋

### Цель

Сделать backend единой входной точкой для всех клиентских запросов и внешних интеграционных потоков.

### Состав работ

- [ ] Уточнить границы ответственности backend и клиентов.
- [ ] Исключить обходные пути прямой бизнес-логики вне backend.
- [ ] Подготовить унифицированный маршрут взаимодействия для bot/web и внешних систем.

### Артефакты

- `backend/` - единый слой входа и маршрутизации запросов.
- `docs/tasks/task-06-unified-entrypoint/plan.md` - план реализации задачи.
- `docs/tasks/task-06-unified-entrypoint/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-06-unified-entrypoint/plan.md)
- 📝 [Summary](tasks/task-06-unified-entrypoint/summary.md)

---

## Задача 07: Рефакторинг бота на backend API 📋

### Цель

Перенести прямую бизнес-логику из Telegram-бота в backend и оставить в боте клиентский слой взаимодействия.

### Состав работ

- [ ] Выявить участки прямой логики в боте и определить точки миграции.
- [ ] Перевести bot-flow на backend API-вызовы по контрактам.
- [ ] Проверить сохранение пользовательских сценариев после переноса.

### Артефакты

- `bot/` - обновленный клиентский слой Telegram-бота.
- `docs/tasks/task-07-bot-refactor-api/plan.md` - план реализации задачи.
- `docs/tasks/task-07-bot-refactor-api/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-07-bot-refactor-api/plan.md)
- 📝 [Summary](tasks/task-07-bot-refactor-api/summary.md)

---

## Задача 08: Соглашения API (форматы, ошибки, версия) 📋

### Цель

Зафиксировать единые правила изменения и использования API-контрактов для всех клиентов и интеграций.

### Состав работ

- [ ] Зафиксировать формат запросов/ответов и обязательные поля.
- [ ] Определить каталог кодов ошибок и правила их применения.
- [ ] Зафиксировать схему версионирования API и правила совместимости.

### Артефакты

- `backend/docs/api-governance.md` - соглашения по API-контрактам.
- `docs/tasks/task-08-api-governance/plan.md` - план реализации задачи.
- `docs/tasks/task-08-api-governance/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-08-api-governance/plan.md)
- 📝 [Summary](tasks/task-08-api-governance/summary.md)

---

## Задача 09: Актуализация проектной документации 📋

### Цель

Привести `vision.md`, `data-model.md` и `integrations.md` в соответствие с фактически реализованным backend.

### Состав работ

- [ ] Обновить архитектурные акценты и границы ответственности в `vision.md`.
- [ ] Обновить доменную модель и связи в `data-model.md`.
- [ ] Обновить интеграционные контракты и риски в `integrations.md`.

### Артефакты

- `docs/vision.md` - актуализированное видение системы.
- `docs/data-model.md` - актуализированная модель данных.
- `docs/integrations.md` - актуализированная карта интеграций.
- `docs/tasks/task-09-docs-alignment/plan.md` - план реализации задачи.
- `docs/tasks/task-09-docs-alignment/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-09-docs-alignment/plan.md)
- 📝 [Summary](tasks/task-09-docs-alignment/summary.md)

---

## Задача 10: Локальный запуск системы 📋

### Цель

Описать единые команды и сценарии локального запуска всей системы вокруг backend-first архитектуры.

### Состав работ

- [ ] Зафиксировать последовательность запуска backend, bot и web в dev-среде.
- [ ] Описать обязательные переменные окружения и минимальные проверки старта.
- [ ] Синхронизировать сценарии в README/технической документации.

### Артефакты

- `README.md` - обновленные команды и сценарии запуска.
- `docs/tasks/task-10-local-run-scenarios/plan.md` - план реализации задачи.
- `docs/tasks/task-10-local-run-scenarios/summary.md` - итог выполнения задачи.

### Документы

- 📋 [План](tasks/task-10-local-run-scenarios/plan.md)
- 📝 [Summary](tasks/task-10-local-run-scenarios/summary.md)

## Качество и инженерные практики

- Тесты: smoke для ключевых endpoint и базовые интеграционные проверки backend-потока.
- Линтеры: единые правила стиля/типизации и обязательный прогон перед merge.
- Наблюдаемость: базовые структурированные логи, health-check endpoint и журнал ошибок интеграций.
- Изменения контрактов: любые несовместимые изменения API только через версионирование и обновление документации.
