# Итерация 1: Local Docker Compose Stack

## Цель

Довести уже начатый контейнерный слой до завершённого compose-first local workflow с согласованными runtime-образами, единым root entrypoint, короткими `make`-командами и синхронизированной документацией.

## Scope

- завершение task 01–07 внутри iteration 1;
- формализация runtime-образов `backend`, `frontend`, `bot`;
- закрепление `compose.yaml` как единственного full-stack entrypoint;
- финализация `Makefile`-команд для full-stack lifecycle;
- отдельный runbook локального Docker Compose workflow;
- docs sync entrypoint-документов;
- обязательный review-gate по skill `docker-expert`.

Вне scope:
- GHCR workflow и registry-image mode;
- полноценный CI/CD;
- deployment automation;
- production-hardening beyond local runtime.

## Ключевые решения

- Основной локальный full-stack путь: `make stack-build` + `make stack-up`.
- `compose.yaml` остаётся единственным корневым compose entrypoint.
- `bot` остаётся optional service через compose profile.
- Root `.dockerignore` сохраняется как часть общего build contract с `context: .`.
- Host-run команды сохраняются как fallback для точечной разработки компонентов.

## Задачи

- [Задача 01: Архитектура devops-артефактов и целевая структура `devops/`](tasks/task-01-devops-artifacts-structure/plan.md)
- [Задача 02: Runtime images and build contract](tasks/task-02-runtime-images/plan.md)
- [Задача 03: Root compose as the only local full-stack entrypoint](tasks/task-03-root-compose/plan.md)
- [Задача 04: Makefile stack commands](tasks/task-04-makefile-stack-commands/plan.md)
- [Задача 05: Compose local runbook](tasks/task-05-compose-local-runbook/plan.md)
- [Задача 06: Docs sync for compose-first local entrypoint](tasks/task-06-docs-sync/plan.md)
- [Задача 07: Docker review gate](tasks/task-07-docker-review/plan.md)

## Критерии завершения

- `compose.yaml` и `Makefile` образуют один понятный local full-stack contract.
- `README.md`, `docs/onboarding.md` и compose runbook не противоречат друг другу.
- Docker-конфигурация отдельно проверена по принципам `docker-expert`.
- Итерация готовит dependency-ready базу для следующего GHCR этапа без смешивания scope.
