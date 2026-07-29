---
title: Development and Documentation Conventions
scope: kafka-adapter-ecosystem
type: development
status: partially-verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/project/contributing.md"
  - "repo:kafka-adapter:docs/project/modules.md"
  - "repo:kafka-adapter:.editorconfig"
related:
  - navigation.md
  - change-process.md
---

# Development and Documentation Conventions

## Summary

- Preserve repository-local style and original Russian 1C identifiers.
- Adapter-owned metadata uses the `кфк` prefix.
- Public application calls are limited to documented facade modules.
- Keep changes scoped to the owning repository.
- Add or update tests with behavior changes.
- Memory Bank prose is English and evidence-linked.
- Generated outputs and raw MCP responses are not documentation.

## 1C conventions

- Treat `*Служебный*` modules as internal.
- Keep execution context, export status, and handler signatures explicit.
- Preserve strict-type and region conventions in modules that use them.
- Validate BSL through EDT and relevant checks when BSL is modified.
- Do not infer metadata availability across extensions; verify the attachment.

## Documentation conventions

- UTF-8, LF, standard Markdown, YAML front matter.
- Stable headings and relative links.
- Five to ten concise points in `## Summary`.
- One canonical home per fact; link rather than copy.
- Use `TODO: verification required` or `Not verified against source code` for
  evidence gaps.
- No absolute workspace paths, tokens, credentials, or editor-specific wiki links.

## Evidence language

Use `verified` only when current source/tests or a current checkout-specific MCP
result supports the content. Use `partially-verified` when a document combines
verified facts with runtime/version assumptions.

## Scope control

Business changes belong to their source repository. This `kfk-tasks` repository
owns only task knowledge, SDD/ADR, Memory Bank service code, and its tests.

