# Задача 05: Compose local runbook

## Итог

Добавлен отдельный runbook `docs/docker-compose-local.md` как основной entrypoint для локального container workflow.

## Что покрыто

- prerequisites и подготовка `.env`;
- сборка образов default stack и stack с bot profile;
- запуск через `make stack-up` и `make stack-up-bot`;
- smoke-check через `make stack-ps` и `make stack-health`;
- просмотр логов всего стека и одного сервиса;
- остановка через `make stack-down`;
- полная очистка через `make stack-clean`;
- типовые проблемы и диагностические действия.

## Почему это важно

- `README.md` и onboarding больше не обязаны держать весь operational detail внутри себя;
- container workflow получил отдельный source of truth;
- host-run сценарии отделены от основного full-stack запуска.
