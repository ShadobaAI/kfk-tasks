---
title: Project Memory Bank and SDD Foundation
id: SPEC-0001
type: specification
status: verified
owner: kafka-adapter maintainers
created: 2026-07-29
updated: 2026-07-29
github_issue:
affected_repositories:
  - kfk-tasks
affected_components:
  - memory-bank
  - mcp
  - sdd
  - validation
related_adrs:
  - ADR-0001
tags:
  - specification
  - documentation
  - mcp
sources:
  - "repo:kfk-tasks:IMPLEMENTATION-PLAN.md"
related:
  - ../decisions/adr-0001-markdown-canonical-storage.md
  - ../README.md
---

# Project Memory Bank and SDD Foundation

## Summary

- Establish project-wide portable knowledge inside `kfk-tasks`.
- Add SDD and ADR lifecycle/templates.
- Provide a bounded local MCP interface over canonical Markdown.
- Secure all write paths and preserve existing files on validation failure.
- Validate structure, metadata, links, anchors, IDs, and portability.
- Cover critical read, write, security, and protocol behavior with tests.

## Context

The ecosystem spans product, base, examples, conversion, tests, reports, and
tooling repositories. Agents need compact verified navigation without loading
complete source trees or relying on one editor.

## Problem

Architecture and repository context was distributed across source, local
MkDocs, README files, and specialized analysis tools. There was no canonical SDD
workflow or bounded knowledge MCP.

## Goal

Create a local-first, Git-friendly, Windows-compatible Memory Bank and minimal
MCP server entirely inside `kfk-tasks`.

## Non-goals

- Business-logic changes.
- Web UI, database, vector index, cloud dependency, or BSL parser.
- Source-code mirroring or replacement of EDT/code/graph MCP services.
- Mandatory GitHub Issues or editor plugins.

## Scope

Documentation, repository/component maps, architecture/data flows, navigation,
agent instructions, SDD/ADR, MCP reads/writes/context, validation, configuration,
tests, and editor instructions.

## Functional Requirements

- Incremental and bounded document reading/search.
- Metadata filters and relationship discovery.
- ADR/specification create/retrieve/update operations.
- Compact task-context assembly.
- Safe create versus update semantics.
- Structural validator and machine-readable results.

## Non-functional Requirements

- UTF-8 Markdown remains canonical and human-editable.
- `KAFKA_PROJECTS_ROOT` resolves the workspace.
- Writes cannot escape `memory-bank/`.
- Runtime is dependency-light and operationally simple.
- No secrets or machine-specific paths are committed.

## Architecture and Design

Use an in-process Markdown store with mtime/size cache. Expose a stdio MCP
JSON-RPC boundary. Validate content before atomic sibling-file replacement.
Use PyYAML only for front matter.

## Implementation Plan

1. Inspect repositories, local/published docs, and MCP scopes.
2. Write the verified repository/architecture map.
3. Implement store, API, protocol server, validator, and configuration.
4. Add SDD/ADR templates and this demonstration specification.
5. Exercise tests, protocol calls, representative writes, and validation.

## Compatibility and Migrations

No existing canonical Memory Bank exists. The solution requires Python 3.10+
and PyYAML. Markdown remains usable without Python or MCP.

## Testing

Use standard-library `unittest` for document operations, security cases,
validation, context bundles, and MCP subprocess behavior.

## Risks

- Some architecture claims remain runtime-unverified.
- Version claims differ between metadata and prose.
- Lexical search is less flexible than semantic search.
- Manual concurrent writers are not coordinated by a distributed lock.

## Acceptance Criteria

- All implementation is inside `kfk-tasks`.
- Required repository and architecture documents exist with evidence.
- MCP supports required bounded reads and controlled writes.
- Traversal, absolute, UNC, overwrite, Cyrillic, and atomic-failure tests pass.
- Validator reports no structural errors in the committed Memory Bank.
- No hardcoded absolute workspace path is present.

## Open Questions

None blocking. Runtime Kafka behavior and broad Conversion Data compatibility
remain project-level verification work, not foundation blockers.

## Implementation Result

The documented Memory Bank, stdio MCP server, validator, configuration examples,
editor guidance, and focused automated test suite were implemented in
`kfk-tasks`. Twelve automated tests pass; the optional Windows symlink test is
skipped where symlink creation is not permitted. The validator reports 34
documents with zero errors and zero warnings. A real stdio process completed
initialization and representative bounded read, search, context, and validation
calls.

## Deviations from Specification

The MCP protocol boundary is implemented directly over stdio JSON-RPC to avoid a
runtime dependency on an MCP SDK. PyYAML is the only application dependency.

## Memory Bank Updates

All architecture, repository, development, agent, decision, specification, and
maintenance documents in this foundation are new.

## Related Documents

- [ADR-0001](../decisions/adr-0001-markdown-canonical-storage.md)
- [Memory Bank index](../README.md)
