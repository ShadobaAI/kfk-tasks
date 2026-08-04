---
title: Use repository documentation and hierarchical agent instructions
id: ADR-0002
type: decision
status: accepted
created: 2026-08-03
updated: 2026-08-03
supersedes: ADR-0001
related_specifications:
  - SPEC-0004
  - SPEC-0005
  - SPEC-0006
  - SPEC-0007
affected_repositories:
  - kfk-tasks
  - kafka-adapter
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-reports
  - kafka-adapter-tests-ui
  - kafka-adapter-tests-unit
  - kafka-tools
sources:
  - "repo:kfk-tasks:sdd/spec-0007-memory-bank-retirement.md"
related:
  - adr-0001-markdown-canonical-storage.md
  - ../sdd/spec-0007-memory-bank-retirement.md
---

# Use repository documentation and hierarchical agent instructions

## Summary

- Product knowledge belongs to the documentation and source of its owning repository.
- Shared agent workflow is stored once at `KAFKA_PROJECTS_ROOT/AGENTS.md`.
- Repository-local `AGENTS.md` files contain only repository-specific rules and a required relative link to the shared file.
- SDD and ADR remain reviewable Markdown under `tasks/sdd` and `tasks/adr`.
- The central Memory Bank and its MCP service are retired.

## Context

The Memory Bank duplicated repository documentation, stored quickly stale checkout observations, and required a dedicated MCP implementation and maintenance workflow. The project workspace has a fixed topology, so shared agent instructions can be centralized while repository-specific rules remain close to their owning source.

## Decision

Use the following canonical ownership model:

1. Product architecture, API, operations, and user guidance live in the owning repository documentation.
2. Current source and tests remain the primary evidence of actual behavior.
3. Shared workflow, safety, SDD/ADR gates, and MCP routing live in `KAFKA_PROJECTS_ROOT/AGENTS.md`.
4. Each Git repository has a local `AGENTS.md` that links to the shared file and defines only local responsibilities and exceptions.
5. Specifications and architecture decisions live in `tasks/sdd` and `tasks/adr` as plain Markdown.
6. Do not maintain a second central project knowledge representation or a dedicated MCP over it.
7. Preserve only durable, non-obvious knowledge. Obtain inventories, counts, diagnostics, and current metadata from source, tests, or the assigned EDT MCP.

## Alternatives

- Keep the Memory Bank and MCP: rejected because it duplicates ownership and adds operational cost.
- Keep a read-only central knowledge archive: rejected because it still becomes stale and creates a competing source of truth.
- Duplicate all common instructions in every repository: rejected because updates diverge across repositories.
- Require standalone repository clones: rejected because project development uses the fixed `KAFKA_PROJECTS_ROOT` layout.

## Consequences

- Agent workflow is maintained once, while local rules remain small.
- Repository documentation becomes the only durable home for product knowledge.
- Work outside the fixed workspace layout is unsupported.
- Current-state questions require source/test/EDT access instead of cached summaries.
- Historical SDD/ADR remain available without retaining the Memory Bank service.

## Risks

- A missing workspace-level `AGENTS.md` blocks repository work; local instructions must report the layout error.
- Incorrect value filtering can discard useful knowledge; migrations require an explicit audit and review.
- Relative links depend on the documented workspace topology.

## Evidence

- SPEC-0004 through SPEC-0006 establish and verify the hierarchical instructions.
- SPEC-0007 audits durable content and retires the previous model.

## Related Documents

- [Superseded decision](adr-0001-markdown-canonical-storage.md)
- [Migration specification](../sdd/spec-0007-memory-bank-retirement.md)

