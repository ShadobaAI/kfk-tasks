# Repository Agent Instructions

## Workspace Instructions

Read the required [workspace instructions](../AGENTS.md) before working in this repository. The fixed `KAFKA_PROJECTS_ROOT` layout is required. If the shared file is missing, report a workspace-layout error and stop. The repository-specific rules below supplement and override the shared rules when they conflict.

## Repository Scope

This repository owns task tracking, SDD specifications, and architecture decisions for the Kafka Adapter ecosystem. It does not own product source.

- Store specifications under `sdd/` and architecture decisions under `adr/`.
- Write all SDD content in Russian while preserving technical identifiers, commands, and paths.
- Preserve stable SDD and ADR IDs and their historical records during moves or index maintenance.
- Keep migration and audit reports bounded to their task. Do not recreate a general-purpose central knowledge base.
- Do not store raw MCP output, secrets, absolute workspace paths, personal configuration, or reasoning logs.
- Changes to product documentation or source require explicit multi-repository scope in an approved SDD.

