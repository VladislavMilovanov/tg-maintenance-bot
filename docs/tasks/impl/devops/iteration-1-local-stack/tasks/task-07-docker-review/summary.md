# Задача 07: Docker review gate

## Итог

Итоговая Docker-конфигурация iteration 1 отдельно проверена по принципам skill `docker-expert`.

## Build speed and cache behavior

- Multi-stage builds уже отделяют dependency/install шаги от runtime stages.
- Root `.dockerignore` дополнен для уменьшения объёма build context без смены root-scoped contract.
- Порядок копирования manifests до application sources сохранён и продолжает давать кешируемость.

## Image/runtime hygiene

- `backend`, `frontend`, `bot` используют отдельные runtime stages.
- Runtime images не несут dev-only tooling из builder stages.
- `frontend` остаётся на `Next.js standalone`, что уменьшает runtime payload.

## Security and user model

- Final images запускаются под non-root `appuser`.
- Секреты не захардкожены в Dockerfile и не передаются через build args, кроме безопасного публичного `NEXT_PUBLIC_API_URL`.
- Compose продолжает читать runtime config из `.env` и `env_file`.

## Local DX and compose ergonomics

- Один root entrypoint `compose.yaml` покрывает default stack и bot profile.
- `Makefile` даёт короткие команды для build, up, status, logs, smoke-check и cleanup.
- Отдельный runbook вынес operational detail из scattered docs в один документ.

## Follow-up

- GHCR workflow и запуск на registry-образах остаются scope iteration 2 и должны проектироваться через skill `github-actions-templates`.
