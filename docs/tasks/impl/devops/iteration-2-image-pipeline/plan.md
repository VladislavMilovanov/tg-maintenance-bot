# Iteration 2: Image Pipeline via GitHub Actions

## Цель

Добавить минимальный pipeline публикации runtime-образов в GHCR и перевести compose-слой к двухрежимному контракту: локальная сборка остаётся default path, а registry-image режим становится отдельным проверяемым operational scenario.

## Зависимости

- артефакты iteration 0 local stack: `compose.yaml`, `Makefile`, Dockerfile сервисов и compose-first docs;
- review-гейт из задачи 07, который зафиксировал текущий Docker runtime contract как базу для publish workflow.

## Scope

В итерацию входят:
- workflow сборки и публикации `backend`, `frontend`, `bot` в `ghcr.io`;
- compose override для запуска на registry-образах;
- operator-facing `Makefile` команды для registry режима;
- docs sync по GHCR, тегам и локальному registry-run.

В итерацию не входят:
- полный CI для тестов и линтеров;
- deployment automation;
- удалённые окружения;
- production hardening beyond текущего runtime contract;
- multi-arch build.

## Обязательные skills

- `github-actions-templates` — для проектирования workflow публикации и tagging strategy.
- `docker-expert` — для review image contract, compose override и разделения local-build/runtime concerns.

## Ключевые решения

- publish workflow хранится отдельно в `.github/workflows/ghcr-images.yml` и не смешивается с CI/testing;
- trusted publish events: `push` в `main` и semver tags `v*.*.*`;
- `pull_request` выполняет только build validation без push;
- публикуются три отдельных image artifacts:
  - `ghcr.io/vladislavmilovanov/tg-maintenance-bot-backend`
  - `ghcr.io/vladislavmilovanov/tg-maintenance-bot-frontend`
  - `ghcr.io/vladislavmilovanov/tg-maintenance-bot-bot`
- root `compose.yaml` остаётся основным entrypoint;
- registry runtime включается через merge с `devops/compose/compose.registry.yaml`, а не через второй основной compose-файл;
- `postgres` остаётся локальным compose service и не публикуется в GHCR.

## Acceptance Snapshot

- `self-check`: workflow валиден, публикует три image в GHCR на trusted events и не выполняет push на PR.
- `self-check`: registry override поднимает тот же стек на GHCR-образах без ломки local-build path.
- `user-check`: человек находит workflow, понимает tags/permissions и запускает стек из GHCR без чтения YAML.
