---
title: Use Markdown as Canonical Memory Bank Storage
id: ADR-0001
type: decision
status: accepted
created: 2026-07-29
updated: 2026-07-29
related_specifications:
  - SPEC-0001
affected_repositories:
  - kfk-tasks
sources:
  - "repo:kfk-tasks:IMPLEMENTATION-PLAN.md"
related:
  - ../specifications/spec-0001-memory-bank-foundation.md
---

# Use Markdown as Canonical Memory Bank Storage

## Summary

- Plain UTF-8 Markdown is the only canonical knowledge representation.
- The MCP server scans Markdown directly and may cache only rebuildable data.
- Standard links and YAML front matter preserve VS Code and Obsidian portability.
- No database, vector store, or editor plugin is required for reading.

## Context

The knowledge base must serve humans and AI agents, minimize context use, remain
Git-reviewable, and work on Windows without operational infrastructure.

## Decision

Store project knowledge, specifications, and ADRs as Markdown under
`memory-bank/`. Use YAML front matter for machine filters and standard Markdown
headings/links for navigation. Implement bounded search with local scanning and
an in-process cache.

## Alternatives

- SQLite FTS: capable but adds a second local artifact and migration/rebuild operations.
- Vector database: unnecessary for the current corpus and duplicates source-analysis indexes.
- Obsidian wiki links/database: reduces portability and makes an editor part of the format.
- Generated monolithic context file: poor diffs and inefficient incremental reading.

## Consequences

The system remains transparent and operationally simple. Search ranking is
lexical, not semantic, and large-corpus performance is bounded by filesystem
scanning; an mtime cache is sufficient for the current expected scale.

## Risks

- Manual edits can introduce broken metadata or links; the validator mitigates this.
- YAML and Markdown parsers may differ on edge cases; conventions stay deliberately narrow.
- Concurrent writers use atomic replacement but not distributed locking.

## Evidence

- `repo:kfk-tasks:IMPLEMENTATION-PLAN.md`
- `repo:kfk-tasks:src/memory_bank_mcp/store.py`

## Related Documents

- [Foundation specification](../specifications/spec-0001-memory-bank-foundation.md)

