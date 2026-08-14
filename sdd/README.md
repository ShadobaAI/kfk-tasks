# Specification-Driven Development

## Назначение

SDD фиксирует требования, design, критерии приёмки, результат реализации и отклонения значимых изменений. Идентификатор `SPEC-NNNN` стабилен и не зависит от номера Issue.

Все новые SDD пишутся на русском языке. Technical identifiers, команды и пути сохраняются без перевода. Historical specifications на английском языке не переводятся автоматически.

## Когда требуется SDD

Утверждённая SDD обязательна до реализации:

- нетривиального изменения поведения;
- изменения публичного API;
- изменения схемы данных;
- изменения нескольких репозиториев.

Агент может создать `draft`, но не начинает реализацию до явного утверждения пользователем. Для локального bug fix, focused test, documentation-only change или routine tooling correction SDD не требуется, если контракты не меняются.

## Жизненный цикл

```text
draft -> approved -> in-progress -> implemented -> verified
draft/approved -> rejected
non-terminal -> superseded
```

| Статус | Минимальное содержание |
|---|---|
| `draft` | Проблема, цель, scope, требования, открытые вопросы |
| `approved` | Решены blocking questions, определены design и acceptance criteria |
| `in-progress` | Указан план реализации |
| `implemented` | Записаны фактический результат, проверки и отклонения |
| `verified` | Acceptance evidence подтверждены пользователем или независимой проверкой |
| `rejected` | Зафиксированы причина и рассмотренные alternatives |
| `superseded` | Указана replacing specification |

## Правила

- Имя файла: `spec-nnnn-short-name.md`.
- Metadata ID: `SPEC-NNNN`.
- Один capability может охватывать несколько репозиториев; каждый указывается явно.
- `Non-goals` ограничивают scope.
- Acceptance criteria должны быть наблюдаемыми.
- После реализации записывается actual result, а не планируемый.
- Durable architecture decisions связываются с ADR из [`../adr`](../adr/README.md).

## Индекс

| ID | Спецификация | Статус |
|---|---|---|
| [SPEC-0001](spec-0001-memory-bank-foundation.md) | Project Memory Bank and SDD Foundation | `verified` |
| [SPEC-0002](spec-0002-simple-kafka-adapter-1-9-2.md) | Upgrade Simple-Kafka_Adapter to 1.9.2+ | `verified` |
| [SPEC-0003](spec-0003-bsl-sonarqube-remediation.md) | Устранение проблем BSL по результатам SonarQube | `draft` |
| [SPEC-0004](spec-0004-adapter-agents-pilot.md) | Пилотные инструкции для агентов kafka-adapter | `verified` |
| [SPEC-0005](spec-0005-repository-agents-rollout.md) | Инструкции остальных репозиториев | `verified` |
| [SPEC-0006](spec-0006-workspace-agents.md) | Общие инструкции мультирепозитория | `verified` |
| [SPEC-0007](spec-0007-memory-bank-retirement.md) | Вывод Memory Bank из эксплуатации | `verified` |
| [SPEC-0008](spec-0008-project-verification-backlog.md) | Верификация внешней совместимости | `draft` |
| [SPEC-0009](spec-0009-kfk-code-placement.md) | Переразмещение логики объектов спецификаций КФК | `implemented` |

Для новой спецификации скопируй [template](template.md).
