# Kafka Adapter — задачи, SDD и ADR

[![Issues](https://img.shields.io/github/issues/ShadobaAI/kfk-tasks)](https://github.com/ShadobaAI/kfk-tasks/issues)

Репозиторий координации разработки экосистемы [1С: Адаптер Kafka](https://github.com/ShadobaAI/kafka-adapter).

## Назначение

- **GitHub Issues** — постановка, обсуждение и контроль задач.
- **GitHub Projects** — визуальное представление хода работ.
- **SDD** — требования, design, acceptance criteria и фактические результаты значимых изменений.
- **ADR** — устойчивые архитектурные решения и их последствия.

Product architecture, API, operations и user guidance сопровождаются в owning repositories. Текущие source и tests имеют приоритет над документацией при расхождении.

## Структура

| Путь | Назначение |
|---|---|
| [`sdd/`](sdd/README.md) | Specifications, lifecycle, index и template |
| [`adr/`](adr/README.md) | Architecture decisions, lifecycle, index и template |
| [`AGENTS.md`](AGENTS.md) | Repository-specific инструкции для агентов |

## Issues и управление работами

Задачи создаются в [GitHub Issues](https://github.com/ShadobaAI/kfk-tasks/issues), а их состояние отслеживается на [доске GitHub Projects](https://github.com/users/ShadobaAI/projects/3/views/1).

В Issue укажи:

- затронутые репозитории и компоненты;
- текущее и ожидаемое поведение;
- шаги воспроизведения либо ожидаемый результат;
- compatibility constraints и acceptance criteria;
- связанные SPEC, ADR, pull requests и commits.

Issue используется для обсуждения и контроля. Устойчивые требования значимого изменения фиксируются в SDD, а долговременные architecture decisions — в ADR. Идентификаторы `SPEC-NNNN` и `ADR-NNNN` не зависят от номера Issue.

## Рабочий процесс

1. Определи owning repositories и прочитай их `AGENTS.md`.
2. Для нетривиального или multi-repository изменения создай draft SDD на русском языке.
3. Получи явное утверждение SDD до реализации.
4. Создай ADR, если меняется долговременная architecture или component boundary.
5. После реализации запиши фактический результат, проверки и отклонения.
6. Обнови owning repository documentation, если изменился её contract.

Подробные правила находятся в [SDD index](sdd/README.md), [ADR index](adr/README.md) и workspace/repository `AGENTS.md`.

