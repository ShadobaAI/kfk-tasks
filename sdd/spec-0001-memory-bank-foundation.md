---
title: Project Memory Bank and SDD Foundation
id: SPEC-0001
type: specification
status: verified
owner: kafka-adapter maintainers
created: 2026-07-29
updated: 2026-08-02
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
  - "repo:kfk-tasks:README.md"
  - "repo:kfk-tasks:docs/mcp.md"
  - "repo:kfk-tasks:src/memory_bank_mcp/store.py"
  - "repo:kfk-tasks:src/memory_bank_mcp/server.py"
related:
  - ../adr/adr-0001-markdown-canonical-storage.md
  - spec-0007-memory-bank-retirement.md
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

Use an in-process Markdown store with mtime/size cache. Expose MCP through the
official SDK Streamable HTTP transport. Validate content and expected revision
before atomic sibling-file replacement. Use PyYAML for front matter.

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

Use `unittest` for document operations, ranking regression, security cases,
validation, context bundles, and real Streamable HTTP client behavior.

## Risks

- Some architecture claims remain runtime-unverified.
- Version claims differ between metadata and prose.
- Lexical search is less flexible than semantic search.
- External editors that do not use the advisory MCP lock can still race with a
  write in the final revision-check window.

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

The documented Memory Bank, Streamable HTTP MCP server, validator,
configuration examples, editor guidance, and focused automated test suite are
implemented in `kfk-tasks`. The optional Windows symlink test is skipped where
symlink creation is not permitted. A real HTTP client completes MCP
initialization and a representative tool call.

## Deviations from Specification

The server uses the official Python MCP SDK 1.27.x Streamable HTTP
implementation. It remains stateless and bound to loopback by default.

## Memory Bank Updates

All architecture, repository, development, agent, decision, specification, and
maintenance documents in this foundation are new.

## Related Documents

- [ADR-0001](../adr/adr-0001-markdown-canonical-storage.md)
- [Memory Bank retirement](spec-0007-memory-bank-retirement.md)
