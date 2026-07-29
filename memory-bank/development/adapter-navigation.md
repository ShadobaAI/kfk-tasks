---
title: Main Adapter Deep Navigation
scope: kafka-adapter
repository: kafka-adapter
type: development
status: verified
updated: 2026-07-29
components:
  - navigation
  - change-impact
sources:
  - "repo:kafka-adapter:docs/project/modules.md"
  - "repo:kafka-adapter:docs/project/metadata.md"
  - "repo:kafka-adapter:src"
related:
  - ../repositories/kafka-adapter.md
  - ../architecture/public-api.md
  - ../architecture/metadata-model.md
  - ../architecture/background-processing.md
---

# Main Adapter Deep Navigation

## Summary

- Start from public facade or persisted state, then follow into service modules.
- Use EDT object/module lists and method structure before source reads.
- Code/metadata and graph indexes are valid only for this repository.
- Configuration catalogs define routing and worker behavior.
- Queue/service registers reveal lifecycle and concurrency semantics.
- Examples/tests validate intended use but do not override product contracts.
- Docs under `adapter/adapter/docs` are the source of the published site and currently equal it.

## Repository layout

| Path | Purpose |
|---|---|
| `src/` | EDT metadata and BSL |
| `docs/overview/` | System purpose, architecture, flows, principles |
| `docs/project/` | Repositories, modules, metadata, build/environment |
| `docs/user/configuration/` | Broker/producer/consumer/jobs/logging/alerts |
| `docs/user/development/` | Public API and handler contracts |
| `docs/user/operations/` | Status, monitoring, diagnosis, maintenance, tuning |
| `docs/user/examples/` | Scenario-level usage |
| `.github/` | CI/release/docs workflows |
| `.bsl-language-server.json` | BSL static-analysis settings |
| `sonar-project.properties` | Sonar analysis |

## Module route map

| Concern | Start | Continue |
|---|---|---|
| Public registration/direct API | `кфкИнтеграция` | service module or data processor called by method |
| Client history command | `кфкИнтеграцияКлиент` | client/server service modules and queue form |
| Automatic event registration | `кфкОбработкаСобытийСлужебный` | producer filters and outgoing register |
| Core orchestration | `кфкФоновыеОперацииСлужебный` | relevant method region only |
| Transport/session | `DataProcessor.кфкИнтеграция.ObjectModule` | connector calls and broker/producer/consumer parameters |
| XDTO transform | `кфкОбменДаннымиXDTOСервер` | host exchange-manager module |
| Cached settings | `кфкИнтеграцияСлужебныйПовтИсп` | catalogs/constants/registers |
| Server-call facade | `кфкИнтеграцияСлужебныйВызовСервера` | target service routine |
| Administration | `кфкПанельАдминистрирования` | specific form/command and service call |
| Forced registration | `кфкРегистрацияИзменений` | public registration/service routine |

## Metadata route map

| Question | Objects |
|---|---|
| Why was an object registered/routed? | producer `ОбъектыМетаданных`, event enum, outgoing record |
| Why was it not registered? | functional/global/producer block, routing key, skip flags |
| Why did serialization fail? | outgoing source/payload/journal, handler fields, worker method |
| Why did send fail? | producer/broker parameters, outgoing attempts/journal, connector log |
| Why was send skipped? | producer idempotency, hash register, duplicate status/journal |
| Why was incoming not read? | broker/consumer blocks, group/topic, timeout, load worker |
| Why was incoming not applied? | incoming status/journal, handler fields, idempotency hash |
| Why are workers idle/stuck? | scheduled job, queue streams, operation positions, blocks |

## Public API change route

1. Read `CommonModules/кфкИнтеграция/Module.bsl` method structure/comments.
2. Read `docs/user/development/api.md` and `direct-api.md`.
3. Search exact method references with EDT/code index.
4. Check examples and YAxUnit call sites.
5. Trace service/data-processor calls and metadata fields.
6. Define backward compatibility and update SDD/ADR if needed.

## Queue/status change route

1. Inspect queue register metadata and status enum.
2. Search every read/write of the changed field/status.
3. Inspect all relevant worker regions and manual UI commands.
4. Inspect cleanup, external logging, monitoring queries, and report interpretation.
5. Check indexes and selection ordering.
6. Add crash/retry/duplicate/idempotency tests.
7. Update operator and data-flow docs.

## Producer/consumer configuration change route

1. Inspect catalog metadata, hierarchy, forms, and manager/object modules.
2. Inspect cached setting construction in `кфкИнтеграцияСлужебныйПовтИсп`.
3. Inspect worker distribution and connector parameter transfer.
4. Verify defaults, validation, password presentation, and upgrade behavior.
5. Update configuration docs and example initialization.

## Event-subscription change route

1. Identify the subscription object and exact source types/event.
2. Inspect handler in `кфкОбработкаСобытийСлужебный`.
3. Verify skip/exchange-loading behavior and exception containment.
4. Check producer routing for reference and register/recorder cases.
5. Test automatic, programmatic, forced, delete, and batch registration.

## Background-operation change route

1. Identify exported dispatcher/worker method.
2. Read its service region and selection query.
3. Follow operation IDs, partitioning, pointer update, and stream queue logic.
4. Map success/error/cancellation state mutations.
5. Check block controls, retries, cleanup, logging, and control thresholds.
6. Test restart and partial-batch behavior.

## Transport change route

1. Start in `DataProcessor.кфкИнтеграция.ObjectModule`.
2. Identify connector method and broker/producer/consumer parameter construction.
3. Verify direct API and worker call sites.
4. Check reusable session lifecycle and Kafka transaction methods.
5. Verify connector/platform/Kafka compatibility from current release evidence.
6. Exercise a real cluster; syntax/static checks are insufficient.

## Documentation route

The published site is generated from local `docs` and currently matches it.
Edit local Markdown only. Main canonical pages:

- architecture: `docs/overview/architecture.md`, `data-flow.md`, `principles.md`;
- API: `docs/user/development/api.md`, `direct-api.md`;
- handlers: `producer-handler.md`, `consumer-handler.md`, `conversion-data.md`;
- configuration: brokers/producers/consumers/jobs;
- operations: statuses/monitoring/diagnostics/queue-maintenance/performance;
- project: modules/metadata/environment/delivery formats/repositories.

## MCP use for the main adapter

Recommended sequence:

1. `kfk_edt` object/module list or details.
2. Code Metadata Search exact/bounded search for identifiers.
3. Graph Metadata Search depth 1 direct relationships for impact.
4. Verify graph/index findings with EDT metadata or source.
5. Read only the relevant method/line range.

Code/graph indexes contain only `adapter/adapter` in this workflow. Do not use
their results to claim behavior of base, examples, or conversion projects.

## Verified high-impact relationships

- `DataProcessor.кфкИнтеграция` holds producer/consumer references.
- Code dependency search found its use by integration service/cache/worker modules.
- Metadata graph found producer and consumer catalog relationships.
- Source and EDT metadata confirm these direct relationships.

## Common pitfalls

- Confusing `CommonModule.кфкИнтеграция` with `DataProcessor.кфкИнтеграция`.
- Treating example modules as the public contract.
- Reading the entire orchestration module instead of one region.
- Changing a status without updating manual return, cleanup, logging, and UI.
- Treating body-hash idempotency as business exactly-once.
- Increasing parallelism without checking DB contention and Kafka capacity.
- Assuming extension metadata alone proves all supported platform/host versions.

