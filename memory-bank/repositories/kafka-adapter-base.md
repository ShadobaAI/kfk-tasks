---
title: kafka-adapter-base Repository
scope: kafka-adapter-base
repository: kafka-adapter-base
type: repository
status: verified
updated: 2026-07-29
components:
  - development-host
  - bsp
sources:
  - "repo:kafka-adapter-base:README.md"
  - "repo:kafka-adapter-base:src/Configuration/Configuration.mdo"
  - "repo:kafka-adapter-base:CommonModule.ОбновлениеИнформационнойБазыKafka"
related:
  - kafka-adapter.md
  - kafka-adapter-examples.md
---

# kafka-adapter-base Repository

## Summary

- This is the BSP-based 1C host for adapter development and tests.
- EDT project name is `base`; configuration name is `BaseKafka`.
- Compatibility metadata is `8.3.21`.
- It is not the Kafka product implementation.
- It supplies infrastructure and an infobase target for the adapter extension.
- Current EDT inspection found no project problems.

## Responsibility

Provide a reproducible host configuration for development, debugging, manual
scenarios, and test assembly without requiring a business production
configuration.

## Significant entry point

`CommonModule.ОбновлениеИнформационнойБазыKafka` registers `BaseKafka` with the
BSP update framework and declares `СтандартныеПодсистемы` as required.

## Relationship

The adapter extension is attached to this host in the development workspace.
The examples extension also runs against the resulting environment. Base
configuration objects are dependencies, not product-owned APIs unless
explicitly documented.

## Limitations

The repository contains a broad BSP-derived surface. Do not document or analyze
all 561 BSL modules for adapter work. Read only the host objects required by the
change.

