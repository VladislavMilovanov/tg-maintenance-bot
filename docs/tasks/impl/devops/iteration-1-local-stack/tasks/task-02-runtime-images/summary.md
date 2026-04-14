# Задача 02: Runtime images and build contract

## Итог

Задача закрыта как ревизия и формализация уже существующих runtime-образов под локальный compose-first workflow.

## Что зафиксировано

- `backend` и `bot` оставлены на multi-stage `python:3.12-slim` с разделением `builder` и `runtime`.
- `frontend` оставлен на multi-stage `node:20-slim` с `deps`, `builder`, `runtime` и `Next.js standalone`.
- Все final stages запускаются под non-root пользователем `appuser`.
- `backend` и `frontend` публикуют порты `8000` и `3000`; `bot` работает без published port.
- Runtime mode iteration 1 для всех сервисов остаётся image-only без bind mounts.
- `bot` закреплён как optional service через compose profile `bot`.

## Что уточнено по build contract

- Root build context `context: .` сохранён как осознанное решение, потому что Dockerfile используют файлы из нескольких корневых директорий.
- Отдельные service-level `.dockerignore` не добавлялись: при общем root context они не дают выигрыша и только усложняют contract.
- Root `.dockerignore` усилен для сокращения build context:
  - исключены `.github`;
  - исключены `backend/tests` и `backend/tests_integration`;
  - исключён `frontend/.env.local`.

## Review через `docker-expert`

- Build speed and cache behavior: dependency manifests копируются до application sources, multi-stage layering сохранён.
- Image/runtime hygiene: runtime stages не тянут dev tooling из builder stages.
- Security and user model: final images запускаются non-root, секреты не baked into layers.
- Local DX: текущий image-only contract лучше соответствует compose-first iteration 1, чем bind-mount режим по умолчанию.
