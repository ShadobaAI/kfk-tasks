---
title: Kafka Adapter Metadata Model
scope: kafka-adapter
repository: kafka-adapter
type: architecture
status: verified
updated: 2026-07-29
components:
  - configuration
  - queues
  - operational-state
sources:
  - "repo:kafka-adapter:docs/project/metadata.md"
  - "repo:kafka-adapter:Catalog.кфкБрокеры"
  - "repo:kafka-adapter:Catalog.кфкПродюсеры"
  - "repo:kafka-adapter:Catalog.кфкКонсьюмеры"
  - "repo:kafka-adapter:InformationRegister.кфкИсходящиеСообщения"
  - "repo:kafka-adapter:InformationRegister.кфкВходящиеСообщения"
related:
  - components.md
  - background-processing.md
  - data-flows.md
---

# Kafka Adapter Metadata Model

## Summary

- The extension currently exposes 39 top-level objects through EDT.
- One subsystem, `кфкИнтеграция`, groups 64 content entries.
- Brokers define nodes and connector-level properties.
- Producers define outgoing routing, transformation, blocking, and parallelism.
- Consumers define group/topic routing, transformation, blocking, and parallelism.
- Outgoing and incoming registers persist payload, status, timing, attempts, and diagnostics.
- Service registers persist worker coordination, operation pointers, settings, and hashes.
- Enums, constants, roles, functional options, subscriptions, and one scheduled job complete the model.

## Configuration hierarchy

```text
кфкБрокеры
  <- кфкПродюсеры (hierarchical; folders act as task dispatchers)
  <- кфкКонсьюмеры (hierarchical; parents act as task dispatchers)
```

The producer catalog uses folders as orchestrators. Both producer and consumer
parents hold worker parallelism; leaf items hold broker/handler/topic settings.

## Broker catalog

`Catalog.кфкБрокеры`:

- blocking flags: `БлокироватьПубликацию`, `БлокироватьЧтение`;
- `Узлы`: enabled flag plus `host:port` address;
- `ПараметрыПодключения`: connector key/value plus password-display mode;
- list and item managed forms.

Connector parameters are intentionally open-ended key/value data. Validate keys
against the connector/librdkafka version used by the deployment.

## Producer catalog

Leaf attributes:

| Attribute | Role |
|---|---|
| `Брокер` | Transport configuration |
| `РежимАсинх` | Connector send mode |
| `БлокироватьРегистрацию` | Stop new outgoing registration |
| `БлокироватьСериализацию` | Stop transformation stage |
| `БлокироватьПубликацию` | Stop Kafka send stage |
| `ИдемпотентнаяОтправка` | Skip unchanged message bodies |
| `ПодпотокиОбработки` | Serialization parallelism |
| `ПодпотокиТранспорта` | Send parallelism |

`ОбъектыМетаданных` rows:

| Field | Role |
|---|---|
| `ТипОбъект` | Exact registration/routing key |
| `ИмяТопика` | Kafka target topic |
| `ТипСериализации` | Custom handler or Conversion Data |
| `ИмяМетодаСериализации` | Custom exported method |
| `ИмяМодуляСериализации` | Custom common module |
| `ИмяПОДСериализации` | Conversion Data processing rule |
| `ФорматСериализации` | XDTO namespace URL |

`ПараметрыПродюсера` holds connector key/value overrides.

## Consumer catalog

Leaf attributes:

| Attribute | Role |
|---|---|
| `Брокер` | Transport configuration |
| `Идентификатор` | Kafka consumer group id |
| `ТаймаутОжидания` | Poll wait in milliseconds |
| `ДвоичныеДанные` | Preserve payload as binary |
| `БлокироватьЧтение` | Stop Kafka loading |
| `БлокироватьДесериализацию` | Stop application processing |
| `ИдемпотентнаяОбработка` | Skip unchanged bodies |
| `ПодпотокиОбработки` | Deserialization parallelism |
| `ПодпотокиТранспорта` | Kafka read parallelism |

`Топики` rows define topic plus custom/KD handler name, module/POD, and XDTO
format. `ПараметрыКонсьюмера` holds connector key/value overrides.

Consumer group identity changes delivery distribution. Multiple consumers with
the same group receive disjoint records, not copies.

## Outgoing queue

`InformationRegister.кфкИсходящиеСообщения` is keyed by:

- `КлючЗаписи`;
- `ДатаРегистрацииМС`.

Core state:

| Kind | Fields |
|---|---|
| Routing | `Продюсер`, `ТипОбъект`, `ТипИсходныхДанных`, `КлючОбъекта` |
| Event | `СобытиеРегистрации`, `ЭтоУдаление` |
| Payload | `ИсходныеДанные`, `КлючСообщения`, `Заголовки`, `ТелоСообщения` |
| Lifecycle | `Статус`, registration/processing/send dates |
| Diagnostics | duration, journal text, processing/send counts |
| Ordering | millisecond registration/change markers |

The queue can hold source data before serialization and final transport body
after serialization. Any schema change affects registration, worker queries,
forms, cleanup, external logging, and test/report interpretation.

## Incoming queue

`InformationRegister.кфкВходящиеСообщения` is keyed by:

- `КлючЗаписи`;
- `ДатаЗагрузкиМС`.

Core state:

| Kind | Fields |
|---|---|
| Routing | `Консьюмер`, `Топик`, `Раздел`, `Смещение` |
| Payload | `КлючСообщения`, `Заголовки`, `ТелоСообщения` |
| Lifecycle | `Статус`, write/load/process dates |
| Diagnostics | duration, journal text, processing count |
| Ordering | millisecond load/change markers |

It is subordinate to a recorder in metadata and keeps Kafka partition/offset
for diagnosis and handler context.

## Service-state registers

| Register | Key state | Purpose |
|---|---|---|
| `кфкОчередьПотоков` | operation key, timestamp, worker UUID | Active/queued worker coordination |
| `кфкПозицииОпераций` | operation UUID and partition | Selection/progress pointer |
| `кфкХэшСуммыСообщений` | queue key -> SHA-256/date/change marker | Idempotency history |
| `кфкПараметрыКонтроляИнтеграции` | thresholds/settings | SLA/error control |
| `кфкПараметрыЛогирования` | logging settings | External log export |
| `кфкПараметрыОчисткиХранилища` | retention settings | Queue/hash cleanup |

## Status and event enums

`кфкСтатусыСообщений` includes new, processed, cancelled, processing error,
sent, send error, and send cancelled states. `ОбработкаОтменена` covers handler
rejection, duplicate outgoing work, and idempotent incoming cancellation; use
journal text/context to distinguish reasons.

`кфкСобытияРегистрации` distinguishes automatic write, programmatic, and forced
registration. `кфкТипыОбработчиков` selects custom versus Conversion Data.

## Controls and security

Constants/functional options enable the subsystem, global blocking, integration
control, stream mode, and component logging details. Roles:

- `кфкБазовыеПрава`: read/observe;
- `кфкПолныеПрава`: administer and modify.

`DefinedType.кфкПользователь` must be adapted to the host user catalog during
embedding. The adopted `Catalog.Пользователи` is development/link-integrity
support and is removed from the final build according to local docs.

## Event entry points

Four subscriptions cover reference writes, register-set writes, calculation
register-set writes, and reference deletion. Producer routing decides whether a
specific event becomes queue work; metadata objects are not manually added to a
subscription for each producer.

## Change-impact checklist

For any metadata change inspect:

1. forms and rights;
2. worker query text and indexes;
3. serialization/external logging;
4. cleanup and retention;
5. configuration import/update handling;
6. docs and examples;
7. YAxUnit/UI scenarios;
8. extension/main-configuration delivery compatibility.

