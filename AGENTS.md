# Repository Agent Instructions

Apply the required [workspace instructions](../AGENTS.md). The rules below are this repository's delta and override shared rules on conflict.

This repository owns task tracking, SDD specifications, and architecture decisions; it does not own product source.

- Store specifications under `sdd/` and architecture decisions under `adr/`.
- Write SDD content in Russian while preserving technical identifiers, commands, and paths.
- Preserve stable SDD and ADR IDs and their historical records during moves or index maintenance.
- Keep migration and audit reports bounded to their task; do not recreate a general-purpose central knowledge base.
- Do not store raw MCP output, secrets, absolute workspace paths, personal configuration, or reasoning logs.
- Changes to product documentation or source require explicit multi-repository scope in an approved SDD.
- Keep only bounded, active task handoffs under `work/`: one file per Issue or approved SDD workstream. A handoff records committed revisions, completed work, decisions, remaining actions, and verification gaps; it is not a general-purpose Memory Bank.
- At completion, promote durable conclusions into the SDD, ADR, or owning repository documentation and remove the active handoff. Git history supplies the audit trail.
