---
title: kafka-adapter-examples Repository
scope: kafka-adapter-examples
repository: kafka-adapter-examples
type: repository
status: verified
updated: 2026-07-29
components:
  - examples
  - test-fixtures
  - conversion-handlers
sources:
  - "repo:kafka-adapter-examples:README.md"
  - "repo:kafka-adapter-examples:CommonModule.кфк_т_ТестовыеДанные"
  - "repo:kafka-adapter-examples:CommonModule.кфк_т_МенеджерОбменаЧерезУниверсальныйФормат"
related:
  - kafka-adapter.md
  - kafka-adapter-tests-unit.md
---

# kafka-adapter-examples Repository

## Summary

- This is a development-only add-on extension.
- EDT project name is `examples`; metadata name is `ТестированиеАдаптераKafka`.
- It demonstrates handlers, direct API, and Conversion Data-style scenarios.
- It supplies test catalogs, documents, and registers.
- It initializes broker/producer/consumer fixtures for development.
- Example behavior is illustrative, not a normative product contract.

## Responsibility

Provide executable usage examples and a controlled data model for manual and
automated adapter verification.

## Entry points

- `CommonModule.кфк_т_ТестовыеДанные` creates integration fixtures.
- `CommonModule.кфк_т_МенеджерОбменаЧерезУниверсальныйФормат` demonstrates a
  generated-style exchange manager and PОD/PКO rules.
- Test catalog/document/register objects drive outgoing and incoming examples.

## Compatibility note

The configuration reports platform compatibility `8.5.1` while its extension
compatibility is `8.3.21` and README badges say `8.3.21+`. Treat the supported
runtime range as requiring verification before changing CI or release baselines.

