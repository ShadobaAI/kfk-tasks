# Architecture Decision Records

## Purpose

ADRs record durable architecture decisions and their consequences. IDs are stable and independent of Issues. Do not use ADRs for routine implementation details.

## Lifecycle

```text
proposed -> accepted -> superseded
proposed -> rejected
```

An accepted ADR is not silently rewritten when the decision changes. Create a new ADR and link both records through `superseded_by`/`supersedes`.

## Index

| ID | Decision | Status |
|---|---|---|
| [ADR-0001](adr-0001-markdown-canonical-storage.md) | Markdown as canonical Memory Bank storage | `superseded` |
| [ADR-0002](adr-0002-repository-documentation-and-agents.md) | Repository documentation and hierarchical agent instructions | `accepted` |

For a new decision, copy [the template](template.md).

