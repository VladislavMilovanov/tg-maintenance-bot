# Задача 04: Makefile stack commands

## Цель

Закрепить `Makefile` как короткую user-facing оболочку поверх `docker compose` для основного локального lifecycle полного стека.

## Решения

- `db-*` команды сохраняются как database-only workflow.
- `stack-*` команды становятся основным full-stack UX.
- Основной набор iteration 1:
  - `stack-build`
  - `stack-build-bot`
  - `stack-up`
  - `stack-up-bot`
  - `stack-down`
  - `stack-clean`
  - `stack-ps`
  - `stack-logs`
  - `stack-logs-%`
  - `stack-health`

## Состав работ

- Уточнить `.PHONY` и lifecycle contract для всех stack targets.
- Добавить явную команду полной очистки compose state.
- Синхронизировать docs, чтобы именно `stack-*` рекламировались как основной первый запуск.
- Явно ограничить роль `db-*` команд backend/integration workflow.

## Артефакты

- `Makefile`

## Критерии завершения

- У `Makefile` есть однозначный compose-first lifecycle для iteration 1.
- Команды покрывают build, up, down, clean, status, logs и smoke-check.
- Docs не рекламируют `db-*` + host-run как основной first-run путь полного стека.
