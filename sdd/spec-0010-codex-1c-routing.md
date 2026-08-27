---
title: Единая маршрутизация разработки 1С через Codex
id: SPEC-0010
type: specification
status: implemented
owner:
created: 2026-08-26
updated: 2026-08-26
github_issue:
affected_repositories:
  - kafka-tools
  - kafka-adapter
  - kafka-adapter-conv
  - kafka-adapter-tests-unit
  - kfk-tasks
affected_components:
  - Codex AGENTS.md
  - Codex skills
  - Codex MCP configuration
  - Codex PreToolUse policy
related_adrs:
  - ADR-0003
tags:
  - specification
  - codex
  - 1c
  - mcp
---

# Единая маршрутизация разработки 1С через Codex

## Краткое описание

В workspace вводится единая асимметричная схема: EDT-MCP является источником истины и единственным writer для 1С, Unica используется только через явный read-only allowlist, v8std является knowledge/policy layer.

## Контекст

Общие Codex-настройки хранятся в `tools/ai`, а EDT endpoints принадлежат конкретным репозиториям. Policy должна обеспечивать единый writer plane, воспроизводимую установку и проверяемые границы MCP.

## Проблема

- Несколько MCP могут представлять разное состояние одного 1С-проекта.
- Unica содержит mutation/runtime tools, которые не должны конкурировать с EDT writer plane.
- Прямое чтение и изменение `src/**` через filesystem создаёт второй source model.
- Общая конфигурация не имеет идемпотентного способа установки и проверки.

## Цель

Сделать policy исполнимой и воспроизводимой: единый набор skills, явные MCP allow/deny rules, repository-local EDT ownership, PreToolUse guard и проверяемая установка общей конфигурации.

## Не входит в задачу

- Изменение 1С-артефактов под `src/**`.
- Запуск или установка EDT, Unica, v8std либо информационных баз.
- Изменение бизнес-логики, публичных API и схем данных продуктов.

## Область изменений

- `kafka-tools`: канонический пакет `ai` — инструкции, skills, MCP policy, guard, installer и документация.
- `kafka-adapter`, `kafka-adapter-conv`, `kafka-adapter-tests-unit`: только repository-local `.codex/config.toml` и связанные инструкции.
- `kfk-tasks`: SPEC и ADR.

## Функциональные требования

1. Любые чтения, semantic navigation, изменения и validation 1С-проекта маршрутизируются через назначенный EDT-MCP; все persistent mutations выполняются только EDT-MCP.
2. Unica доступна только через явный read-only allowlist. Новые tools запрещены по умолчанию.
3. Standards и snippet analysis используют один MCP `v8std` со всеми knowledge tools. По умолчанию настроен `https://ai.v8std.ru/mcp`; пользователь может заменить `mcp_servers.v8std.url` на локальный endpoint. Agent policy не классифицирует и не ограничивает передаваемый код.
4. `git` и `ask_workmate` EDT-MCP запрещены; high-risk EDT tools требуют prompt.
5. PreToolUse guard блокирует известные прямые filesystem обращения к защищённым `src/**` и Unica mutation tools.
6. Managed skills: `1c-routing`, `1c-code-change`, `1c-platform-docs`, `1c-standards`.
7. Установка общей конфигурации идемпотентна, не копирует secrets, сохраняет заменяемые пользовательские файлы в backup и запускается без параметров из канонического layout. Для переноса installer принимает произвольный `WorkspaceRoot`, обнаруживает skills автоматически и подставляет фактические пути hook.
8. После каждой мутации запускаются focused EDT diagnostics изменённых объектов. Диагностики нельзя отключать, подавлять, фильтровать или скрывать. Finding считается подтверждённым дефектом только после проверки в актуальном контексте исходника и метаданных. Оставить finding неисправленным можно только при доказательной классификации как false positive; иначе он остаётся unresolved и включается в результат проверки.
9. Repository-owned Codex configuration хранится как рабочий `.codex/config.toml`; дублирующие `config.toml.example` не используются.

## Нефункциональные требования

- Конфигурация должна соответствовать актуальной схеме Codex и быть пригодной для Windows workspace.
- Общие и project-local ownership boundaries сохраняются.
- Guards считаются дополнительным барьером, а не полной security boundary.
- Обновление Unica не расширяет allowlist автоматически.

## Архитектура и дизайн

Решение закреплено в ADR-0003. `tools/ai` остаётся единственным версионируемым источником общей policy. Project-local файлы содержат только назначенный EDT endpoint и его risk policy.

## План реализации

1. Обновить shared `AGENTS.md`.
2. Заменить skills и добавить точную policy reference.
3. Добавить common MCP config, PreToolUse guard и installer.
4. Сократить repository-local MCP configs до EDT-only и обновить local instructions.
5. Проверить TOML, YAML/frontmatter, hook cases и идемпотентность installer.
6. Записать фактический результат и проверки в эту SDD.

## Совместимость и миграции

- Skills устанавливаются в `$CODEX_HOME/skills`; заменяемые managed directories сохраняются в backup.
- Common MCP block управляется markers в `$CODEX_HOME/config.toml`, не перезаписывая остальные настройки.
- Локальный v8std использует `http://127.0.0.1:8766/mcp`, чтобы не конфликтовать с EDT на `8765`.
- Unica policy предполагает установленный plugin `unica@unica`.

## Проверка

- Парсинг всех изменённых TOML.
- `quick_validate.py` для каждого skill.
- Позитивные и негативные тестовые входы PreToolUse guard.
- Установка в temporary `CODEX_HOME` дважды и сравнение результата.
- `codex mcp list` в temporary `CODEX_HOME`, если доступно.

## Риски

- Hook покрывает поддерживаемые Codex tool paths, но не является абсолютной sandbox boundary.
- При публичном endpoint передаваемые snippets покидают локальную среду; выбор endpoint и ответственность за передаваемые данные принадлежат пользователю.
- Названия tools зависят от фактической MCP surface; обновления требуют явной переклассификации.

## Критерии приёмки

- Project configs содержат назначенный EDT endpoint и его risk policy.
- Unica expose ограничен ровно утверждённым read-only allowlist.
- `v8std` exposes все knowledge tools, включая `v8std_explain_snippet`, и имеет один настраиваемый пользователем URL.
- Попытка filesystem/tool mutation, покрытая guard, получает `permissionDecision=deny`.
- Все четыре managed skills проходят validator и синхронизируются installer.
- Installer повторно выполняется без дублирования managed config.

## Открытые вопросы

Нет blocking questions.

## Результат реализации

- В `tools/ai` создан единый пакет policy: shared `AGENTS.md`, четыре новых skill, common MCP config, `PreToolUse` guard, installer и launcher локального v8std.
- Managed skills и repository-local EDT configs приведены к целевой policy.
- `adapter/adapter` хранит рабочий `.codex/config.toml`; дублирующий example удалён.
- Installer поддерживает zero-argument setup в каноническом layout и перенос пакета `ai/` в произвольное расположение через `-WorkspaceRoot`; protected roots вынесены в `workspace-policy.json`.
- Unica ограничена явным allowlist из 33 read-only tools; все остальные tools блокируются config и guard.
- `v8std` по умолчанию использует публичный endpoint и exposes snippet tool; локальный endpoint выбирается заменой `mcp_servers.v8std.url`.
- Общая policy установлена в пользовательский Codex с backup и без перезаписи неуправляемой части `config.toml`.
- EDT validation policy требует запускать focused diagnostics после каждой мутации, запрещает скрывать findings и разрешает оставить finding неисправленным только при доказательной классификации как false positive.

Выполненные проверки:

- PowerShell parser: installer, launcher, guard и guard tests — без ошибок.
- `quick_validate.py`: все четыре skills валидны; их `openai.yaml` успешно разобраны YAML parser.
- TOML parser: common config, три рабочих repository-local config и установленный пользовательский config валидны; example configs отсутствуют.
- Guard: 6 позитивных/негативных cases пройдены.
- Installer: fresh install, повторный idempotent run, сохранение выбранного пользователем `v8std.url` и запуск скопированного пакета из произвольного пути проверены в temporary workspace/CODEX_HOME; skills обнаружены автоматически, hook получил фактические абсолютные пути.
- Фактический `kfk-edt` прочитан Codex CLI с отключёнными `git` и `ask_workmate`.

Остаётся операционная проверка после перезапуска Codex. Project-local TOML для `conv-edt` и `kfk-unit-edt` валиден, но их загрузка Codex CLI в текущем sandbox не подтверждена из-за project trust/loading context.

## Отклонения от спецификации

Codex не предоставляет документированный отдельный switch для отключения skills установленного plugin Unica. Mutation skills plugin могут оставаться видимыми в каталоге, но их tools недоступны через `enabled_tools` и дополнительно блокируются `PreToolUse` guard. Сам plugin сохранён, поскольку предоставляет требуемый read-only MCP.

## Связанные документы

- [ADR-0003](../adr/adr-0003-edt-authoritative-writer.md)
