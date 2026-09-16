# Active task handoffs

This directory holds short, versioned handoffs for work that must cross a Codex session or developer boundary. Use one file per active Issue or approved SDD workstream, named by its stable identifier (for example `SPEC-0012.md`). Copy `template.md` and replace its placeholders. Only committed versions are shared team context.

Keep a handoff focused on decisions and next actions. Include the relevant committed revisions for every affected repository, completed work, changed contracts, unresolved questions, and checks already performed. Do not include raw tool output, exploratory transcripts, source dumps, secrets, personal configuration, or absolute local paths.

When the work finishes, move durable knowledge into the owning documentation, SDD result, or ADR, then remove the active handoff. Git history retains the record. This directory is not a Memory Bank or an archive of completed tasks.
