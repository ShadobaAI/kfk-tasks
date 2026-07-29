---
title: Project Navigation
scope: kafka-adapter-ecosystem
type: development
status: verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/project/repositories.md"
  - "repo:kafka-adapter:docs/project/modules.md"
  - "repo:kafka-adapter:docs/project/metadata.md"
related:
  - ../repositories.md
  - testing.md
---

# Project Navigation

## Summary

- Resolve the workspace from `KAFKA_PROJECTS_ROOT`.
- Start product behavior in `adapter/adapter/src` and local `docs`.
- Use 1C FQNs for architecture-significant metadata.
- Route main/base/examples to `kfk_edt`.
- Route KFK/Conversion Data to `conv_edt`.
- Use indexed code/graph services only for the main adapter.
- Ignore generated EDT workspace and report artifacts unless the task needs them.

## From a symptom to source

| Symptom or change | First location |
|---|---|
| Public API | `CommonModule.кфкИнтеграция` |
| Object-write registration | `CommonModule.кфкОбработкаСобытийСлужебный` |
| Producer/consumer filtering | producer/consumer catalogs and service modules |
| Serialization/send/load/deserialization | `CommonModule.кфкФоновыеОперацииСлужебный` |
| Connector/session behavior | `DataProcessor.кфкИнтеграция` |
| Queue schema/status | outgoing/incoming information registers and status enum |
| Operator UI | `DataProcessor.кфкПанельАдминистрирования` |
| Example contract | `adapter/examples` after checking product contract |
| KD/AsyncAPI authoring | `conversion/KFK` with adopted object checks in `conversion/КД` |
| Unit behavior | `tests/unit/unit/src/CommonModules/ОМ_ЮТест` |
| Managed UI | `tests/ui/features` |
| Local Kafka/logging | `tools/` |

## Source-reference convention

Use:

```text
repo:<repository>:<relative-path>
repo:<repository>:<1C-Type>.<Object>
```

Examples:

```text
repo:kafka-adapter:CommonModule.кфкИнтеграция
repo:kafka-adapter:src/CommonModules/кфкИнтеграция/Module.bsl
repo:kafka-adapter-conv:Catalog.ПравилаКонвертацииОбъектов
```

Prefer FQNs in architecture prose and paths when a developer must open the
exact file.

## Generated/local material

Do not use these as canonical source without a specific need:

- EDT `.metadata` workspaces;
- `tests/unit/base` assembled host;
- generated HTML under test reports;
- runtime logs, database data, or container volumes.

## Narrow-reading rule

List metadata/modules or retrieve module structure before reading a full BSL
module. `кфкФоновыеОперацииСлужебный` is more than 5,000 lines; read the method
or region relevant to the task.

