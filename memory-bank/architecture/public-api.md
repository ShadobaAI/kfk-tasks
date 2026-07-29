---
title: Kafka Adapter Public API
scope: kafka-adapter
repository: kafka-adapter
type: architecture
status: verified
updated: 2026-07-29
components:
  - public-api
  - registration
  - direct-kafka-api
sources:
  - "repo:kafka-adapter:CommonModule.кфкИнтеграция"
  - "repo:kafka-adapter:CommonModule.кфкИнтеграцияКлиент"
  - "repo:kafka-adapter:docs/user/development/api.md"
  - "repo:kafka-adapter:docs/user/development/direct-api.md"
related:
  - overview.md
  - data-flows.md
  - ../development/adapter-navigation.md
---

# Kafka Adapter Public API

## Summary

- `кфкИнтеграция` is the server/external-connection/ordinary-application facade.
- `кфкИнтеграцияКлиент` owns supported client form navigation.
- Queue registration is the default reliable asynchronous path.
- Direct `Отправить`/`Прочитать` calls are synchronous and caller-managed.
- Reusable session maps improve batch throughput but require explicit closure.
- Message/result constructors define stable exchange structures.
- Registration-event predicates let handlers distinguish automatic, API, and forced work.
- Internal `*Служебный*` modules are not public contracts.

## Contract boundary

Only the two documented facade common modules should be called by application
code. EDT verified 14 exports in the server facade and two exports in the client
facade in the current checkout. Source comments and the local API page are the
signature authority.

## Registration API

| Method | Signature | Purpose |
|---|---|---|
| `Отключить` | `(Источник)` | Set `кфкПропуститьРегистрацию` before a write |
| `ПоместитьВОчередьИсходящих` | `(Источник, ТипОбъект = "", Продюсеры = Неопределено)` | Register source data or a ready message |
| `КлючОбъекта` | `(Данные)` | Calculate the business/object identity used by outgoing messages |
| `КлючЗаписиИсходящихСообщений` | `(Данные)` | Find queue record keys for source data |

### `Отключить`

Supported source families include reference objects and record sets for
information, accumulation, accounting, and calculation registers. Call it
before `Записать()` when an incoming handler must prevent a feedback loop.

The method inserts `кфкПропуститьРегистрацию = Истина` into
`ДополнительныеСвойства`. That flag is scoped to the object/record-set instance;
it is not a global integration lock.

### `ПоместитьВОчередьИсходящих`

`Источник` may be:

- a supported reference/object/record set;
- a structure or map used as an arbitrary payload;
- a structure returned by `ПараметрыСообщения`;
- an array for batch registration.

`ТипОбъект` is the routing key matched exactly against producer table
`ОбъектыМетаданных.ТипОбъект`. Use a metadata full name for automatic and
explicit registration of a metadata object. Use an arbitrary domain key only
with explicit API registration.

`Продюсеры` can constrain or bypass normal routing. This is a high-impact option:
callers assume responsibility for choosing compatible producer handlers/topics.

Batch input is processed in bounded portions by the implementation. It is
preferable to repeated single calls when registering a large controlled set.

## Registration-event predicates

| Method | True when `Свойства.СобытиеРегистрации` is |
|---|---|
| `ЭтоРегистрацияПриЗаписи(Свойства)` | automatic write subscription |
| `ЭтоРегистрацияПрограммно(Свойства)` | public API registration |
| `ЭтоРегистрацияПринудительно(Свойства)` | operator/forced registration |

Handlers use these methods instead of comparing enum values directly. This keeps
business code coupled to the public facade rather than enum implementation.

## Direct Kafka API

| Method | Signature | Result |
|---|---|---|
| `Отправить` | `(Продюсер, ИмяТопика, Сообщение, Партиция = -1, Сессии = Неопределено)` | integration result |
| `Прочитать` | `(Консьюмер, АвтоФиксацияСмещения, Сессии = Неопределено)` | integration result plus received message |
| `ЗакрытьСессииПродюсера` | `(Сессии)` | closes cached producer connections |
| `ЗакрытьСессииКонсьюмера` | `(Сессии)` | closes cached consumer connections |

The direct path does not provide queue dispatch, queue retry, or parallel worker
management. Caller code must observe `Успешно`, handle `ТекстОшибки`, decide
retry/transaction semantics, and close explicitly reused sessions.

### Session behavior

- `Неопределено`: create and close a connection for the call; simple but costly
  for volume.
- `Соответствие`: reuse connector objects between calls; efficient for a batch,
  but requires the matching closure method in a guaranteed cleanup path.

Do not share an undocumented session map between incompatible producers or
consumers. Its keys and values are implementation detail.

### Partition behavior

The public documentation specifies `-1` as automatic partition selection. When
source comments or call sites differ, confirm the current source and add a
regression test before changing defaults.

## Constructors

### `ПараметрыСообщения(Данные = "", Ключ = "")`

Returns a structure with:

| Field | Type/purpose |
|---|---|
| `Данные` | string, binary data, structure, or array of structures |
| `Ключ` | stable Kafka message key |
| `Заголовки` | map of header name to string value |

`Отправить` and queue registration may augment a structure with operation
result fields. Keep message creation through this constructor so new fields can
be added compatibly.

### `РезультатИнтеграции()`

Returns:

| Field | Meaning |
|---|---|
| `Успешно` | aggregate operation success |
| `ТекстОшибки` | operation-level error text |

`Прочитать` additionally exposes `Сообщение` with body, key, headers, topic,
timestamp, partition, and offset when a message is available.

## Client API

`кфкИнтеграцияКлиент.ИсторияВыгрузкиОбъекта` opens outgoing history for a
reference/object/register key and accepts optional owner form/window/open mode.
`ВыполнитьПодключаемуюКоманду` is the connected-command integration callback.

## Safe usage patterns

### Reliable outgoing integration

1. Build or identify source data.
2. Call `ПоместитьВОчередьИсходящих`.
3. Observe the outgoing register and worker statuses.
4. Let dispatcher retry transport errors according to policy.

### Incoming business write

1. Validate and identify the incoming event.
2. Load or create the target object.
3. Call `Отключить(target)` before write.
4. Set the standard exchange-loading flag where application logic requires it.
5. Write idempotently.

### Direct batch publish

1. Create one `Соответствие` session map.
2. Build each message through `ПараметрыСообщения`.
3. Call `Отправить`, check every result, and decide retry.
4. Close in guaranteed cleanup through `ЗакрытьСессииПродюсера`.

## Compatibility rule

Any method rename, parameter/default change, result-field change, accepted type
change, routing-key semantic change, or session lifecycle change is a public API
change. It requires SDD, compatibility analysis, docs, and focused tests.

