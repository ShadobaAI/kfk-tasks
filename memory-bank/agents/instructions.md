---
title: AI Agent Instructions
scope: kafka-adapter-ecosystem
type: instructions
status: verified
updated: 2026-07-29
sources:
  - "repo:kfk-tasks:memory-bank/README.md"
  - "repo:kafka-adapter:docs/project/repositories.md"
related:
  - ../README.md
  - ../development/navigation.md
  - ../maintenance/update-process.md
---

# AI Agent Instructions

## Summary

- Start at the root index and read summaries first.
- Identify affected repositories/components before detailed source.
- Source and tests outrank the Memory Bank.
- Route each 1C project only to its assigned MCP.
- Preserve Russian identifiers and write Memory Bank prose in English.
- Cite portable repository paths/FQNs and distinguish assumptions.
- Update specifications/results/deviations and affected knowledge after changes.

## Required sequence

1. Read [the Memory Bank index](../README.md).
2. Read project and repository summaries.
3. Determine affected components and current specification/Issue, if any.
4. Inspect current source/tests with bounded requests.
5. Load detailed documents only as needed.
6. Implement minimal scoped changes.
7. Verify proportionately and update maintained knowledge.

## Authority

Current local source and tests describe factual behavior. Specialized MCPs are
interfaces to the checkout, not independent truth. The Memory Bank is maintained
context and may be stale; record conflicts rather than hiding them.

## MCP routing

- Code Metadata Search: `adapter/adapter` only.
- Graph Metadata Search: `adapter/adapter` only.
- `kfk_edt`: `adapter/adapter`, `adapter/base`, `adapter/examples`.
- `conv_edt`: `conversion/KFK`, `conversion/КД`.
- Help/docs/SSL/templates: supporting reference after source confirms relevance.
- Syntax/code checks: validate BSL fragments; they do not prove runtime behavior.
- Memory Bank MCP: this repository's knowledge, ADR, SDD, and navigation only.

Never route a project through an MCP index assigned to another project group.
Do not call destructive EDT operations for analysis.

## Context discipline

- Request lists, signatures, metadata, sections, or line ranges before full modules.
- Do not load the complete Memory Bank.
- Do not store raw MCP output or complete source listings.
- Prefer one canonical fact and links.
- Respect `max_chars` and result limits.

## Writing

- English prose; keep original 1C object/module/form identifiers.
- Standard Markdown links, YAML front matter, UTF-8.
- No absolute workspace paths, secrets, tokens, personal settings, or reasoning logs.
- Use `TODO: verification required` or `Not verified against source code`.

## Completion

After implementation:

- record actual result and deviations;
- update acceptance evidence and status;
- link commits/PRs where available;
- update affected repository/architecture documents;
- update ADRs if decisions changed;
- run validation and leave unresolved items explicit.

