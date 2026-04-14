# Задача 03: Root compose as the only local full-stack entrypoint

## Итог

Задача закрыта как формализация уже существующего full-stack `compose.yaml` и синхронизация документации вокруг него.

## Что закреплено

- Корневой `compose.yaml` является единственным основным operator-facing entrypoint локального контейнерного стека.
- Default stack: `postgres`, `backend`, `frontend`.
- Optional profile `bot` включает контейнер Telegram-бота только при явном запуске.
- Compose сохраняет local-build mode и не смешивается с registry-image режимом iteration 2.

## Runtime contract

- `docker compose up -d` эквивалентен default stack без бота.
- `COMPOSE_PROFILES=bot docker compose up -d` поднимает тот же стек плюс `bot`.
- `postgres` использует named volume `postgres_data`.
- Published ports оставлены только для `backend` и `frontend`, что соответствует local DX iteration 1.

## Review через `docker-expert`

- Health/readiness оставлены только там, где они дают orchestration value: `postgres`, `backend`.
- Лишние volume mounts не вводились.
- Env configuration остаётся в `.env` и `env_file`, а не хардкодится в compose beyond safe defaults.
