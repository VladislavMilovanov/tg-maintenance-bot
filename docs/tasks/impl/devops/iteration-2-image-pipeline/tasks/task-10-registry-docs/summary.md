# Задача 10: Registry docs

## Итог

Пользовательские и DevOps-документы выровнены под новый GHCR image pipeline и registry-runtime mode.

## Что покрыто

- `README.md` оставляет local-build основным стартом и добавляет обзор GHCR workflow;
- `docs/onboarding.md` объясняет, когда использовать registry-run;
- `docs/docker-compose-local.md` описывает команды pull и запуск из GHCR;
- DevOps docs указывают, где лежит registry override и зачем он нужен.

## Синхронизированные документы

- `README.md`
- `docs/onboarding.md`
- `docs/docker-compose-local.md`
- `devops/README.md`
- `devops/compose/README.md`

## Результат для команды

- без чтения YAML понятно, когда публикуются образы;
- понятно, какие теги выбирать для локального запуска;
- registry-run остаётся дополнением к compose-first local workflow, а не заменой ему.
