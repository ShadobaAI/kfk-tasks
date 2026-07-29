---
title: Kafka Adapter Data Flows
scope: kafka-adapter
type: architecture
status: verified
updated: 2026-07-29
components:
  - outgoing-flow
  - incoming-flow
  - background-processing
sources:
  - "repo:kafka-adapter:docs/overview/data-flow.md"
  - "repo:kafka-adapter:CommonModule.кфкФоновыеОперацииСлужебный"
related:
  - overview.md
  - components.md
---

# Kafka Adapter Data Flows

## Summary

- Outgoing flow is registration, serialization, transport, plus duplicate control.
- Incoming flow is transport loading followed by deserialization/application processing.
- Each stage persists state in 1C information registers.
- Dispatchers split work into bounded background streams.
- Hash checks support idempotent send and processing.
- Transport errors and application errors have different retry behavior.

## Outgoing

```text
object/record-set write or direct API
  -> producer filter
  -> кфкИсходящиеСообщения
  -> serialization worker
  -> optional idempotency/duplicate decision
  -> send worker
  -> DataProcessor.кфкИнтеграция
  -> Simple Kafka Connector 1C
  -> Kafka topic
```

Automatic registration errors are logged and are designed not to abort the
originating application write. Direct registration may provide either source
data for serialization or a ready message body.

Serialization invokes a custom handler or the Conversion Data/XDTO route. For
registers subordinate to a recorder, the recorder is the registration unit;
the Conversion Data route can produce one array-bearing message for its records.

Transport failures are documented with up to three automatic attempts at the
scheduled-job interval. After exhaustion, operator intervention is required.

## Incoming

```text
Kafka topic
  -> Simple Kafka Connector 1C
  -> loading worker
  -> кфкВходящиеСообщения
  -> optional idempotency decision
  -> custom handler or Conversion Data/XDTO
  -> host application write
  -> final queue status
```

Application processing errors do not receive the same automatic retry policy as
transport sends. Operators return corrected messages to the queue explicitly.

## State and concurrency

`кфкОчередьПотоков` and `кфкПозицииОпераций` coordinate workers and selection
pointers. Configuration determines maximum parallelism; idle workers terminate.
Do not assume exactly-once delivery. Build handlers around stable keys,
idempotent effects, and observable status transitions.

## Failure boundaries

| Failure | Persisted evidence | Recovery owner |
|---|---|---|
| Registration exception | 1C event log | Adapter developer/operator |
| Serialization/deserialization error | Queue status and journal text | Handler owner |
| Kafka send error | Outgoing status and attempt count | Automatic then operator |
| Duplicate/idempotent payload | Cancelled/duplicate status | Expected adapter behavior |
| Worker interruption | Queue and progress state | Dispatcher/operator |

