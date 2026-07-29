---
title: kafka-adapter-tests-reports Repository
scope: kafka-adapter-tests-reports
repository: kafka-adapter-tests-reports
type: repository
status: verified
updated: 2026-07-29
components:
  - test-reporting
sources:
  - "repo:kafka-adapter-tests-reports:README.md"
  - "repo:kafka-adapter-tests-reports:latest/allure-unit/summary.json"
  - "repo:kafka-adapter-tests-reports:latest/allure-ui/summary.json"
related:
  - kafka-adapter-tests-unit.md
  - kafka-adapter-tests-ui.md
---

# kafka-adapter-tests-reports Repository

## Summary

- This repository publishes generated test and static-analysis HTML.
- It contains Allure UI, Allure Unit, and Sonar reports.
- `latest/` mirrors the newest published run.
- Run-specific directories use workflow run and attempt identifiers.
- Publication is performed by the product release workflow.
- Generated directories must not be manually edited.

## Responsibility

Store deployable GitHub Pages artifacts and retain a bounded history of release
verification outputs.

## Use

Consult report data to investigate failures and establish historical evidence.
Do not treat report HTML as a source repository or copy generated content into
the Memory Bank.

## Limitations

Presence of a report does not prove that the current uncommitted checkout was
tested. Correlate with the producing workflow run and commit when making a
release claim.

