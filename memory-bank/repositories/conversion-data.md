---
title: Conversion Data 3.1 Base Configuration
scope: conversion-data
repository: conversion-data
type: repository
status: verified
updated: 2026-07-29
components:
  - conversion-data
sources:
  - "repo:conversion-data:src/Configuration/Configuration.mdo"
  - "repo:conversion-data:Catalog.ПравилаКонвертацииОбъектов"
  - "repo:conversion-data:CommonModule.КонвертацияДанныхXDTOСервер"
related:
  - kafka-adapter-conv.md
---

# Conversion Data 3.1 Base Configuration

## Summary

- This is the local base for the `KFK` extension.
- EDT project and configuration name are `КД` / `КонвертацияДанных`.
- Target compatibility line is `3.1+`; the exact patch version is intentionally
  not stored because the base is updated regularly.
- Compatibility metadata is `8.3.24`.
- Analysis is limited to attachment points required by `KFK`.
- The directory is not a Git repository in this workspace.

## Relevant attachment points

The extension adopts rule catalogs, exchange processors, selected enums, and
`CommonModule.КонвертацияДанныхXDTOВызовСервера`. The base
`Catalog.ПравилаКонвертацииОбъектов` contains the standard conversion rule
attributes and forms that `KFK` extends.

## Scope limitation

This Memory Bank does not describe the full architecture of Conversion Data.
Use `conv_edt` for a bounded object/module inspection when a `KFK` change
touches an adopted base object.

## Compatibility

The inspected attachment demonstrates compatibility with one local checkout,
not every `3.1+` release. Adopted metadata and borrowed form paths are the
highest-risk upgrade points.
