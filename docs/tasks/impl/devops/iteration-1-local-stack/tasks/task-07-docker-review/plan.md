# Задача 07: Docker review gate

## Цель

Закрыть iteration 1 только после отдельного review-gate итоговой Docker-конфигурации по принципам skill `docker-expert`.

## Scope review

- `devops/backend/Dockerfile`
- `devops/frontend/Dockerfile`
- `devops/bot/Dockerfile`
- `.dockerignore`
- `compose.yaml`
- `Makefile` в части container UX

## Структура review

- build speed and cache behavior;
- image/runtime hygiene;
- security and user model;
- local DX and compose ergonomics.

## Критерии завершения

- Существенные замечания исправлены в iteration 1.
- Follow-up вопросы, не блокирующие локальный стек, явно вынесены в summary.
- Итог summary описывает не только факт review, но и конкретные выводы.
