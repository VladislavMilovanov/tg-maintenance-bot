# Задача 08: GHCR workflow

## Цель

Подготовить отдельный GitHub Actions workflow для сборки и публикации runtime-образов проекта в GHCR без разрастания в полный CI/CD pipeline.

## Подход

- использовать skill `github-actions-templates` как основной шаблон проектирования workflow;
- оставить PR безопасным: только build validation, `push: false`;
- публиковать образы только на trusted events:
  - `push` в `main`;
  - semver tags `v*.*.*`;
- публиковать образы по сервисам, а не как один meta-image, чтобы сохранить независимость runtime artifacts и traceability к Dockerfile.

## Реализация

- создать `.github/workflows/ghcr-images.yml`;
- использовать official actions:
  - `actions/checkout`
  - `docker/setup-buildx-action`
  - `docker/login-action`
  - `docker/metadata-action`
  - `docker/build-push-action`
- настроить `concurrency` по `github.ref`;
- оставить top-level `permissions: contents: read`;
- выдавать `packages: write` только publish job;
- собирать `backend`, `frontend`, `bot` отдельными matrix entries с явным `context: .` и собственным `dockerfile`;
- генерировать теги:
  - `main` и `sha-*` на branch publish;
  - `<version>`, `latest`, `sha-*` на semver tag publish;
- labels собирать через `docker/metadata-action`;
- использовать GHA cache для buildx.

## Auth и инфраструктурные предпосылки

- базовый auth path: `GITHUB_TOKEN` для same-repo publish в `ghcr.io`;
- предполагается, что GitHub Actions в репозитории имеет право `Read and write permissions` для packages;
- если policy пакетов ограничивает publish, это считается внешней настройкой repository/org, а не проблемой структуры workflow.

## Почему так

- publish на PR запрещён, чтобы не публиковать непроверенный или недоверенный код;
- разделение образов по сервисам лучше соответствует существующим Dockerfile и compose contract;
- workflow не включает тесты, линтеры и deploy automation, потому что задача ограничена image pipeline.
