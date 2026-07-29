---
title: kafka-adapter-tests-unit Repository
scope: kafka-adapter-tests-unit
repository: kafka-adapter-tests-unit
type: repository
status: verified
updated: 2026-07-29
components:
  - unit-tests
  - test-assembly
sources:
  - "repo:kafka-adapter-tests-unit:README.md"
  - "repo:kafka-adapter-tests-unit:src/CommonModules/ОМ_ЮТест/Module.bsl"
  - "repo:kafka-adapter-tests-unit:scripts/create_test_edt.py"
related:
  - kafka-adapter-examples.md
  - kafka-adapter-tests-reports.md
  - ../development/testing.md
---

# kafka-adapter-tests-unit Repository

## Summary

- YAxUnit is the unit-test framework.
- The canonical Git repository is `tests/unit/unit`.
- `ОМ_ЮТест` contains the current BSL test suite.
- Assembly scripts compose base, adapter, examples, and YAxUnit projects.
- `YaxParams.json` configures execution.
- Sibling `tests/unit/base` is generated/local assembly output, not canonical source.

## Responsibility

Verify adapter application logic and provide repeatable assembly of the EDT
test project.

## Navigation

| Purpose | Path |
|---|---|
| Test module | `src/CommonModules/ОМ_ЮТест/Module.bsl` |
| EDT assembly | `scripts/create_test_edt.py`, `create_test_edt.sh` |
| Runner settings | `YaxParams.json` |
| Extension metadata | `src/Configuration/Configuration.mdo` |

## Test ownership

Use unit tests for deterministic queue, routing, serialization, status, and
helper behavior. Kafka cluster, connector, or managed-form behavior requires a
different contour.

