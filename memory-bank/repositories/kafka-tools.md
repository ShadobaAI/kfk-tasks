---
title: kafka-tools Repository
scope: kafka-tools
repository: kafka-tools
type: repository
status: partially-verified
updated: 2026-07-29
components:
  - local-infrastructure
  - ci
  - xsd-generation
sources:
  - "repo:kafka-tools:readme.md"
  - "repo:kafka-tools:kafka/docker-compose.yml"
  - "repo:kafka-tools:xdto/asyncapi2xsd.py"
  - "repo:kafka-tools:.github/workflows/release-1c-artifacts.yml"
related:
  - kafka-adapter.md
  - ../development/testing.md
---

# kafka-tools Repository

## Summary

- This repository supplies local Kafka and observability environments.
- It contains CI image/release actions and Python conversion utilities.
- Kafka runs as a two-node KRaft development cluster.
- ELK and OpenSearch are alternative external logging stacks.
- SonarQube tooling supports local/static BSL analysis.
- `asyncapi2xsd.py` generates XSD for XDTO import.
- README path names do not fully match the current checkout.

## Responsibility

Provide operationally separate development and release tooling. Product runtime
must not depend on this repository being present after deployment.

## Current areas

| Area | Current path |
|---|---|
| Kafka | `kafka/` |
| ELK | `elk/` |
| OpenSearch | `opensearch/` |
| MS SQL | `mssql/` |
| SonarQube | `sonarqube/` |
| AsyncAPI to XSD | `xdto/asyncapi2xsd.py` |
| CI images/actions/workflows | `.github/` |

## Documented conflict

The README describes a `docker-image/` layout and some script names that are not
present under those exact paths in the current checkout; CI image material is
under `.github/ci-images/`. Verify and update the owning README before relying
on copied commands.

## Security

Examples include local credentials and token setup instructions. Treat them as
development defaults only; never copy secrets or machine paths into canonical
project knowledge.

