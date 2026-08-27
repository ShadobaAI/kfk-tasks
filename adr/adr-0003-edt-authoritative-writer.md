---
title: EDT-MCP как единственный writer для 1С-проектов Codex
id: ADR-0003
type: decision
status: superseded
created: 2026-08-26
updated: 2026-08-27
related_specifications:
  - SPEC-0010
affected_repositories:
  - kafka-tools
  - kafka-adapter
  - kafka-adapter-conv
  - kafka-adapter-tests-unit
superseded_by:
  - ADR-0004
---

# EDT-MCP как единственный writer для 1С-проектов Codex

## Summary

- EDT-MCP является authoritative project/platform model, единственным writer и primary validation gate для 1С-проектов workspace.
- Unica остаётся явно ограниченным read-only analysis layer, а v8std — read-only standards/policy corpus.

## Context

EDT-MCP и Unica способны работать с одними сериализованными 1С-исходниками, но используют разные модели и механизмы синхронизации. Разделение записи по типам артефактов создаёт два writer plane и делает результат зависимым от порядка синхронизации. v8std решает другую задачу: предоставляет нормативные материалы, но не знает live state проекта и платформы.

## Decision

1. Все persistent 1C mutations, включая BSL, metadata, forms, rights, DCS, XDTO, translations и database update, выполняются через назначенный repository-owned EDT-MCP.
2. Прямой filesystem access агента к configuration/extension `src/**` запрещён как для чтения, так и для записи.
3. Unica ограничивается explicit read-only allowlist; default для новых tools — deny.
4. EDT diagnostics являются primary gate. Unica diagnostics допустимы только как secondary evidence.
5. Project/platform facts устанавливаются EDT; general/corporate standards — целевым v8std corpus.
6. Standards и snippet analysis используют один MCP с именем `v8std`. Endpoint принадлежит пользовательской конфигурации: по умолчанию используется `https://ai.v8std.ru/mcp`, пользователь может заменить `url` на локальный endpoint. Agent policy не классифицирует передаваемый код и не переключает endpoint.

## Alternatives

- Разделить writers по типам объектов. Отклонено из-за конфликтов model/disk state и зависимости от порядка синхронизации.
- Использовать только EDT-MCP. Отклонено: Unica полезна для дополнительного index/graph анализа, v8std — для нормативного retrieval.
- Оставить ограничения только в prompt. Отклонено: MCP allowlist и PreToolUse guard дают проверяемый defense-in-depth.

## Consequences

- Маршрутизация становится предсказуемой, а validation привязан к той же модели, которая выполняет запись.
- Unica mutation/runtime возможности недоступны в этом workflow.
- Выбор публичного или локального v8std и ответственность за передаваемые данные находятся на стороне пользователя, задающего `mcp_servers.v8std.url`.
- Policy и tool inventory требуют пересмотра при обновлении MCP.

## Risks

- Codex hooks документированы как guardrail, а не полная enforcement boundary; invariant дополнительно закреплён в AGENTS и skills.
- Ошибка в tool names может скрыть требуемый read-only tool или оставить policy неполной; allowlist и tests должны обновляться вместе с MCP.
- Plugin-level Unica policy действует для пользователя шире одного repository.

## Evidence

- `repo:kafka-tools:ai/AGENTS.md`
- `repo:kafka-tools:ai/.codex/config.toml`
- `repo:kafka-tools:ai/hooks/guard-1c-routing.ps1`
- `repo:kafka-tools:ai/.codex/skills/1c-routing/SKILL.md`

## Related Documents

- [SPEC-0010](../sdd/spec-0010-codex-1c-routing.md)
- Superseded by [ADR-0004](adr-0004-code-index-bsl-ls-analysis-plane.md).
