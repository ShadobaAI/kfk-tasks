# Architecture Decision Records

## Purpose

ADRs record durable architecture decisions and their consequences. IDs are stable and independent of Issues. Do not use ADRs for routine implementation details.

ADR хранит решение, его контекст и последствия как историю выбора. Текущее устройство компонента и инструкции по работе с ним поддерживаются в документации репозитория-владельца. При реализации решения обновляются оба документа по их назначению: ADR не копирует эксплуатационное описание, а документация не пересказывает историю выбора.

## Lifecycle

```text
proposed -> accepted -> superseded
proposed -> rejected
```

An accepted ADR is not silently rewritten when the decision changes. Create a new ADR and link both records through `superseded_by`/`supersedes`.

## Index

Новых ADR пока нет. Следующий ID — `ADR-0001`.

For a new decision, copy [the template](template.md).
