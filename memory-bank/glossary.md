---
title: Project Glossary
scope: kafka-adapter-ecosystem
type: glossary
status: verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:docs/glossary.md"
  - "repo:kafka-adapter:docs/project/metadata.md"
related:
  - architecture/overview.md
---

# Project Glossary

## Summary

- Terms preserve original 1C identifiers where translation would be ambiguous.
- Kafka producer/consumer terms map to adapter configuration catalogs.
- Queue names refer to 1C information registers, not Kafka queues.
- `КД` means 1C:Conversion Data.
- `ПОД` and `ПКО` are Conversion Data rule concepts.

## Terms

| Term | Meaning |
|---|---|
| Adapter | The embeddable 1C Kafka subsystem |
| Broker | Kafka cluster connection configured in `кфкБрокеры` |
| Producer | Outgoing adapter configuration in `кфкПродюсеры` |
| Consumer | Incoming adapter configuration in `кфкКонсьюмеры` |
| Outgoing queue | `InformationRegister.кфкИсходящиеСообщения` |
| Incoming queue | `InformationRegister.кфкВходящиеСообщения` |
| Handler | Application BSL transformation method or KD exchange rule |
| KD / `КД` | `1С:Конвертация данных` / 1C:Conversion Data |
| XDTO | 1C XML Data Transfer Objects contract model |
| AsyncAPI | Event-driven API contract used by conversion tooling |
| `ПОД` | Правило обработки данных, data processing rule |
| `ПКО` | Правило конвертации объектов, object conversion rule |
| `ПВХ` | План видов характеристик, characteristic types plan |
| `РС` | Регистр сведений, information register |
| EDT | 1C:Enterprise Development Tools |
| BSP / `БСП` | 1C Standard Subsystems Library |
| FQN | Stable type-qualified 1C metadata identifier |
| Memory Bank | Maintained compact project context in this repository |
| SDD | Specification-Driven Development |
| ADR | Architecture Decision Record |

## Naming rule

Do not translate identifiers such as `кфкИнтеграция`,
`ПравилаКонвертацииОбъектов`, or `СформироватьAsyncAPI`. Add a short English
explanation at first use when it helps a non-Russian reader.

