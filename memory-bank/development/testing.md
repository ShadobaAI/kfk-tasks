---
title: Testing Strategy and Locations
scope: kafka-adapter-ecosystem
type: development
status: verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/project/repositories.md"
  - "repo:kafka-adapter-tests-unit:README.md"
  - "repo:kafka-adapter-tests-ui:README.md"
  - "repo:kafka-adapter-tests-reports:README.md"
related:
  - ../repositories/kafka-adapter-tests-unit.md
  - ../repositories/kafka-adapter-tests-ui.md
  - ../repositories/kafka-adapter-tests-reports.md
---

# Testing Strategy and Locations

## Summary

- YAxUnit covers deterministic 1C application logic.
- Vanessa Automation covers managed UI behavior.
- Product release CI combines unit, UI, coverage, and static analysis.
- Allure/Sonar outputs are published separately.
- Examples and the base configuration supply test fixtures and host context.
- A report must be correlated with its commit before making a release claim.

## Contours

| Contour | Repository | Use |
|---|---|---|
| Unit | `kafka-adapter-tests-unit` | Queue/routing/serialization/helper logic |
| UI | `kafka-adapter-tests-ui` | Forms, writes, user workflows |
| Static | `kafka-adapter` plus Sonar tooling | BSL quality and diagnostics |
| Integration | Product/base/examples plus Kafka | Connector and broker behavior |
| Publication | `kafka-adapter-tests-reports` | Allure/Sonar evidence |
| Memory Bank | `kfk-tasks/tests` | MCP, security, Markdown validation |

## Selection guidance

- Public API or status change: unit plus integration.
- Managed form change: focused unit where possible plus UI feature.
- Connector/session change: integration against a Kafka cluster.
- Conversion Data attachment change: `conv_edt` diagnostics and an end-to-end
  generated contract scenario.
- Documentation-only change: link/front-matter/anchor validation.

## Current checkout observations

- EDT problem summary for `adapter`, `base`, and `examples`: zero.
- EDT problem summary for `KFK`: 2 major and 18 minor; no errors.
- UI repository: three feature files in the checkout.
- Unit repository: one main YAxUnit common module plus assembly scripts.

These are observations from 2026-07-29, not permanent project properties.

## Memory Bank verification

Run:

```powershell
python -m unittest discover -s tests -v
$env:PYTHONPATH = "src"
python -m memory_bank_mcp.cli validate
```

