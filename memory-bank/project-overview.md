---
title: Kafka Adapter Project Overview
scope: kafka-adapter-ecosystem
type: overview
status: verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/overview/about.md"
  - "repo:kafka-adapter:docs/overview/principles.md"
  - "repo:kafka-adapter:docs/overview/architecture.md"
related:
  - repositories.md
  - architecture/overview.md
---

# Kafka Adapter Project Overview

## Summary

- Kafka Adapter is an embeddable 1C subsystem for bidirectional Kafka exchange.
- It separates application handlers from transport, queueing, retry, and monitoring.
- Outgoing and incoming work is persisted in 1C information registers.
- Background jobs provide asynchronous and parallel processing.
- Serialization is custom BSL or Conversion Data 3.1 plus XDTO.
- Low-level Kafka access is delegated to Simple Kafka Connector 1C.
- The ecosystem separates product, host, examples, tests, reports, conversion, and tools.

## Purpose

The adapter gives a 1C application a managed integration layer without requiring
the application to implement Kafka transport. It supports automatic and direct
registration, custom or Conversion Data handlers, persistent queues, background
processing, diagnostics, external logging, and administration.

## Runtime boundaries

The adapter owns:

- broker, producer, and consumer configuration;
- outgoing and incoming queue records;
- dispatch and background-worker coordination;
- transport calls through the external component;
- status, retry, deduplication, and idempotency state;
- administration and operational diagnostics.

The host application owns:

- business events and objects;
- message contracts;
- custom serialization/deserialization handlers;
- application-side idempotency and transactional business behavior.

Apache Kafka and its cluster operations are external to the 1C subsystem.

## Primary constraints

- Client-server 1C infobases are documented as required.
- Adapter compatibility metadata is `8.3.21`; Linux documentation raises the
  runtime platform floor to `8.3.24`.
- The documented BSP baseline is `3.1.10+`.
- Message and tabular-section practical limits are documented, not enforced by
  this Memory Bank; verify them against the current implementation before
  changing capacity assumptions.
- Registration errors are designed not to interrupt a user's object write.
- Delivery and application handlers must still be designed for retries.

## Ecosystem boundary

All stable project knowledge, SDD, ADRs, and the Memory Bank MCP live in
`kfk-tasks`. Business logic remains in its owning repositories.

## Evidence note

Published repository, architecture, and data-flow pages were loaded on
2026-07-29 and spot-compared with the local checkout. Their material content
matched; the local Markdown remains authoritative for this checkout.

