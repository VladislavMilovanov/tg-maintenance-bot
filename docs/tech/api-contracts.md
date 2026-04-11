# API Contracts

Единая точка входа в документацию по API-контрактам проекта.

## Source of truth

- hand-written OpenAPI: `backend/docs/openapi.yaml`
- runtime OpenAPI: `GET /docs`, `GET /openapi.json`

## Поясняющий документ

Подробное описание текущих MVP-сценариев находится в:

- `backend/docs/api-contracts.md`

На текущем этапе там же зафиксированы:

- временная frontend auth-схема через `POST /api/v1/auth/login` и `GET /api/v1/auth/me`
- protected endpoint `POST /api/v1/query/text-to-sql` с `Authorization: Bearer {access_token}`
- различие между frontend auth flow и Telegram-ботом как service client поверх `BACKEND_URL`

Этот файл существует для выравнивания структуры `docs/` и onboarding-навигации. Детали DTO, обязательных полей и кодов ошибок по-прежнему определяются в OpenAPI-спеке backend.
