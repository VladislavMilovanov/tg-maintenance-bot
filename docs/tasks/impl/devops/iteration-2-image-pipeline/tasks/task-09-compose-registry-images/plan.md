# Задача 09: Compose registry images

## Цель

Сохранить root `compose.yaml` основным local-stack entrypoint и добавить проверяемый registry-runtime mode без появления второго конкурирующего compose lifecycle.

## Подход

- использовать skill `docker-expert` для review runtime/image contract;
- не менять local-build default path;
- включать registry mode через merge root `compose.yaml` с `devops/compose/compose.registry.yaml`;
- заменять только `build` на `image` для runtime-сервисов проекта;
- не дублировать `postgres` и общую orchestration-логику.

## Реализация

- добавить `devops/compose/compose.registry.yaml`;
- завести env-driven image refs:
  - `BACKEND_IMAGE`
  - `FRONTEND_IMAGE`
  - `BOT_IMAGE`
- использовать безопасные дефолты на GHCR main tags;
- добавить короткие команды `Makefile`:
  - `stack-pull`
  - `stack-up-registry`
  - `stack-up-registry-bot`
- оставить `stack-ps`, `stack-logs`, `stack-health`, `stack-down`, `stack-clean` универсальными.

## Правила режима

- local-build режим остаётся default path для разработки и onboarding;
- registry-image режим нужен для smoke/verification published images и повторяемого запуска без локальной сборки;
- bot profile сохраняет optional nature и в registry режиме.
