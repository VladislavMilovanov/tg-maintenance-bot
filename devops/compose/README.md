# Shared Compose Artifacts

Каталог зарезервирован для общих DevOps-файлов, которые относятся к Compose-слою, но не должны лежать в корне репозитория.

Сюда добавляются:

- `compose.override*.yaml` и другие compose-fragments;
- env-шаблоны и примеры для compose-сценариев;
- helper scripts и entrypoints, используемые несколькими сервисами;
- вспомогательные файлы для локального container workflow.

Корневой `compose.yaml` остаётся основным operator-facing entrypoint локального стека.

## Текущие артефакты

- `compose.registry.yaml` — override для запуска runtime-сервисов на GHCR-образах вместо локальной сборки.
