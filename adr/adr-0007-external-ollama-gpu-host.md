---
id: ADR-0007
title: Внешняя Ollama на GPU хоста для OpenViking в ВМ
status: accepted
date: 2026-09-16
supersedes: ADR-0006
related_spec: SPEC-0012
---

# Внешняя Ollama на GPU хоста для OpenViking в ВМ

## Контекст

После принятия ADR-0006 пользователь уточнил, что рабочее окружение находится
в Hyper-V ВМ, а RTX 3060 с 12 ГБ VRAM доступна на физическом хосте. Пользователь
развернул там Ollama в Docker, подтвердил GPU execution и сетевую доступность.

## Решение

OpenViking сохраняет единственный Docker runtime. Его provider может быть:

- managed Ollama в том же Compose project;
- явно настроенная внешняя Ollama на GPU хоста через HTTP(S).

Во втором режиме installer не управляет внешним контейнером, не скачивает модели
и не запускает вторую Ollama в ВМ. GPU passthrough в ВМ не требуется. Endpoint
сохраняется в Docker state; проверяются обе модели и реальные запросы из контейнера.
Git sync/MCP остаются на Windows; OpenViking API остаётся доступным только на
loopback ВМ. Windows venv и автоматическая миграция по-прежнему не поддерживаются.

## Следствия

Доступность GPU host становится условием readiness. Firewall хоста ограничивает
доступ из ВМ. Модели обновляет владелец хоста; их фактические digests входят в
runtime state. Смена endpoint меняет конфигурационный digest контейнера, поэтому
Compose применяет новое подключение. Старые volumes автоматически не удаляются.

См. [дополнение к SPEC-0012](../sdd/spec-0012-docker-runtime-addendum.md).
