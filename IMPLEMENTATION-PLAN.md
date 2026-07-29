# Memory Bank implementation plan

## Scope

All created artifacts remain in `kfk-tasks`. Other repositories are read-only
evidence sources.

## Proposed tree

```text
memory-bank/                 Canonical Markdown knowledge
  architecture/             Components, integrations, data flows
  repositories/             One responsibility document per repository
  development/              Navigation, conventions, tests, change process
  decisions/                ADR index and template
  specifications/           SDD lifecycle, template, demonstration spec
  agents/                   Incremental context and MCP routing rules
  maintenance/              Update process and verification backlog
src/memory_bank_mcp/         Dependency-light MCP, document model, validator
tests/                       unittest coverage for reads, writes, security
config/                      Portable repository mapping example
docs/                        Installation, MCP, editor, validation documentation
```

## Document model

- UTF-8 Markdown with LF line endings.
- Compact YAML front matter on significant documents.
- Standard Markdown links only.
- `repo:<repository>:<relative-path-or-1C-FQN>` source references.
- A 5-10 point `## Summary` in each significant document.
- English prose; original Russian 1C identifiers are preserved.
- One canonical location per fact and progressive disclosure from the root
  index.

## SDD and ADR

- Specifications use stable `SPEC-NNNN` identifiers independent of Issues.
- Lifecycle: `draft -> approved -> in-progress -> implemented -> verified`,
  with `rejected` and `superseded` terminal alternatives.
- Architecture decisions use `ADR-NNNN`; files are immutable records except
  for status and consequence updates.
- Templates are plain Markdown and can be instantiated by MCP tools.

## MCP design

- Local stdio JSON-RPC/MCP server implemented with the Python standard library.
- Markdown scanning with an in-memory, mtime-aware cache; no database.
- Bounded list, metadata, summary, section, line-range, exact, ranked search,
  filters, ADR/spec retrieval, relationships, and task-context tools.
- Controlled create/update/section/spec/ADR operations with explicit create
  versus update semantics.
- Resources expose the root index, tree, templates, and individual documents.

## Security

- Paths are relative to `memory-bank/`; absolute, drive, UNC, traversal, and
  out-of-root paths are rejected.
- Final resolved paths are checked after symlink/junction resolution where the
  host permits it.
- Markdown is validated before mutation.
- Updates use a temporary sibling followed by `os.replace`.
- No client-provided command is executed.

## Configuration

- `KAFKA_PROJECTS_ROOT` resolves the changing workspace root.
- A portable JSON repository-to-relative-path map is committed.
- Optional local override is ignored by Git.
- No secrets, tokens, personal paths, or editor workspace state are committed.

## Validation and tests

- Validator checks structure, metadata, links, anchors, duplicate IDs/headings,
  navigation, source references, portability, orphans, and document size.
- `unittest` covers bounded reads/search, context assembly, lifecycle writes,
  traversal/UNC/drive rejection, overwrite protection, Cyrillic, atomic
  failure preservation, and validator findings.
- MCP startup and representative JSON-RPC requests are exercised as subprocess
  smoke tests.

## Explicit non-goals

- No source-code index, BSL parser, web UI, database, cloud service, containers,
  workflow engine, or generated mirror of analyzed repositories.
