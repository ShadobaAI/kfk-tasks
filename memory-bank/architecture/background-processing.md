---
title: Background Processing and Operations
scope: kafka-adapter
repository: kafka-adapter
type: architecture
status: verified
updated: 2026-07-29
components:
  - background-processing
  - statuses
  - retry
  - observability
  - maintenance
sources:
  - "repo:kafka-adapter:CommonModule.кфкФоновыеОперацииСлужебный"
  - "repo:kafka-adapter:docs/user/configuration/jobs.md"
  - "repo:kafka-adapter:docs/user/operations/statuses.md"
  - "repo:kafka-adapter:docs/user/operations/monitoring.md"
  - "repo:kafka-adapter:docs/user/operations/queue-maintenance.md"
related:
  - data-flows.md
  - metadata-model.md
  - ../development/adapter-navigation.md
---

# Background Processing and Operations

## Summary

- One scheduled job starts dispatch across exchange and service operations.
- Separate operations serialize, send, load, deserialize, de-duplicate, retry, clean, log, and control.
- Producer/consumer dispatcher nodes define processing and transport parallelism.
- Stream mode keeps work active between scheduled-job intervals.
- Queue and service registers preserve progress across interruptions.
- Only send errors receive the documented limited automatic retry.
- Monitoring combines queue forms, job forms, event log, component logs, and external logging.
- Queue deletion requires exchange suspension and appropriate rights.

## Orchestration module

`CommonModule.кфкФоновыеОперацииСлужебный` contains 5,288 lines in the inspected
checkout, with 48 procedures and 83 functions. Its verified regions include:

- task/background-job management;
- parallel stream allocation and pointers;
- outgoing serialization;
- Kafka send;
- Kafka load;
- incoming deserialization;
- duplicate removal and queue return;
- queue/service cleanup;
- external logging;
- integration control.

Use method/region reads; do not load this module in full for routine tasks.

## Exported dispatcher operations

Important exported entry points include:

| Operation | Responsibility |
|---|---|
| `ЗапуститьРегламентноеЗадание` | Scheduled entry point |
| `ПолучитьПотоки`, `ЗапуститьПотоки` | Resolve and start bounded operations |
| `СериализацияСообщений` | Dispatch outgoing transformation |
| `ОтправкаСообщенийВKafka` | Dispatch outgoing transport |
| `ЗагрузкаСообщенийИзKafka` | Dispatch incoming transport |
| `ДесериализацияСообщений` | Dispatch application processing |
| `УдалениеДублейОчереди` | Mark obsolete unsent versions |
| `ВозвратВОчередь` | Move eligible records back to new work |
| `КонтрольИнтеграции` | Evaluate operational thresholds/alerts |
| cleanup exports | Remove expired queue/service/hash state |
| log exports | Send outgoing/incoming history to external logging |

Several exported methods are internal callbacks for background jobs, not public
application contracts.

## Parallelism model

Producer dispatcher:

- processing streams -> serialization;
- transport streams -> Kafka publication.

Consumer dispatcher:

- transport streams -> Kafka polling/loading;
- processing streams -> deserialization/application handler.

Worker allocation uses `кфкОчередьПотоков`; selection/progress uses
`кфкПозицииОпераций`. The module maintains partitions, selection pointers,
timeouts, minimum portions, and worker completion. Configuration changes affect
future dispatch; running work finishes according to current operation behavior.

## Blocking controls

| Level | Controls |
|---|---|
| Global | integration use/block constants and functional options |
| Broker | publication/read blocks |
| Producer | registration/serialization/publication blocks |
| Consumer | read/deserialization blocks |
| Job UI | block/unblock all streams after current portion |

Choose the narrowest operational block that isolates the incident. Global
blocking changes more flows and should be observable to operators.

## Outgoing status path

Typical path:

```text
Новое
  -> Обработано
  -> Выгружено
```

Branches:

- serialization exception -> `ОшибкаОбработки`;
- send exception/no confirmation -> `ОшибкаВыгрузки`;
- unchanged body with idempotent send -> `ВыгрузкаОтменена`;
- obsolete unsent version/handler refusal -> `ОбработкаОтменена`.

The implementation stores processing/send counts, dates, duration, and journal
text. Status alone may not explain cancellation; inspect journal text.

## Incoming status path

Typical path:

```text
Новое
  -> Обработано
```

Branches:

- deserialization/application exception -> `ОшибкаОбработки`;
- handler refusal or unchanged idempotent body -> `ОбработкаОтменена`.

Incoming loading persists topic, partition, offset, Kafka timestamp, load time,
key, headers, and body before application processing.

## Retry semantics

- `ОшибкаВыгрузки`: automatic retry is documented up to three attempts, spaced
  by the scheduled job interval.
- `ОшибкаОбработки`: no automatic retry; fix the handler/data issue and return
  the record manually.
- Direct API: no queue-managed automatic retry.
- `Прочитать` offset behavior depends on the caller's auto-commit choice and
  connector/session configuration.

Do not generalize these policies into exactly-once guarantees.

## Duplicate and idempotency controls

Duplicate removal chooses the newest relevant outgoing version and marks older
unsent versions as cancelled/duplicate.

Idempotency uses `кфкХэшСуммыСообщений`:

- outgoing unchanged body -> skip Kafka send;
- incoming unchanged body -> skip application handler.

The hash is body-based and keyed by queue identity. It does not prove business
transaction idempotency across different keys or side effects.

## Cleanup

Retention settings govern outgoing, incoming, service, and hash history.
Documented special values include:

- `-1`: retain indefinitely;
- `-2`: delete after successful external-log export.

Manual commands delete selected, filtered, or all records. Stop relevant
exchange operations first; deletion while workers select/update records risks
inconsistent operator expectations and lost diagnostics.

## Observability

| Surface | Best use |
|---|---|
| Queue list/record forms | Per-message status, payload context, journal, retry |
| Background jobs form | Worker state and task failures |
| Scheduled job form | Dispatcher schedule/user/execution |
| 1C event log | Registration exceptions and system context |
| Connector logs | librdkafka/network/TLS/session failures |
| External ELK/Loki-style logs | Trends, dashboards, long-term analysis |
| Integration control/Telegram | Threshold alerts |

Daily checks should focus on queue growth, error statuses, stuck workers, and
scheduled-job health. Weekly checks include retention, connector logs, and
capacity trends.

## Performance levers

- increase processing streams for CPU-bound transformation backlog;
- increase transport streams for broker/network-latency backlog;
- enable stream mode for sustained traffic;
- batch registration/publication when the contract supports it;
- split topics/dispatchers with distinct throughput characteristics;
- add recommended DB indexes where deployment mode/licensing requires manual work.

Measure queue wait, processing duration, send/load latency, throughput, server
CPU, DB query plans/locks, and broker metrics before tuning. Higher parallelism
can increase DB contention and connector/broker pressure.

## Operational change checklist

For worker/status/query changes:

1. inspect query selection, progress pointers, and indexes;
2. define crash/restart behavior;
3. define status/journal/attempt updates on every branch;
4. test block/unblock and manual return;
5. test empty queue, partial batch, duplicate, and error cases;
6. verify cleanup does not race active work;
7. update monitoring and operator documentation.

