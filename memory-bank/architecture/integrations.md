---
title: Integration Boundaries
scope: kafka-adapter-ecosystem
type: architecture
status: partially-verified
updated: 2026-07-29
components:
  - kafka
  - connector
  - conversion-data
  - logging
  - notifications
sources:
  - "repo:kafka-adapter:docs/overview/about.md"
  - "repo:kafka-adapter:docs/user/development/conversion-data.md"
  - "repo:kafka-tools:readme.md"
related:
  - overview.md
  - ../repositories/kafka-adapter-conv.md
---

# Integration Boundaries

## Summary

- Apache Kafka is reached only through Simple Kafka Connector 1C.
- The adapter release baseline for Simple Kafka Connector 1C is `1.9.2+`.
- Application payload transformation is either custom BSL or Conversion Data 3.1.
- XDTO is the contract mechanism for Conversion Data paths.
- External operational logging supports ELK/OpenSearch-style HTTP ingestion.
- Telegram alerts are documented for integration-control thresholds.
- Tooling supplies local Kafka, logging, database, and Sonar environments.

## Kafka boundary

`DataProcessor.кфкИнтеграция` owns connector creation, producer/consumer
sessions, direct send/read, and Kafka transaction operations. Connector and
librdkafka versions are external compatibility surfaces. `SPEC-0002` upgraded
the embedded connector baseline to `1.9.2+`; runtime behavior was waived for
that release and remains pending verification.

## Host-application boundary

The host provides business objects and transformation handlers. Automatic event
subscriptions observe supported writes/deletes, while producer configuration
filters actual participation.

Incoming handlers must avoid re-registering the same business write as an
outgoing event. The public API provides `Отключить`; documented application code
also uses the standard exchange-loading flag when appropriate.

## Conversion Data boundary

The adapter calls generated exchange-manager contracts. `kafka-adapter-conv`
customizes Conversion Data 3.1 so arbitrary XDTO can replace an EnterpriseData-
only contract and adds an AsyncAPI-oriented specification workspace.

The extension targets Conversion Data `3.1+`. The exact patch version is not
stored because the base is updated regularly. Compatibility across updates in
that line must be verified by the conversion extension's tests.

## Operational integrations

| Boundary | Purpose | Evidence status |
|---|---|---|
| Kafka cluster | Message transport | Connector `1.9.2+` verified in source/bundle/docs; runtime not exercised here |
| ELK / OpenSearch | External history logs | Documented and tooling present |
| Telegram | Threshold alerts | Documented; credentials/runtime not inspected |
| SonarQube | Static BSL analysis | Tooling present |
| Allure | Unit/UI report publication | Published report repository present |

## Security considerations

Broker credentials, TLS files, external logging endpoints, alert tokens, and
database credentials are deployment secrets. They must not enter the Memory
Bank or committed local configuration.
