---
title: kafka-adapter-conv Repository
scope: kafka-adapter-conv
repository: kafka-adapter-conv
type: repository
status: partially-verified
updated: 2026-07-29
components:
  - conversion-data
  - asyncapi
  - xdto
sources:
  - "repo:kafka-adapter-conv:README.md"
  - "repo:kafka-adapter-conv:src/Configuration/Configuration.mdo"
  - "repo:kafka-adapter-conv:DataProcessor.кфкКонструкторAsyncAPI"
related:
  - conversion-data.md
  - ../architecture/integrations.md
---

# kafka-adapter-conv Repository

## Summary

- This extension customizes Conversion Data 3.1 for arbitrary XDTO.
- EDT project name is `KFK`; metadata extension name is `АдаптерKafka`.
- Extension compatibility metadata is `8.3.24`.
- It adopts selected Conversion Data objects and adds `кфк*` specification objects.
- `DataProcessor.кфкКонструкторAsyncAPI` exports AsyncAPI generation.
- Current EDT diagnostics report 2 major and 18 minor non-error findings.

## Responsibility

Provide authoring support for integration contracts and generated exchange
logic used by the adapter's Conversion Data handler path. It does not implement
Kafka transport.

## Extension attachment

EDT verified adopted core objects such as
`Catalog.ПравилаКонвертацииОбъектов`. The extension adds
attribute `кфкТабличнаяЧасть` to that object and adopts its form. The matching
base object is visible through the `КД` project.

## Added model

The extension includes:

- specifications and version documents/registers;
- channels, applications, examples, enums, and data types;
- change-history registers;
- AsyncAPI constructor processing and workbench forms.

## Entry point

`DataProcessor.кфкКонструкторAsyncAPI.ManagerModule.СформироватьAsyncAPI`
is the verified exported generation function. Internal helpers construct
channels, operations, messages, schemas, enums, history, and naming templates.

## Risks

- Поддерживаемая линия — `КД 3.1+`; точная версия базы намеренно не
  фиксируется, так как она регулярно обновляется.
- KFK diagnostics include form data-path and form-structure recommendations.
- Adopted-object compatibility can change with Conversion Data updates.
