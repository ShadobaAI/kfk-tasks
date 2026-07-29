---
title: Change Process
scope: kafka-adapter-ecosystem
type: development
status: partially-verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/project/contributing.md"
  - "repo:kfk-tasks:memory-bank/specifications/README.md"
related:
  - conventions.md
  - ../specifications/README.md
  - ../decisions/README.md
---

# Change Process

## Summary

- Determine ownership before editing.
- Use an SDD specification for non-trivial behavior or cross-repository work.
- Use ADRs for durable architecture decisions.
- Issues are optional tracking, not the requirement source.
- Verify against source/tests and route MCP by project.
- Update result, deviations, knowledge, and validation after implementation.

## Workflow

1. Read the root index and affected summaries.
2. Confirm repository and component ownership.
3. Inspect current source, tests, and only then detailed docs.
4. Link an existing specification or create one.
5. Resolve open design decisions; write an ADR if durable.
6. Implement the minimum scoped change.
7. Run risk-proportionate checks.
8. Record implementation result, deviations, commits/PRs when available.
9. Update affected stable knowledge.
10. Run Memory Bank validation.

## Cross-repository changes

Split implementation by repository ownership but keep one specification when the
change represents one user-visible capability. Acceptance criteria must name
every affected repository and compatibility boundary.

## Completion

A specification is `verified` only when acceptance criteria have evidence.
Documentation and test updates are part of implementation, not follow-up debt
unless explicitly recorded as an unresolved item.

## Uncertainty

Do not block every task on an Issue or full architecture review. Conversely, do
not silently implement against unverified connector/platform/version behavior.

