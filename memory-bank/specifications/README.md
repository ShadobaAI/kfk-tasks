---
title: Specification-Driven Development
scope: kafka-adapter-ecosystem
type: index
status: verified
updated: 2026-07-29
sources:
  - "repo:kfk-tasks:memory-bank/specifications/template.md"
related:
  - template.md
  - spec-0001-memory-bank-foundation.md
  - spec-0002-simple-kafka-adapter-1-9-2.md
  - ../decisions/README.md
---

# Specification-Driven Development

## Summary

- Specifications are the requirement and implementation-design record.
- IDs are stable and do not depend on GitHub Issues.
- Issues remain optional tracking/discussion links.
- Status transitions require increasing evidence.
- Implementation results and deviations are mandatory after implementation.
- Architecture decisions link to ADRs.

## Lifecycle

```text
draft -> approved -> in-progress -> implemented -> verified
draft/approved -> rejected
any non-terminal -> superseded
```

| Status | Minimum information |
|---|---|
| `draft` | Problem, goal, scope, initial requirements, open questions |
| `approved` | Resolved blocking questions, acceptance criteria, design |
| `in-progress` | Owner and implementation plan |
| `implemented` | Result, deviations, tests run, remaining verification |
| `verified` | Acceptance evidence and Memory Bank updates complete |
| `rejected` | Reason and alternatives |
| `superseded` | Replacement specification link |

## Rules

- File: `<id-lowercase>-<short-name>.md`.
- Metadata ID: `SPEC-NNNN`.
- One capability can span repositories; list each explicitly.
- Non-goals prevent scope drift.
- Acceptance criteria must be observable.
- Record actual result, not intended result.
- Update related architecture and repository documents after implementation.

## Index

| ID | Specification | Status |
|---|---|---|
| [SPEC-0001](spec-0001-memory-bank-foundation.md) | Memory Bank and SDD foundation | implemented |
| [SPEC-0002](spec-0002-simple-kafka-adapter-1-9-2.md) | Upgrade Simple-Kafka_Adapter to 1.9.2+ | verified |

## Creation

Copy [the template](template.md) or call `create_specification` through the
Memory Bank MCP.
