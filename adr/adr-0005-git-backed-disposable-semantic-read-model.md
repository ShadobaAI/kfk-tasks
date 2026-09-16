---
title: Git-backed disposable semantic read-model for Codex project context
id: ADR-0005
type: decision
status: accepted
created: 2026-09-14
updated: 2026-09-14
related_specifications:
  - SPEC-0012
affected_repositories:
  - kafka-tools
  - kfk-tasks
  - kafka-adapter
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-unit
  - kafka-adapter-tests-reports
  - kafka-adapter-tests-ui
sources:
  - "repo:kfk-tasks:sdd/spec-0012-codex-context-quality-and-cost.md"
  - "repo:kfk-tasks:adr/adr-0002-repository-documentation-and-agents.md"
  - "repo:kfk-tasks:adr/adr-0004-code-index-bsl-ls-analysis-plane.md"
---

# Git-backed disposable semantic read-model for Codex project context

## Summary

- Canonical project knowledge remains in the owning Git repositories; a developer-local OpenViking index is only a disposable read-model of committed documents.
- Codex receives a bounded, read-only retrieval surface, while source, metadata, platform, and normative authority remain with EDT, code-index, BSL LS, and v8std.

## Context

ADR-0002 removed the central Memory Bank because it duplicated repository documentation and became stale. Task-scoped Codex sessions still need efficient access to reviewed project history across session and developer boundaries. A derived index can reduce repeated broad reads without taking ownership of knowledge, provided it follows the local Git revisions and can be rebuilt completely.

## Decision

1. Product knowledge stays in owning repository documentation; SDD, ADR, and bounded active handoff artifacts stay in `kfk-tasks`. Git remains the only durable, shared source.
2. Each developer builds a local OpenViking read-model from explicitly selected, tracked documents at the committed `HEAD` of their current checkouts. Dirty and untracked content is excluded.
3. The read-model is disposable. Its index, embeddings, semantic sidecars, session storage, and runtime files may be deleted and rebuilt from Git without losing team knowledge.
4. Codex accesses OpenViking only through an explicit read-only, bounded MCP allowlist. Writable memory, auto-memory, ingestion, and administrative tools are not exposed to Codex.
5. A revision check before retrieval is the correctness boundary. Git hooks may trigger eager reconciliation but cannot substitute for that check. Stale or failed reconciliation blocks dependent retrieval.
6. OpenViking provides historical and documented context, never live source, metadata, call/reference analysis, platform API, or normative authority. ADR-0004's EDT, code-index, BSL LS, and v8std boundaries remain unchanged.
7. This decision supersedes only ADR-0002's prohibition on a dedicated *derived* knowledge MCP/read-model. ADR-0002's ownership model and its rejection of a canonical central Memory Bank remain in force.

## Alternatives

- Keep relying on long-lived Codex sessions: rejected because stale context and compaction undermine reproducibility.
- Restore a writable central Memory Bank: rejected because it creates a second source of truth.
- Use OpenViking as shared team storage: rejected because developer branches and Git review would no longer determine project knowledge.
- Index source code and standards in OpenViking: rejected because specialized authoritative planes already own those facts.

## Consequences

- Fresh sessions and clean developer clones can reconstruct the same source inventory from committed revisions.
- Local runtime, provider configuration, revision reconciliation, and rebuild validation become operational requirements.
- Semantic ranking may vary with local models, but canonical resources and readiness must not.
- A missing or stale OpenViking runtime blocks only work that depends on historical/project-context retrieval.

## Risks

- Missed Git hooks may leave an index stale; mandatory pre-use revision checks prevent stale results from being accepted.
- A broad or writable MCP surface could recreate the Memory Bank problem; the proxy and guard must default deny.
- Provider cost and context growth require bounded retrieval and explicit measurement.

## Evidence

- `repo:kfk-tasks:sdd/spec-0012-codex-context-quality-and-cost.md`
- `repo:kfk-tasks:adr/adr-0002-repository-documentation-and-agents.md`
- `repo:kfk-tasks:adr/adr-0004-code-index-bsl-ls-analysis-plane.md`

## Related Documents

- [SPEC-0012](../sdd/spec-0012-codex-context-quality-and-cost.md)
- [ADR-0002](adr-0002-repository-documentation-and-agents.md)
- [ADR-0004](adr-0004-code-index-bsl-ls-analysis-plane.md)
