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
| [ADR-0003](adr-0003-edt-authoritative-writer.md) | EDT-MCP как единственный writer для 1С-проектов Codex | `superseded` |
| [ADR-0004](adr-0004-code-index-bsl-ls-analysis-plane.md) | code-index и BSL LS как read-only analysis plane для 1С-проектов Codex | `accepted` |
| [ADR-0005](adr-0005-git-backed-disposable-semantic-read-model.md) | Git-backed disposable semantic read-model for Codex project context | `accepted` |
| [ADR-0006](adr-0006-openviking-ollama-docker.md) | Docker-only runtime для OpenViking и Ollama | `superseded` |
| [ADR-0007](adr-0007-external-ollama-gpu-host.md) | Внешняя Ollama на GPU хоста для OpenViking в ВМ | `accepted` |

For a new decision, copy [the template](template.md).
