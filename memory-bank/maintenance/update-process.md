---
title: Memory Bank Update Process
scope: kafka-adapter-ecosystem
type: maintenance
status: verified
updated: 2026-07-29
sources:
  - "repo:kfk-tasks:src/memory_bank_mcp/validator.py"
  - "repo:kfk-tasks:memory-bank/specifications/README.md"
related:
  - pending-verification.md
  - ../agents/instructions.md
---

# Memory Bank Update Process

## Summary

- Update only facts affected by the implemented change.
- Preserve verified content unless new evidence supersedes it.
- Keep one canonical home per fact.
- Record conflicts and uncertainty explicitly.
- Update specifications and ADRs before declaring work complete.
- Run structural validation after manual or MCP writes.

## Procedure

1. Update the specification implementation result.
2. Record deviations from approved design.
3. Update affected architecture/repository/component documents.
4. Add or supersede ADRs when a durable decision changes.
5. Check relative links and heading anchors.
6. Run tests and validator.
7. Review diffs for duplication, source dumps, and unrelated rewrites.
8. Confirm no absolute path, secret, or personal editor state was added.

## Status policy

- `draft`: content not yet evidence-backed.
- `partially-verified`: key facts checked, some assumptions remain.
- `verified`: current checkout evidence supports the material claims.
- `deprecated`: retained only for history/navigation.

Update `updated` with the ISO date of the material review. A formatting-only
change does not require changing evidence status.

## Validation

Run:

```powershell
$env:PYTHONPATH = "src"
python -m memory_bank_mcp.cli validate
```

Warnings require human triage; errors block a clean handoff.

