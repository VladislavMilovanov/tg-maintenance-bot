# Задача 01: Стек, ADR, conventions

## Итог

Задача завершена в рамках итерации 0.

## Что сделано

- создан `docs/adr/adr-002-backend-stack.md` с решением по backend-стеку и границам ответственности;
- создан `tg-maintenance-bot/.cursor/rules/conventions.mdc`;
- в `docs/vision.md` добавлена ссылка на `ADR-002`;
- в `docs/plan.md` добавлена подготовительная итерация 0 `Backend bootstrap`;
- в `docs/tasks/tasklist-backend.md` задача 01 переведена в `Done` и связана с iteration package.

## Принятые решения

- backend фиксируется на Python 3.12+ и FastAPI;
- `uv` используется как базовый Python toolchain;
- `bot` и будущий `web` рассматриваются как thin clients поверх backend API;
- стандартные backend-команды резервируются под `Makefile`.
