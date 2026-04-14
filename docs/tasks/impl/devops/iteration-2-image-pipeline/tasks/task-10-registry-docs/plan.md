# Задача 10: Registry docs

## Цель

Сделать новый GHCR pipeline и registry-run mode понятными без чтения workflow YAML.

## Подход

- сохранить local-build путь основным first-run сценарием;
- описать registry-run как дополнительный operational сценарий;
- синхронизировать operator-facing docs с фактическими командами и image naming contract.

## Реализация

- обновить `README.md`;
- обновить `docs/onboarding.md`;
- обновить `docs/docker-compose-local.md`;
- дополнить `devops/README.md` и `devops/compose/README.md` упоминанием registry override;
- описать:
  - путь к workflow;
  - trusted publish events;
  - tagging strategy `main`, `sha-*`, semver, `latest`;
  - expected permissions и `GITHUB_TOKEN` auth path;
  - команды `make stack-pull`, `make stack-up-registry`, `make stack-up-registry-bot`;
  - различие между local-build и registry runtime.
