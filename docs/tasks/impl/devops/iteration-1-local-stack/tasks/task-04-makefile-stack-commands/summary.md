# Задача 04: Makefile stack commands

## Итог

`Makefile` закреплён как основной user-facing слой над `docker compose` для full-stack сценария iteration 1.

## Что обновлено

- В `.PHONY` добавлены все stack targets, включая `stack-logs-%`.
- Добавлена команда `stack-clean` для сценария полной очистки compose state и volumes.
- `stack-up` закреплён как запуск default stack без бота.
- `stack-up-bot` закреплён как запуск полного стека с profile `bot`.
- `stack-health` остаётся лёгким backend smoke-check без внешних секретов.

## Что оставлено без изменения

- `db-*` команды сохранены для database-only и backend integration workflow.
- Host-run команды `run`, `run-backend`, `web-dev` сохранены как component-level fallback для точечной разработки.

## Review через `docker-expert`

- Основной container UX сфокусирован на коротких compose wrappers, а не на длинных raw-командах.
- Отдельная команда очистки уменьшает вероятность ручных ошибок при cold start и повторной диагностике.
