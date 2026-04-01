# Задача 02: API-контракты двух сценариев

## Цель

Зафиксировать контрактный слой MVP для двух backend-сценариев: вопрос ассистенту и ручная фиксация состояния оборудования. Контракты должны стать общей основой для Telegram-бота, будущего web-клиента и следующих backend-задач.

## Контекст

- В репозитории уже есть Telegram-бот, где `src/maintenance_bot/handlers/chat.py` обрабатывает пользовательское сообщение, собирает историю диалога и напрямую вызывает LLM.
- `vision.md` и `ADR-002` фиксируют backend-first модель и thin-clients подход.
- Backend-каркас ещё не создан, поэтому результат задачи должен быть документарным и пригодным для последующей реализации без повторного проектирования.
- Для MVP выбран `OpenAPI-first`: машиночитаемая спецификация является источником истины, а текстовые документы лишь поясняют принятые решения.

## Решения

- Зафиксировать основной артефакт контрактов в `backend/docs/openapi.yaml`.
- Добавить краткий companion-doc `backend/docs/api-contracts.md` с пояснением сценариев, ограничений MVP и связи с текущим bot-flow.
- Зафиксировать два endpoint'а версии `v1`:
  - `POST /api/v1/assistant/messages`
  - `POST /api/v1/equipment-state-records`
- Для assistant-сценария принять request shape с полями `channel`, `user`, `message`, `conversation_id?`, `equipment_context?`.
- Для assistant-сценария принять response shape с полями `answer`, `conversation_id`, `context_used?`, `meta`.
- Для state-record сценария принять MVP minimal request shape с полями `equipment_id`, `status`, `comment?`, `observed_at`, `channel`, `author`.
- Для state-record сценария принять response shape с `record_id`, нормализованными полями записи и `created_at`.
- Зафиксировать общий error-shape `code`, `message`, `details?`, `trace_id?` для обоих endpoint'ов.
- Не включать в scope задачи аутентификацию, авторизацию, вложенные датчики, файлы, review-lifecycle и persistence-стратегию истории диалога.

## Состав работ

- Подготовить OpenAPI-спеку с endpoint'ами, схемами DTO и типовыми кодами ошибок.
- Отразить в контракте assistant flow требования из текущего бота: пользовательское сообщение, conversation context, ответ ассистента и fallback при недоступности LLM.
- Зафиксировать MVP enum статусов оборудования: `normal`, `warning`, `critical`, `unknown`.
- Синхронизировать терминологию и поля в `docs/data-model.md` под контракт фиксации состояния.
- Синхронизировать `docs/integrations.md`, чтобы backend был единственной точкой вызова LLM и общим API для bot/web.
- Обновить `docs/tasks/tasklist-backend.md` ссылками на реальные артефакты задачи.

## Артефакты

- `backend/docs/openapi.yaml`
- `backend/docs/api-contracts.md`
- `docs/tasks/impl/backend/iteration-1-backend-foundation/tasks/task-02-api-contracts-two-scenarios/summary.md`

## Definition of Done

- OpenAPI-спека однозначно описывает оба endpoint'а, их request/response схемы и типовые ошибки.
- Assistant-контракт покрывает текущий bot-flow без прямого вызова LLM из клиента в целевой архитектуре.
- Контракт фиксации состояния не требует вложенных сенсорных структур и остаётся в рамках MVP minimal.
- `docs/data-model.md` и `docs/integrations.md` используют те же термины и не противоречат контрактам.
- `tasklist-backend.md` указывает на реальные артефакты задачи 02.
