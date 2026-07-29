---
title: kafka-adapter Repository
scope: kafka-adapter
repository: kafka-adapter
type: repository
status: verified
updated: 2026-07-29
components:
  - public-api
  - queues
  - background-processing
  - transport
sources:
  - "repo:kafka-adapter:README.md"
  - "repo:kafka-adapter:docs/overview/architecture.md"
  - "repo:kafka-adapter:src/Configuration/Configuration.mdo"
related:
  - ../architecture/overview.md
  - ../architecture/public-api.md
  - ../architecture/metadata-model.md
  - ../architecture/background-processing.md
  - ../development/navigation.md
  - ../development/adapter-navigation.md
---

# kafka-adapter Repository

## Summary

- This is the main product repository.
- It is an EDT extension project named `АдаптерKafka`.
- It contains product metadata/BSL, MkDocs, and release/quality configuration.
- Compatibility metadata is `8.3.21`; the extension purpose is customization.
- The embedded Simple Kafka Connector 1C compatibility baseline is `1.9.2+`.
- The `кфк` prefix identifies adapter-owned metadata.
- Two common modules form the documented application API.
- Current EDT inspection found no project problems.

## Responsibility

Own the reusable Kafka integration subsystem, its runtime configuration,
persistent queues, workers, connector facade, operational UI, public user
documentation, and product release sources.

## Navigation

| Area | Location or identifier |
|---|---|
| Configuration | `src/Configuration/Configuration.mdo` |
| Public server API | `CommonModule.кфкИнтеграция` |
| Public client API | `CommonModule.кфкИнтеграцияКлиент` |
| Worker orchestration | `CommonModule.кфкФоновыеОперацииСлужебный` |
| Transport facade | `DataProcessor.кфкИнтеграция` |
| Queues | `InformationRegister.кфкИсходящиеСообщения`, `кфкВходящиеСообщения` |
| Documentation | `docs/` |
| MkDocs config | `mkdocs.yml` |
| Static analysis | `.bsl-language-server.json`, `sonar-project.properties` |

## Primary API

Current EDT structure reports 14 exported methods in `кфкИнтеграция` and two in
`кфкИнтеграцияКлиент`. Use source comments for signatures and behavior. Do not
treat similarly named data-processor methods as the public application facade.

## Dependencies

- Host 1C configuration, normally with BSP infrastructure.
- Simple Kafka Connector 1C `1.9.2+` and its bundled librdkafka for transport.
- Apache Kafka at runtime.
- Optional custom application handlers or Conversion Data/XDTO artifacts.

## Risks

- The large orchestration module concentrates concurrency and status semantics.
- Extension and main-configuration delivery modes have different deployment constraints.
- Connector/platform/BSP compatibility is version-sensitive.

## Detailed model

Use the following adapter-specific documents before reading broad source:

- [Public API](../architecture/public-api.md) for supported method contracts;
- [Metadata model](../architecture/metadata-model.md) for configuration, queue,
  and service-state objects;
- [Background processing](../architecture/background-processing.md) for worker
  operations, status transitions, retry, cleanup, monitoring, and performance;
- [Adapter deep navigation](../development/adapter-navigation.md) for module,
  metadata, documentation, and test change routes.
