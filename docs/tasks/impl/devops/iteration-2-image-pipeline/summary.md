# Iteration 2: Image Pipeline via GitHub Actions

## Итог

Добавлен preparatory image pipeline для GHCR и registry-runtime mode поверх уже существующего local compose entrypoint.

## Что сделано

- добавлен workflow `.github/workflows/ghcr-images.yml`, спроектированный по принципам `github-actions-templates`;
- publish path ограничен trusted events: `main` и semver tags;
- PR workflow выполняет только build validation без публикации;
- для compose добавлен registry override `devops/compose/compose.registry.yaml`;
- в `Makefile` добавлены команды `stack-pull`, `stack-up-registry`, `stack-up-registry-bot`;
- docs синхронизированы так, чтобы local-build оставался default first-run path, а registry-run был отдельным operational сценарием.

## Проверки

- workflow YAML проходит синтаксическую проверку и не содержит publish-step на `pull_request`;
- merged compose config для `compose.yaml` и `devops/compose/compose.registry.yaml` переключает runtime-сервисы на GHCR `image:` без второго main entrypoint;
- `make -n stack-pull stack-up-registry stack-up-registry-bot` подтверждает operator-facing contract для registry-run;
- после push в `origin/main` GitHub создал первый run workflow `GHCR Images` на событии `push`.

## Review gates

- workflow и tagging strategy спроектированы с явной опорой на skill `github-actions-templates`;
- compose/image contract отдельно проверен через принципы `docker-expert`: root entrypoint не раздвоен, local-build и registry-runtime не смешаны в конкурирующие lifecycle.

## Ограничения

- publish path предполагает same-repo GHCR access через `GITHUB_TOKEN`;
- если package/org policy GitHub запретит push в GHCR, потребуется инфраструктурная настройка repository permissions, но сам workflow contract остаётся корректным.
