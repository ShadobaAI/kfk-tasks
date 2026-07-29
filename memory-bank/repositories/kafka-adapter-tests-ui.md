---
title: kafka-adapter-tests-ui Repository
scope: kafka-adapter-tests-ui
repository: kafka-adapter-tests-ui
type: repository
status: verified
updated: 2026-07-29
components:
  - ui-tests
sources:
  - "repo:kafka-adapter-tests-ui:README.md"
  - "repo:kafka-adapter-tests-ui:features/011_Справочники_ФормаСписка.feature"
related:
  - kafka-adapter-tests-reports.md
  - ../development/testing.md
---

# kafka-adapter-tests-ui Repository

## Summary

- Vanessa Automation drives the UI test contour.
- The current checkout contains three feature files.
- Scenarios cover list form, object form, and write behavior for catalogs.
- `VAParams.json` configures the runner.
- This repository is development-only.
- Reports are published by the separate reports repository.

## Responsibility

Verify user-observable adapter behavior through managed forms and application
actions.

## Navigation

- `features/011_Справочники_ФормаСписка.feature`
- `features/012_Справочники_ФормаОбъекта.feature`
- `features/013_Справочники_Запись.feature`
- `VAParams.json`

## Limitation

The current feature set is narrower than the architecture documentation's full
administration and queue surface. Do not infer UI coverage from documented
capabilities alone.

