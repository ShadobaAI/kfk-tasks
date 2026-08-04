---
title: Upgrade Simple-Kafka_Adapter to 1.9.2+
id: SPEC-0002
type: specification
status: verified
owner: null
created: '2026-07-29'
updated: '2026-07-29'
github_issue: https://github.com/ShadobaAI/kfk-tasks/issues/52
affected_repositories:
- kafka-adapter
affected_components:
- DataProcessor.кфкИнтеграция
- CommonTemplate.кфкАдаптерKafka
- documentation
related_adrs: []
tags:
- specification
- kafka
- external-component
- compatibility
sources:
- repo:kafka-adapter:DataProcessor.кфкИнтеграция
- repo:kafka-adapter:CommonTemplate.кфкАдаптерKafka
- repo:kafka-adapter:README.md
related:
  - ../../adapter/adapter/docs/user/development/api.md
  - ../../adapter/adapter/docs/project/repositories.md
---
# Upgrade Simple-Kafka_Adapter to 1.9.2+

## Summary

- Upgrade the embedded Simple-Kafka_Adapter compatibility baseline from `1.9.1+` to `1.9.2+`.
- The binary common template has already been replaced with the `v1.9.2` release artifact.
- Extend the `кфкИнтеграция` object-module wrappers with the optional `Брокеры` argument introduced in `v1.9.2`.
- Preserve existing calls and parameter defaults.
- Verify argument validation, broker-backed metadata checks, batch atomicity, diagnostics, and documentation.

## Context

`kafka-adapter` embeds Simple-Kafka_Adapter in `CommonTemplate.кфкАдаптерKafka` and exposes its operations through `DataProcessor.кфкИнтеграция`.

Before implementation, the embedded binary and common-template comment already
referenced `v1.9.2`, while the object module still exposed the `v1.9.1`
position-setting signatures and project documentation still stated `1.9.1+`
as the minimum version.

Upstream `v1.9.2` adds an optional broker argument to `УстановитьПозициюЧтения` and `УстановитьПозицииЧтения`. It also changes these methods from unconditional success to validated Boolean results and makes batch position updates atomic.

## Problem

The embedded component and its BSL wrapper no longer expose the same contract. Application code cannot explicitly provide brokers for topic, partition, and offset validation through the wrapper. Documentation also advertises an obsolete compatibility baseline.

## Goal

Align the BSL wrapper and project documentation with Simple-Kafka_Adapter `v1.9.2+` while preserving source compatibility for existing consumers.

## Non-goals

- Change the JSON or array format accepted by `УстановитьПозицииЧтения`.
- Reimplement Kafka metadata validation in BSL.
- Refactor unrelated `кфкИнтеграция` methods.
- Remove the deprecated `УстановитьПозициюЧтения` method.
- Add wrappers for upstream changes that do not introduce a new public method or parameter required by this upgrade.

## Scope

Repository: `kafka-adapter`.

Required changes:

- `repo:kafka-adapter:DataProcessor.кфкИнтеграция` object module;
- embedded component version evidence in `repo:kafka-adapter:CommonTemplate.кфкАдаптерKafka`;
- minimum-version declarations in project and installation documentation;
- focused automated or integration checks for the changed contract.

## Functional Requirements

### FR-1: Single-position wrapper

Change the exported BSL signature to the equivalent of:

```bsl
Функция УстановитьПозициюЧтения(Топик, Смещение, Партиция = 0, Брокеры = "") Экспорт
```

The wrapper must pass `Брокеры` as the last argument to the external component and return its Boolean result without replacing the component's validation.

The existing deprecation notice and recommendation to use `УстановитьПозицииЧтения` must remain.

### FR-2: Batch-position wrapper

Change the exported BSL signature to the equivalent of:

```bsl
Функция УстановитьПозицииЧтения(Позиции, Брокеры = "") Экспорт
```

The wrapper must pass `Брокеры` as the last argument to the external component and return its Boolean result.

### FR-3: Broker argument semantics

`Брокеры` must:

- be documented as `Строка, Массив Из Строка`;
- default to an empty string;
- provide one or more Kafka broker addresses used by the component for topic, partition, and offset validation;
- allow the component to fall back to `bootstrap.servers` and then `metadata.broker.list` when empty;
- preserve local-only argument validation when no broker address can be resolved.

### FR-4: Validation behavior

The wrapper must expose the component's `Ложь` result and diagnostics through `ПолучитьСообщениеОбОшибке()` for applicable invalid input, including:

- empty or invalid topic name;
- negative partition number;
- invalid argument type;
- invalid JSON, absent `metadata`, or empty `metadata` for batch input;
- nonexistent topic or partition when broker metadata is available;
- non-negative offset above the partition high watermark when broker metadata is available.

Special negative librdkafka offsets must not be rejected by the range check.

### FR-5: Atomic batch behavior

If any entry supplied to `УстановитьПозицииЧтения` is invalid, the component must reject the entire set and apply none of the positions.

### FR-6: Version documentation

Change the minimum supported component version from `1.9.1+` to `1.9.2+` in at least:

- `repo:kafka-adapter:README.md`;
- `repo:kafka-adapter:docs/user/installation/updating.md`;
- `repo:kafka-adapter:docs/user/installation/requirements.md`;
- `repo:kafka-adapter:docs/project/environment.md`.

The common-template comment must reference the upstream `v1.9.2` release.

## Non-functional Requirements

- Preserve the order and defaults of all existing parameters.
- Preserve source compatibility for calls that omit `Брокеры`.
- Keep documentation comments consistent with project BSL style.
- Do not duplicate component-side validation in 1C code.
- The changed BSL must pass the project's applicable syntax and static checks.

## Architecture and Design

The BSL layer remains a thin adapter over the external component. Validation ownership stays in Simple-Kafka_Adapter because it owns librdkafka configuration, metadata access, special offsets, and last-error diagnostics.

No ADR is required: this is a compatible extension of an existing adapter boundary and does not change repository or subsystem architecture.

`v1.9.2` also changes Admin API timeout handling, asynchronous error propagation, UTF conversion, and Avro `time-millis` handling. These changes require regression smoke coverage where practical but no additional BSL wrapper design.

## Implementation Plan

1. Confirm the embedded binary reports version `1.9.2` or later.
2. Add `Брокеры = ""` to both exported wrapper signatures.
3. Pass the new argument to the corresponding component calls.
4. Update both BSL API comments with semantics, validation, diagnostics, and batch atomicity.
5. Update all minimum-version documentation references.
6. Add or update focused tests.
7. Run syntax/static checks and Kafka-backed smoke tests.
8. Record implementation results and any deviations in this specification.

## Compatibility and Migrations

No application-code migration is required because the argument is appended and optional.

Consumers that need deterministic broker-backed validation should pass `Брокеры` explicitly. With an empty argument and no broker setting available to the component, only local validation is guaranteed.

No metadata or persisted-data migration is required.

## Testing

Required checks:

1. Component connection smoke test and `ВерсияКомпоненты()` result of `1.9.2` or later.
2. Regression calls to both methods without `Брокеры`.
3. Calls to both methods with an explicit reachable broker.
4. Local validation when no broker address is available.
5. Broker-backed rejection of a nonexistent topic, nonexistent partition, and offset above high watermark.
6. Acceptance of supported special negative librdkafka offsets.
7. Batch atomicity: one invalid entry rejects the full set.
8. `ПолучитьСообщениеОбОшибке()` returns a non-empty useful diagnostic after failed validation.
9. Message-read smoke test after successfully setting a position.
10. BSL syntax and applicable project static checks.

Assertions against diagnostic text must verify presence and usefulness, not exact wording, because the external component owns the message.

## Risks

- Kafka metadata checks require a reachable test broker and cannot be fully replaced by unit tests.
- Empty `Брокеры` does not guarantee metadata validation when neither supported broker setting is present.
- The embedded artifact is binary; its version and platform variants require runtime verification rather than source inspection alone.
- Upstream `v1.9.2` changes error propagation and Admin API timeout behavior beyond the two signatures; focused regression smoke tests are needed to detect integration regressions.

## Acceptance Criteria

- The embedded component reports version `1.9.2` or later at runtime.
- Both `кфкИнтеграция` functions expose optional `Брокеры = ""` and forward it to the component.
- Existing calls without `Брокеры` continue to compile and work.
- A valid existing topic, partition, and offset returns `Истина` under the documented preconditions.
- Invalid topic, partition, or offset returns `Ложь` and exposes a non-empty diagnostic.
- A batch containing one invalid position applies no positions.
- All listed documents state `1.9.2+`.
- The common-template release reference points to `v1.9.2`.
- The configuration builds, and changed BSL passes applicable syntax and static checks.

## Open Questions

- Broker-backed validation and batch-atomicity scenarios remain general
  integration-test follow-up; no test-suite ownership was added by this change.
- Windows x86-64 and Linux x86-64 artifacts were verified statically from
  `MANIFEST.XML` and bundle entries. Runtime matrix coverage remains a release
  infrastructure follow-up.

Neither follow-up blocks this release. Runtime coverage is tracked in
`maintenance/pending-verification.md`.

## Release Disposition

- Product commit:
  `84dd8f32bc5d55b9645051ad325f7f90e577fa1d`
  (`обновил Simple-Kafka_Adapter до 1.9.2+ ShadobaAI/kfk-tasks#52`).
- Commit is present in `origin/main`; the `kafka-adapter` worktree was clean at
  release-readiness review on 2026-07-29.
- The owner marked the task ready for release on 2026-07-29.
- Runtime 1C and Kafka-backed checks are explicitly waived for this release.
  The accepted residual risk is that component validation, diagnostics, batch
  atomicity, and message-read behavior were not exercised in this checkout.

## Implementation Result

- `кфкИнтеграция.УстановитьПозицииЧтения` accepts optional `Брокеры = ""`,
  normalizes a string or array of strings through `МассивИзСтроки`, and forwards
  it to the external component after the unchanged JSON conversion.
- Deprecated `кфкИнтеграция.УстановитьПозициюЧтения` accepts optional
  `Брокеры = ""`, applies the same normalization, and forwards it as the last
  component argument.
- Both API comments document broker resolution, local-only validation fallback,
  diagnostics, and atomic batch rejection.
- `README.md` and all three required installation/environment pages now declare
  Simple Kafka Connector 1C `1.9.2+`.
- The existing common-template update was preserved. Static bundle inspection
  found `SimpleKafka1C64_1_9_2.dll`, `SimpleKafka1C64_1_9_2.so`, and matching
  `MANIFEST.XML` entries; SHA-256 of the bundle is
  `EC9D7557BAA98DB7BD5214FFE38F33067BC44F30355732F421F020A11177A5CF`.

Executed checks:

- EDT targeted revalidation of `DataProcessor.кфкИнтеграция`: no problems.
- EDT module structure inspection: both signatures and defaults recognized.
- BSL syntax analysis of the changed wrappers: no syntax errors.
- `git diff --check`: passed.
- Release commit contents match the reviewed implementation and documentation.
- Source/documentation assertions: no remaining `1.9.1+` declarations in
  `kafka-adapter`; all required `1.9.2+` declarations and the `v1.9.2`
  template reference are present.

Accepted verification waiver:

- Tests requiring a 1C runtime were skipped by explicit user instruction.
  An earlier configured thin-client debug launch did not reach the startup
  breakpoint and was terminated without executing assertions.
- Kafka-backed metadata validation, special offsets, atomicity, diagnostics,
  and message-read smoke tests were not executed.

## Deviations from Specification

- No automated product test was added. Test-suite ownership remains unresolved,
  and no test project was loaded in the EDT workspace. The owner accepted this
  deviation for release; runtime behavior remains an explicitly tracked risk.

## Memory Bank Updates

- `architecture/public-api.md` was not changed because it documents the
  application facade, not `DataProcessor.кфкИнтеграция` transport wrappers.
- `repositories/kafka-adapter.md` now records the `1.9.2+` connector baseline.
- `architecture/integrations.md` records the upgraded connector boundary and
  its runtime-verification limitation.
- `development/testing.md` was not changed because integration-test ownership
  remains unresolved.
- `maintenance/pending-verification.md` retains runtime connector coverage as a
  release follow-up.
- Specification status, release commit, waiver, and executed checks were
  recorded here.

## Related Documents

- [Public API](../../adapter/adapter/docs/user/development/api.md)
- [Kafka adapter repositories and testing](../../adapter/adapter/docs/project/repositories.md)
- [SDD lifecycle](README.md)
- [GitHub Issue #52](https://github.com/ShadobaAI/kfk-tasks/issues/52)
- [Simple-Kafka_Adapter v1.9.2](https://github.com/NuclearAPK/Simple-Kafka_Adapter/releases/tag/v1.9.2)
