# Задача 05: Compose local runbook

## Цель

Выделить отдельный runbook локального запуска полного проекта через Docker Compose как основной операционный сценарий iteration 1.

## Решения

- Source of truth для container workflow: отдельный документ `docs/docker-compose-local.md`.
- Основной UX документа строится вокруг `make stack-*`.
- Raw `docker compose` упоминается только как reference.

## Состав работ

- Описать prerequisites и подготовку `.env`.
- Описать сборку default stack и запуск с bot profile.
- Описать smoke-check, просмотр логов, остановку, очистку и cold start.
- Добавить типовые проблемы по Docker daemon, bot token, readiness, frontend API URL и занятым портам.

## Артефакты

- `docs/docker-compose-local.md`

## Критерии завершения

- Runbook покрывает весь базовый lifecycle iteration 1.
- По документу можно поднять стек без чтения исходников и без обращения к старому host-run сценарию.
