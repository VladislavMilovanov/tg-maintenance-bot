# Задача 06: Docs sync for compose-first local entrypoint

## Цель

Убрать documentation drift между старым host-run onboarding и фактическим compose-first full-stack workflow.

## Решения

- `README.md` и `docs/onboarding.md` переводятся на compose-first narrative.
- `backend/README.md` обновляется минимально и сохраняет host-run как component fallback.
- Приоритетный источник container workflow: `docs/docker-compose-local.md`.

## Состав работ

- Обновить quick start и структуру репозитория в `README.md`.
- Обновить onboarding под основной compose-first путь.
- Развести основной full-stack запуск и optional host-run сценарии по разным разделам.
- Синхронизировать ссылки на `devops/`, `compose.yaml`, `Makefile` и новый runbook.

## Артефакты

- `README.md`
- `docs/onboarding.md`
- `backend/README.md`

## Критерии завершения

- Основные entrypoint docs не противоречат друг другу.
- Compose-first workflow описан как основной локальный путь.
- Host-run режим остаётся доступным, но явно вторичным.
