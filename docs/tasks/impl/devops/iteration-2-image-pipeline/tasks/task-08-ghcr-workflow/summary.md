# Задача 08: GHCR workflow

## Итог

Добавлен отдельный workflow `.github/workflows/ghcr-images.yml` для build validation и publish runtime-образов в GHCR.

## Что покрыто

- `pull_request` в `main` -> только build validation без push;
- `push` в `main` -> publish с тегами `main` и `sha-*`;
- `push` semver tag `v*.*.*` -> publish с тегами `<version>`, `latest`, `sha-*`;
- `packages: write` ограничен publish job;
- для каждого сервиса задан явный `dockerfile` и отдельный GHCR image name.

## Почему решение соответствует scope

- workflow спроектирован по принципам skill `github-actions-templates`;
- publish логика отделена от тестов, линтов и deployment automation;
- tagging strategy остаётся детерминированной и человекочитаемой.
