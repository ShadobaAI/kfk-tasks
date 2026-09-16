---
id: ADR-0006
title: Docker-only runtime для OpenViking и Ollama
status: superseded
superseded_by: ADR-0007
date: 2026-09-16
related_spec: SPEC-0012
---

# Docker-only runtime для OpenViking и Ollama

## Контекст

Windows bootstrap OpenViking выявил проблемы native quoting, перемещения Python
venv и совместимости Python-зависимостей. Пользователь утвердил переход на Docker
и исключил обратную совместимость в дополнении к SPEC-0012.

## Решение

OpenViking и Ollama работают как отдельные Linux services одного Docker Compose
project. Только OpenViking API публикуется на loopback Windows. Данные и модели
сохраняются в отдельных volumes; конфигурация и локальный API key находятся вне Git.
Git sync, hooks и read-only MCP остаются на Windows и взаимодействуют по HTTP.
Windows venv bootstrap и его параметры удаляются без автоматической миграции.

Сохраняется latest-stable policy OpenViking: версия пакета внутри официального
образа должна совпасть с разрешённым стабильным release; deployment использует
фактический image digest. Поддержка native mode не входит в архитектуру.

## Следствия

Для запуска обязателен Docker Desktop с Linux containers. Ресурсы моделей делятся
с другими контейнерами; GPU проверяется отдельно. Отсутствие модели или semantic
readiness блокирует установку. Static/mock tests не заменяют live-проверку.
Перезапуск сохраняет volumes; удаление данных и автоматический downgrade исключены.
Ранее установленное Windows-окружение не используется и автоматически не удаляется.

## Основание

[Утверждённое дополнение к SPEC-0012](../sdd/spec-0012-docker-runtime-addendum.md).
