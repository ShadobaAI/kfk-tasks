---
title: Kafka Adapter Components
scope: kafka-adapter
type: architecture
status: verified
updated: 2026-07-29
components:
  - public-api
  - configuration
  - queues
  - background-processing
  - transport
  - administration
sources:
  - "repo:kafka-adapter:docs/project/metadata.md"
  - "repo:kafka-adapter:docs/project/modules.md"
  - "repo:kafka-adapter:CommonModule.кфкФоновыеОперацииСлужебный"
related:
  - overview.md
  - data-flows.md
---

# Kafka Adapter Components

## Summary

- Three catalogs configure brokers, producers, and consumers.
- Two registers are message queues; service registers hold execution state.
- Public, registration, transformation, orchestration, and transport modules are separated.
- One scheduled job enters the dispatcher.
- Four event subscriptions cover writes/deletes for supported object classes.
- Administration and forced-registration processors provide operator workflows.

## Component map

| Component | Key identifiers | Notes |
|---|---|---|
| Broker configuration | `Catalog.кфкБрокеры` | Connection and connector properties |
| Producers | `Catalog.кфкПродюсеры` | Outgoing filters, topics, handlers, parallelism |
| Consumers | `Catalog.кфкКонсьюмеры` | Topics, groups, handlers, parallelism |
| Outgoing queue | `InformationRegister.кфкИсходящиеСообщения` | Registration, serialization, send status |
| Incoming queue | `InformationRegister.кфкВходящиеСообщения` | Loaded payload and application status |
| Worker coordination | `кфкОчередьПотоков`, `кфкПозицииОпераций` | Parallel work and progress pointers |
| Idempotency | `кфкХэшСуммыСообщений` | SHA-256 body history |
| Dispatcher | `ScheduledJob.кфкЗапускИнтеграции` | Starts processing operations |
| Worker logic | `CommonModule.кфкФоновыеОперацииСлужебный` | 5,288-line orchestration module in current checkout |
| Connector facade | `DataProcessor.кфкИнтеграция` | External component lifecycle and direct API |
| Administration | `DataProcessor.кфкПанельАдминистрирования` | Queue/configuration/diagnostic UI |

## Worker operations

EDT module structure verifies regions and exported entry points for:

- serialization;
- sending to Kafka;
- loading from Kafka;
- deserialization;
- duplicate removal;
- queue return;
- cleanup;
- external logging;
- integration control.

This document intentionally does not inventory all internal routines. Use EDT
module structure or source for a change-specific call path.

## Configuration extension points

Transformation can use:

- an exported method in an application common module;
- a generated Conversion Data 3.1 exchange manager and XDTO package.

Example code is evidence of intended use, not the normative contract. Confirm
the contract in the public API module and current user development docs.

