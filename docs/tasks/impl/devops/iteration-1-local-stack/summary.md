# Итерация 1: Local Docker Compose Stack

## Итог

Итерация завершена как compose-first локальный контейнерный слой проекта.

## Что реализовано

- `devops/` закреплён как место implementation-level Docker-артефактов;
- runtime-образы `backend`, `frontend`, `bot` формализованы под local-build contract;
- `compose.yaml` закреплён как единственный full-stack entrypoint;
- `Makefile` покрывает build, up, status, logs, smoke-check и cleanup сценарии;
- добавлен отдельный runbook [docs/docker-compose-local.md](../../../../docker-compose-local.md);
- `README.md`, `docs/onboarding.md` и `backend/README.md` синхронизированы под compose-first workflow;
- итоговая Docker-конфигурация отдельно проверена по принципам `docker-expert`.

## Проверочный baseline

- `make stack-build`
- `make stack-up`
- `make stack-ps`
- `make stack-health`
- `make stack-down`

## Follow-up

- GHCR workflow, registry tags и compose-on-registry остаются scope iteration 2;
- для task 08 должен использоваться skill `github-actions-templates`;
- registry-mode не смешивается с local-build contract iteration 1.
