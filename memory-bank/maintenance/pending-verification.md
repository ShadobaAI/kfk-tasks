---
title: Pending Verification
scope: kafka-adapter-ecosystem
type: maintenance
status: partially-verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/project/environment.md"
  - "repo:kafka-adapter-examples:src/Configuration/Configuration.mdo"
  - "repo:kafka-adapter-conv:src/Configuration/Configuration.mdo"
  - "repo:kafka-tools:readme.md"
related:
  - update-process.md
  - ../repositories/kafka-adapter-conv.md
  - ../repositories/kafka-tools.md
---

# Pending Verification

## Summary

- Runtime Kafka and connector behavior was not exercised during foundation analysis.
- The Simple Kafka Connector 1C `1.9.2+` release change was accepted with
  runtime 1C/Kafka checks waived.
- Compatibility with every update in the Conversion Data `3.1+` line is not
  proven.
- Example extension metadata and documented platform baselines differ.
- KFK has 20 non-error EDT diagnostics requiring owner triage.
- `kafka-tools` README paths partially diverge from the checkout.
- Published and local docs are currently equal; local checkout remains the version source.

## Items

| Area | Evidence | Required follow-up |
|---|---|---|
| Connector/runtime | `SPEC-0002` and commit `84dd8f3` verify the `1.9.2+` source, bundle, and docs; runtime was waived | Run validation, atomicity, diagnostics, and end-to-end send/read against supported Kafka/connector versions |
| KFK compatibility | Targets `КД 3.1+`; exact patch is intentionally not stored | Test each claimed supported Conversion Data release |
| Examples version | Platform `8.5.1`, extension `8.3.21`, README `8.3.21+` | Define and align intended baseline |
| KFK diagnostics | 2 major, 18 minor | Review each marker; document accepted exceptions |
| Tools layout | README mentions absent/exactly renamed paths | Align README with `.github/ci-images` checkout |
| Test coverage | UI checkout has three feature files | Compare against intended UI capability coverage |

## Documentation equality

The project owner confirmed on 2026-07-29 that the published site is built from
`adapter/adapter/docs` and currently equals the local documentation. A read-only
spot comparison of repository, architecture, and data-flow pages also found no
material difference.

## Marker

TODO: verification required for runtime- and release-specific claims listed above.
