---
title: Верификация внешней совместимости
id: SPEC-0008
type: specification
status: draft
owner:
created: 2026-08-03
updated: 2026-08-03
github_issue:
affected_repositories:
  - kafka-adapter
  - kafka-adapter-conv
affected_components:
  - connector-runtime
  - conversion-data-compatibility
related_adrs: []
tags:
  - specification
  - verification
  - backlog
sources:
  - "repo:kfk-tasks:sdd/migration-audit-spec-0007.md"
---

# Верификация внешней совместимости

## Краткое описание

- Сохранить два долговечных verification gaps, которые нельзя надёжно получить простым чтением текущего source.
- Не переносить быстро устаревающие counts, diagnostics, file inventories и текущие checkout observations.
- Не считать заявленную внешнюю совместимость подтверждённой без runtime evidence.

## Контекст

При удалении Memory Bank обнаружены два значимых ограничения: runtime Kafka/connector не проверялся для принятого baseline, а совместимость расширения KFK со всей линией Conversion Data `3.1+` не доказана. Остальные прежние pending items являются быстро устаревающими observations или легко повторно получаются из текущего checkout и не сохраняются.

## Проблема

Source и metadata подтверждают структуру и declared versions, но не доказывают runtime behavior внешней компоненты и attachment compatibility со всеми обновлениями внешней конфигурации.

## Цель

Зафиксировать минимальный backlog для проверки внешних compatibility claims без создания общего хранилища текущего состояния проектов.

## Не входит в задачу

- Не выполнять runtime или compatibility tests в рамках создания backlog.
- Не сохранять текущие EDT diagnostic counts, feature counts и layout observations.
- Не исправлять product source или documentation.
- Не утверждать поддержку непроверенных versions.

## Область проверки

### Kafka connector runtime

- Репозиторий: `kafka-adapter`.
- Известное ограничение: source, embedded artifact и documentation baseline `Simple Kafka Connector 1C 1.9.2+` проверены в SPEC-0002, но runtime checks были waived.
- Требуется: validation, batch atomicity, diagnostics и end-to-end send/read на явно выбранных Kafka/connector versions.
- Evidence: exact versions, environment, scenarios и результаты.

### Conversion Data compatibility

- Репозиторий: `kafka-adapter-conv`.
- Известное ограничение: проверен attachment к одному local checkout; это не доказывает совместимость с каждым обновлением линии `КД 3.1+`.
- Требуется: определить поддерживаемую version matrix и проверить adopted metadata, form attachment paths и end-to-end generated contract scenario.
- Evidence: exact КД version, focused `conv_edt` diagnostics, scenario result и deviations.

## Функциональные требования

- Перед реализацией утвердить конкретный item и exact version matrix.
- Текущие source/tests/EDT results имеют приоритет над историческими observations.
- Закрытие item требует воспроизводимых steps и versioned evidence.
- Documentation claims обновляются только после проверки.

## Нефункциональные требования

- Использовать bounded navigation.
- 1С-изменения выполнять только через назначенный EDT MCP.
- Соблюдать общий network limit.
- Не хранить credentials, raw dumps и absolute environment paths.

## План реализации

Не определён. Рекомендуется отдельная approved SDD для каждого compatibility contour.

## Совместимость и миграции

Эта draft specification сохраняет только durable backlog из retired `pending-verification.md`. Она не заменяет product documentation и не меняет compatibility guarantees.

## Проверка

- Сохранены оба durable external compatibility gaps.
- Быстро устаревающие observations не перенесены.
- Historical claims не представлены как current verified state.

## Риски

- Runtime tests могут потребовать внешние artifacts свыше network limit.
- Неопределённая version matrix делает compatibility claim непроверяемым.

## Критерии приёмки

- Для выбранного contour утверждены exact versions и scenarios.
- Собраны воспроизводимые results.
- Product claims согласованы с evidence.

## Открытые вопросы

- Какой compatibility contour проверять первым?
- Какие exact Kafka, connector и Conversion Data versions входят в поддерживаемую matrix?

## Результат реализации

Не реализовано. Создан только migration-safe backlog.

## Отклонения от спецификации

Не зафиксированы.

## Связанные документы

- `tasks/sdd/spec-0007-memory-bank-retirement.md`
- `tasks/sdd/migration-audit-spec-0007.md`
- `tasks/sdd/spec-0002-simple-kafka-adapter-1-9-2.md`
