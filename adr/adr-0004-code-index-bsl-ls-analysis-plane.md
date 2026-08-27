---
title: code-index и BSL LS как read-only analysis plane для 1С-проектов Codex
id: ADR-0004
type: decision
status: accepted
created: 2026-08-27
updated: 2026-08-27
related_specifications:
  - SPEC-0011
affected_repositories:
  - kafka-tools
  - kafka-adapter
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-unit
supersedes:
  - ADR-0003
sources:
  - C:/Users/admin/Downloads/code-index-mcp/README_RU.md
---

# code-index и BSL LS как read-only analysis plane для 1С-проектов Codex

## Summary

- EDT-MCP остаётся authoritative model, единственным writer и primary validation gate.
- Unica заменяется общим federated `code-index` и repository-local BSL LS; оба используются только как supplementary read-only evidence.

## Context

Unica RLM не поддерживает Windows. `code-index` разделяет единственный daemon-индексатор и read-only MCP readers, поддерживает Windows и предоставляет структурный BSL-поиск и графы. BSL LS предоставляет focused diagnostics и language-semantic операции, но зависит от repository root и analyzer configuration. Ни один из компонентов не отражает live EDT model с теми же гарантиями, что EDT-MCP.

## Decision

1. Все persistent 1C mutations и primary diagnostics выполняются только назначенным repository-owned EDT-MCP.
2. Общий `bsl-indexer` daemon является единственным writer только для собственных `.code-index/` данных в repository roots и coordination/runtime в `CODE_INDEX_HOME`; он не является writer 1С-проекта.
3. Общий `code-index serve` предоставляет federated aliases через explicit read-only allowlist. Перед использованием проверяется health/freshness; при расхождении доверяется EDT.
4. BSL LS подключается repository-local через защитный proxy и explicit read-only allowlist только там, где есть локальная analyzer-конфигурация.
5. `v8std` сохраняется как standards/policy corpus.
6. Прямой filesystem access к 1С `src/**` остаётся запрещённым. Разрешённое чтение выполняется только EDT-MCP, `code-index` или BSL LS MCP.
7. Новые MCP tools не становятся доступными автоматически: allowlists и tests обновляются после отдельной классификации.

## Alternatives

- Сохранить Unica до официальной Windows-поддержки. Отклонено: workflow уже должен быть переносимым на Windows, а срок поддержки неизвестен.
- Использовать только `code-index`. Отклонено: индекс не является live EDT model и не предоставляет эквивалент focused language-server diagnostics.
- Использовать только BSL LS. Отклонено: MCP BSL LS ориентирован на конкретные файлы/символы и не заменяет индексный поиск по конфигурации и метаданным.
- Сделать `code-index` writer plane для исходников. Отклонено: его MCP `serve` read-only, а второй writer нарушил бы authoritative EDT invariant.
- Запускать отдельный daemon на каждый репозиторий. Отклонено: один daemon уже поддерживает несколько paths и проще в наблюдении и обслуживании.

## Consequences

- Windows получает постоянный supplementary analysis plane без Unica RLM.
- Индексный поиск и focused BSL semantics разделены по назначению; EDT остаётся arbiter project truth.
- Появляются внешние prerequisites: `bsl-indexer.exe`, BSL LS JAR и работающий daemon.
- Общий federated index уменьшает дублирование процессов, но требует строгого выбора alias.

## Risks

- Eventual consistency индекса может вернуть stale evidence.
- Несогласованные `CODE_INDEX_HOME` у daemon и MCP делают daemon невидимым.
- Неподходящая версия публичного `code-index` без BSL extension даст неполную tool surface.
- BSL LS proxy снижает, но не устраняет риски несовместимости JAR/Java/MCP protocol.
- Hooks являются guardrail и не заменяют sandbox/authorization boundary.

## Evidence

- `repo:kafka-tools:ai/.codex/config.toml`
- `repo:kafka-tools:ai/code-index/daemon.toml.template`
- `repo:kafka-tools:ai/mcp/code-index-mcp.ps1`
- `repo:kafka-tools:ai/hooks/guard-1c-routing.ps1`
- `repo:kafka-adapter:.codex/mcp/bsl-ls-proxy.mjs`
- `repo:kafka-adapter:.codex/config.toml`

## Related Documents

- [SPEC-0011](../sdd/spec-0011-code-index-bsl-ls-routing.md)
- Supersedes [ADR-0003](adr-0003-edt-authoritative-writer.md).
