---
title: Architecture Decision Records
scope: kafka-adapter-ecosystem
type: index
status: verified
updated: 2026-07-29
sources:
  - "repo:kfk-tasks:memory-bank/decisions/template.md"
related:
  - template.md
  - adr-0001-markdown-canonical-storage.md
  - ../specifications/README.md
---

# Architecture Decision Records

## Summary

- ADRs record durable architecture choices and their consequences.
- IDs are stable and independent of Issues.
- Accepted ADRs are not silently rewritten when a decision changes.
- Superseding ADRs link to the previous decision.
- Evidence and affected repositories are explicit.
- Routine task detail remains in the specification.

## Statuses

| Status | Meaning |
|---|---|
| `proposed` | Under review |
| `accepted` | Current decision |
| `rejected` | Considered and declined |
| `deprecated` | No longer recommended without a direct successor |
| `superseded` | Replaced by another ADR |

## Index

| ID | Decision | Status |
|---|---|---|
| [ADR-0001](adr-0001-markdown-canonical-storage.md) | Markdown as canonical Memory Bank storage | accepted |

## Creation

Copy [the template](template.md) or call the Memory Bank MCP `create_adr` tool.
Use the next unused numeric ID and a short lowercase filename.

