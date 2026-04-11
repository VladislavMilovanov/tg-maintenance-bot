# Local Agents

Локальные subagent-определения хранятся в `.agents/skills/`.

## docs-updater

Назначение:
- проверить, создали ли изменения в коде documentation drift;
- при необходимости синхронизировать `docs/tech/api-contracts.md`;
- при необходимости обновить `docs/onboarding.md` и соседние документы, если изменились setup/runtime/workflow детали.

Когда запускать:
- после изменений backend API, DTO, auth, error-shape;
- после правок `backend/docs/openapi.yaml`;
- после изменений env-переменных, команд запуска, smoke-check или developer workflow.

Основные файлы:
- `.agents/skills/docs-updater/SKILL.md`
- `.agents/skills/docs-updater/agents/openai.yaml`

Пример вызова:

```text
Use $docs-updater to inspect the current diff, identify documentation drift, and update docs/tech/api-contracts.md plus any affected onboarding sections.
```

Ожидаемый результат:
- агент либо вносит минимальные правки в docs,
- либо явно пишет, что текущий diff не требует документарных изменений.
