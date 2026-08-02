---
title: Kafka Adapter Memory Bank
scope: kafka-adapter-ecosystem
type: index
status: partially-verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/project/repositories.md"
  - "repo:kafka-adapter:docs/overview/architecture.md"
related:
  - project-overview.md
  - repositories.md
  - agents/instructions.md
---

# Kafka Adapter Memory Bank

## Summary

- This is the compact project knowledge index for the Kafka Adapter ecosystem.
- Markdown under this directory is canonical and readable without MCP.
- Source code and tests outrank this Memory Bank when evidence conflicts.
- Begin with summaries; load full documents only for the affected area.
- Architecture centers on asynchronous queues between 1C and Apache Kafka.
- The main public API is `CommonModule.кфкИнтеграция`.
- SDD specifications define changes; ADRs capture architecture decisions.
- All repository paths are relative to `KAFKA_PROJECTS_ROOT`.

## Reading path

Use progressive disclosure:

```text
README.md
  -> project-overview.md
  -> repositories.md
  -> affected repository
  -> affected architecture/component document
  -> active specification
  -> related ADR
```

Do not load the entire Memory Bank by default.

## Start here

| Need | Read |
|---|---|
| Project purpose and boundaries | [Project overview](project-overview.md) |
| Repository ownership and paths | [Repository map](repositories.md) |
| System structure | [Architecture overview](architecture/overview.md) |
| Main subsystems | [Components](architecture/components.md) |
| Public BSL contract | [Public API](architecture/public-api.md) |
| Metadata and queue schema | [Metadata model](architecture/metadata-model.md) |
| Workers, status, and operations | [Background processing](architecture/background-processing.md) |
| Cross-system boundaries | [Integrations](architecture/integrations.md) |
| Message movement | [Data flows](architecture/data-flows.md) |
| Source navigation | [Navigation](development/navigation.md) |
| Main adapter change map | [Adapter deep navigation](development/adapter-navigation.md) |
| Test strategy | [Testing](development/testing.md) |
| Agent behavior and MCP routing | [Agent instructions](agents/instructions.md) |
| Terms and original identifiers | [Glossary](glossary.md) |

## Repository documents

| Repository | Responsibility document |
|---|---|
| `kafka-adapter` | [Main adapter](repositories/kafka-adapter.md) |
| `kafka-adapter-base` | [Base configuration](repositories/kafka-adapter-base.md) |
| `kafka-adapter-examples` | [Examples extension](repositories/kafka-adapter-examples.md) |
| `kafka-adapter-conv` | [Conversion Data extension](repositories/kafka-adapter-conv.md) |
| Conversion Data 3.1 | [Conversion Data base](repositories/conversion-data.md) |
| `kafka-adapter-tests-reports` | [Published reports](repositories/kafka-adapter-tests-reports.md) |
| `kafka-adapter-tests-ui` | [UI tests](repositories/kafka-adapter-tests-ui.md) |
| `kafka-adapter-tests-unit` | [Unit tests](repositories/kafka-adapter-tests-unit.md) |
| `kafka-tools` | [Development tools](repositories/kafka-tools.md) |

## Architecture

The primary runtime chain is:

```text
1C application
  -> adapter registration/API
  -> outgoing information-register queue
  -> serialization workers
  -> transport workers
  -> Simple Kafka Connector 1C
  -> Apache Kafka
```

The reverse chain is:

```text
Apache Kafka
  -> Simple Kafka Connector 1C
  -> loading workers
  -> incoming information-register queue
  -> deserialization/application workers
  -> 1C application
```

Evidence and operational qualifications are in
[Data flows](architecture/data-flows.md).

## Public entry points

Application code should normally call only:

- `repo:kafka-adapter:CommonModule.кфкИнтеграция`;
- `repo:kafka-adapter:CommonModule.кфкИнтеграцияКлиент`.

The server module exports queue registration, direct publish/read, session
closure, message/result constructors, and registration-event predicates.
Modules containing `Служебный` are internal implementation surfaces.

## Specifications

- [SDD index and lifecycle](specifications/README.md)
- [Specification template](specifications/template.md)
- [Demonstration specification](specifications/spec-0001-memory-bank-foundation.md)

Allowed lifecycle:

```text
draft -> approved -> in-progress -> implemented -> verified
   \-> rejected
any non-terminal -> superseded
```

An Issue is optional. The specification ID is the stable identity.

## Architecture decisions

- [ADR index](decisions/README.md)
- [ADR template](decisions/template.md)
- [ADR-0001: Markdown canonical storage](decisions/adr-0001-markdown-canonical-storage.md)

Create an ADR when a durable architecture choice affects multiple changes or
repositories. Do not use ADRs for routine implementation detail.

## Development workflow

1. Identify affected repositories and components.
2. Read their summaries and current source/tests.
3. Locate or create a specification when the change is non-trivial.
4. Record architecture choices in ADRs.
5. Implement only in repositories explicitly in scope.
6. Run focused tests and relevant integration checks.
7. Record implementation results and deviations.
8. Update affected Memory Bank documents.
9. Run the validator.

Details:

- [Conventions](development/conventions.md)
- [Change process](development/change-process.md)
- [Testing](development/testing.md)

## Evidence rules

Use evidence in this order:

1. Current local source and metadata.
2. Current automated tests.
3. Specialized MCP results verified against the checkout.
4. Local project documentation.
5. Published project documentation.
6. Repository README files.
7. Git history and Issues.
8. Existing Memory Bank content.

Record conflicts; do not silently choose the more convenient source.

## MCP routing

| Project | Allowed primary analysis interface |
|---|---|
| `adapter/adapter` | `kfk_edt`, Code Metadata Search, Graph Metadata Search |
| `adapter/base` | `kfk_edt` |
| `adapter/examples` | `kfk_edt` |
| `conversion/KFK` | `conv_edt` |
| `conversion/КД` | `conv_edt` |
| Markdown knowledge | Memory Bank MCP |

Code Metadata Search and Graph Metadata Search are restricted to
`adapter/adapter`. Do not route other projects through their indexes.

## Memory Bank MCP

The local stateless Streamable HTTP service supports:

- document listing, tree, metadata, summary, section, and line ranges;
- BM25-style ranked and exact search with bounded diagnostic output;
- repository/component/type/status filtering;
- ADR and specification retrieval;
- compact task-context bundles;
- revision-protected document, ADR, specification, and section writes;
- specification lifecycle/result/deviation updates;
- structural and link validation.

See the repository-level [MCP documentation](../docs/mcp.md).

## Maintenance

- [Update process](maintenance/update-process.md)
- [Pending verification](maintenance/pending-verification.md)

Current limitations:

- GitHub Issues were not required for the foundation specification.
- Published documentation was spot-compared for repository, architecture, and
  data-flow pages; no material content difference was observed on 2026-07-29.
- `KFK` has non-error EDT findings that require project-owner triage.
- Several version declarations differ between metadata and prose; see pending
  verification rather than assuming compatibility.

## Source-reference format

Files:

```text
repo:kafka-adapter:docs/overview/architecture.md
repo:kafka-tools:xdto/asyncapi2xsd.py
```

1C objects:

```text
repo:kafka-adapter:CommonModule.кфкИнтеграция
repo:kafka-adapter:DataProcessor.кфкИнтеграция
repo:kafka-adapter-conv:DataProcessor.кфкКонструкторAsyncAPI
```

Use the repository name from [Repository map](repositories.md). Never store an
absolute local path in canonical documentation.

## Editor use

The directory can be opened directly in VS Code or as an Obsidian vault.
Canonical links are ordinary relative Markdown links. Wiki links and personal
workspace state are not required or committed.
