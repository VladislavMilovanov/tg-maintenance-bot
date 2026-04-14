# Задача 09: Compose registry images

## Итог

Compose runtime дополнен registry override без смены основного entrypoint.

## Что сделано

- добавлен `devops/compose/compose.registry.yaml`;
- `backend`, `frontend`, `bot` получают `image:` из env-переменных с дефолтами на GHCR naming contract;
- local-build contract в `compose.yaml` не удалён и остаётся default;
- `Makefile` получил команды для pull и запуска registry stack.

## Review через docker-expert

- root `compose.yaml` не раздвоен;
- registry override не смешивает bind mounts и dev-only concerns;
- health/dependency contract для `postgres`, `backend`, `frontend`, `bot` сохранён.
