---
title: Постоянная маршрутизация Codex через EDT-MCP, code-index, BSL LS и v8std
id: SPEC-0011
type: specification
status: implemented
owner:
created: 2026-08-27
updated: 2026-08-27
github_issue:
affected_repositories:
  - kafka-tools
  - kafka-adapter
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-unit
  - kfk-tasks
affected_components:
  - Codex AGENTS.md
  - Codex skills
  - Codex MCP configuration
  - Codex PreToolUse policy
  - code-index daemon configuration
  - code-index MCP compatibility proxy
  - BSL LS MCP proxy
related_adrs:
  - ADR-0004
tags:
  - specification
  - codex
  - 1c
  - mcp
sources:
  - C:/Users/admin/Downloads/code-index-mcp/README_RU.md
---

# Постоянная маршрутизация Codex через EDT-MCP, code-index, BSL LS и v8std

## Краткое описание

Unica полностью выводится из активной Codex-интеграции. Постоянная схема состоит из authoritative EDT-MCP, общего read-only `code-index`, опционального repository-local BSL LS и общего `v8std`.

## Контекст

SPEC-0010 внедрила асимметричную схему с EDT-MCP как единственным writer и Unica как supplementary read-only layer. Unica RLM не поддерживает Windows. Локальная копия `code-index` подтверждает Windows-сборку `bsl-indexer`, read-only MCP `serve`, отдельный daemon-индексатор и BSL-специфичные индексы. В `kafka-adapter` ранее применялся BSL LS MCP proxy, устраняющий проблемы roots и путей с кириллицей.

## Проблема

- Активная Unica-зависимость делает общий workflow непереносимым на Windows.
- `code-index serve` сам не индексирует: без единого daemon и общего `CODE_INDEX_HOME` MCP возвращает только состояние `daemon_offline`.
- BSL LS требует корректный repository root, JAR и локальную analyzer-конфигурацию; он не заменяет метаданные и live model EDT.
- Простая замена названий MCP могла бы создать неявный второй источник истины либо разрешить новые tools без классификации.

## Цель

Сохранить единый writer plane и стиль текущего managed-пакета, заменить Unica постоянным Windows-совместимым read-only analysis plane и сделать его установку, allowlist, prerequisites и ограничения проверяемыми.

## Не входит в задачу

- Изменение 1С-артефактов под `src/**`.
- Вендоринг или сборка сторонних бинарников `bsl-indexer` и BSL Language Server.
- Автоматическая установка фонового процесса или Scheduled Task без отдельного решения пользователя.
- Изменение правил анализатора `.bsl-language-server.json`.
- Построение рёбер для динамических вызовов, где имя процедуры передаётся строкой или вычисляется во время выполнения.

## Область изменений

- `kafka-tools`: общая policy, skills, MCP config, code-index launcher/daemon template, installer, guard, tests и документация.
- `kafka-adapter`: repository-local BSL LS proxy/config и инструкции.
- `kafka-adapter-base`, `kafka-adapter-examples`, `kafka-adapter-conv`, `kafka-adapter-tests-unit`: федеративные aliases общего code-index; локальные инструкции меняются только где содержат Unica.
- `kfk-tasks`: новая SDD и superseding ADR.

## Функциональные требования

1. EDT-MCP остаётся источником истины, единственным writer и primary diagnostics gate.
2. Общий `code-index` предоставляет только явно перечисленные read-only tools. Его daemon пишет только собственные `.code-index/` данные вне 1С `src/**` и coordination/runtime в `CODE_INDEX_HOME`; MCP `serve` является read-only reader.
3. `code-index` обслуживает отдельные aliases канонических репозиториев и не разрешает агенту подменять целевой alias соседним проектом.
4. При расхождении или stale index доверенным считается EDT; состояние индекса должно проверяться через `health`.
5. BSL LS используется только в репозитории с явной MCP-конфигурацией и analyzer-конфигурацией, только для focused diagnostics/semantic navigation. Он не заменяет EDT validation.
6. BSL LS proxy проверяет root и входной файл, ограничивает файл root-ом, поддерживает Windows-пути с кириллицей и получает JAR через явный параметр либо `BSL_LANGUAGE_SERVER_JAR`.
7. Unica отсутствует в активном config, skills, policy, hook и текущих AGENTS. Installer удаляет конфликтующую legacy Unica MCP table при миграции managed block.
8. `$1c-routing` активируется только для работы с конкретным 1С-проектом либо общего вопроса про 1С, а не для любого запроса workspace.
9. `v8std` сохраняет текущий пользовательский endpoint и роль standards/policy corpus.
10. Новые tools `code-index` и BSL LS запрещены по умолчанию до явной переклассификации allowlist.
11. Рабочий Windows runtime `bsl-indexer` обновляется с `0.67.0` до `0.69.0`; после обновления выполняется полный принудительный разбор всех управляемых aliases, потому что формат имён вызываемых функций в графе изменился.
12. Для BSL-графа предоставляются отдельные read-only tools `get_callers_bsl`, `get_callees_bsl` и `get_call_tree_bsl`, использующие `proc_call_graph`. Универсальные `get_callers`, `get_callees` и `get_call_tree` сохраняются без изменения контракта.
13. Ответы новых BSL-tools явно сообщают источник графа, неоднозначность адресации, число разрешённых и неразрешённых рёбер, обрезку и ограничения покрытия. Пустой ответ не объявляется доказательством отсутствия динамических вызовов.

## Нефункциональные требования

- Решение работает на Windows и fail-fast сообщает об отсутствующем runtime.
- Общий package не содержит сторонние binaries, secrets и машинно-зависимые пользовательские credentials.
- Индексы размещаются в исключённых из Git `.code-index/` каталогах repository roots; логи и daemon coordination/runtime — в managed `CODE_INDEX_HOME`. Ничего не записывается в 1С `src/**`.
- Hooks остаются defense-in-depth, а не полной security boundary.

## Архитектура и дизайн

```text
                         +--> v8std (standards/policy)
Codex --> routing -------+--> code-index MCP (read-only index/search/graphs)
   |                     +--> BSL LS MCP (focused secondary BSL evidence)
   +------------------------> repository EDT-MCP (authoritative read/write/validate)

bsl-indexer daemon (single writer) --> repository .code-index/ + CODE_INDEX_HOME runtime
code-index MCP serve (read-only) ----> same indexes/runtime identity
```

Общий `tools/ai` владеет federated `code-index`, daemon template, allowlist, hook и skills. Repository-local config продолжает владеть EDT endpoint. BSL LS остаётся repository-local, потому что его root и analyzer-конфигурация принадлежат конкретному проекту.

Три BSL-инструмента реализуются тонким repository-owned stdio proxy над штатным `bsl-indexer serve`. Proxy расширяет `tools/list`, преобразует вызовы named-tools в ограниченные параметризованные read-only запросы `bsl_sql` к `proc_call_graph` и нормализует ответ. Такая реализация не меняет схему `.code-index`, не предоставляет произвольную запись и сохраняет upstream runtime заменяемым.

## План реализации

1. Зафиксировать ADR-0004 и пометить ADR-0003 superseded.
2. Удалить Unica из managed config, guard, skills и текущих инструкций.
3. Добавить общий `code-index` launcher, daemon template, explicit allowlist и installer migration.
4. Восстановить и усилить BSL LS proxy для `kafka-adapter`, добавить local MCP allowlist.
5. Добавить skills маршрутизации `1c-code-index` и `bsl-ls-mcp`, сузить trigger `$1c-routing`.
6. Обновить tests, выполнить парсинг, validators, hook и installer checks.
7. Установить managed policy; runtime запускать только при наличии внешних binaries.
8. Обновить runtime до `0.69.0`, принудительно пересобрать индексы и проверить новые BSL-tools через MCP.

## Совместимость и миграции

- Legacy managed block заменяется идемпотентно. Unmanaged legacy Unica table удаляется только с `-ReplaceConflictingCommonMcp` и backup.
- `v8std.url` сохраняется.
- `bsl-indexer.exe` ожидается в `<CODE_INDEX_HOME>/bsl-indexer.exe` либо по `BSL_INDEXER_EXE`/`PATH`.
- BSL LS JAR ожидается по `BSL_LANGUAGE_SERVER_JAR`, явному `--jar`, в repository root либо `<CODEX_HOME>/bsl-ls`.
- После изменения MCP/skills требуется перезапуск Codex.

## Проверка

- TOML/YAML/frontmatter parsing.
- `quick_validate.py` для всех managed skills.
- Позитивные и негативные hook cases для code-index, BSL LS, EDT и filesystem.
- Unit checks launchers/proxy без запуска стороннего runtime.
- Fresh, migration и повторная portable установка в temporary `CODEX_HOME`.
- Runtime smoke checks только если binaries фактически доступны.
- Proxy unit checks: расширение `tools/list`, параметризованный SQL, callers/callees/tree, неоднозначность, truncation и ошибка upstream.

## Риски

- Индекс является eventually consistent и может отставать от EDT.
- Один federated MCP технически видит несколько repositories; routing policy обязана фиксировать alias задачи.
- BSL LS coverage зависит от локальной analyzer-конфигурации, версии JAR и поддерживаемых MCP tools.
- `code-index` BSL tools доступны только в `bsl-indexer`, а публичный npm `code-index` недостаточен для полной 1С-функциональности.
- Без запущенного daemon `code-index serve` не выполняет индексацию.

## Критерии приёмки

- В активных policy/config/skills/AGENTS нет зависимости от Unica.
- EDT остаётся единственным writer; прямой filesystem доступ к 1С `src/**` блокируется.
- `code-index` и BSL LS ограничены явными read-only allowlists и guard default-deny.
- Общая установка создаёт согласованные `CODE_INDEX_HOME/daemon.toml` и MCP args с одинаковыми aliases/paths.
- BSL LS proxy проходит targeted tests root/path/argument processing.
- Все managed skills валидны, включая суженный trigger `$1c-routing`.
- Installer остаётся идемпотентным и сохраняет пользовательский `v8std.url`.
- Runtime `bsl-indexer --version` сообщает `0.69.0`; после полного reindex все aliases возвращаются в `ready`.
- Фактическая MCP surface содержит 34 разрешённых read-only tools, включая `get_callers_bsl`, `get_callees_bsl`, `get_call_tree_bsl`.
- BSL routing использует новые tools вместо универсального графа; пустой ответ содержит явные coverage limitations.

## Открытые вопросы

Нет blocking questions. Наличие сторонних binaries является операционным prerequisite и проверяется отдельно.

## Результат реализации

- Unica удалена из managed MCP config, current skills, hook и текущих AGENTS. Legacy `[marketplaces.unica]`, `[plugins."unica@unica"]` и nested MCP tables удаляются installer с backup; в установленном `%USERPROFILE%\.codex\config.toml` совпадений `unica` нет. Codex plugin removal завершён через Plugin Management.
- Общий `code-index` установлен как federated read-only MCP. `serve` получает managed `daemon.toml`, поэтому фактическая MCP surface содержит 31 tool: 20 core и 11 BSL.
- Один скрытый `bsl-indexer` daemon обслуживает aliases `kafka-adapter`, `kafka-adapter-base`, `kafka-adapter-examples`, `kafka-adapter-conv`, `kafka-adapter-tests-unit`; все пять paths имеют status `ready`.
- В корнях всех индексируемых repositories `.code-index/` исключён из Git. Coordination/log runtime использует `%USERPROFILE%\.codex\code-index`.
- Для `kafka-adapter` восстановлен и усилен BSL LS proxy: явный root, roots/list workaround, проверка file-аргумента внутри root, Windows short-path bridge для кириллицы и переносимый поиск JAR. Фактическая MCP surface содержит 10 read-only tools; outside-root smoke получил JSON-RPC `-32602`.
- Установлен и проверен BSL Language Server `1.0.7` (`SHA256 9F62765EDD344D66456DA24C906EAF623A03C56E90E5AAFEE466200100909F64`).
- `bsl-indexer` обновлён официальным Windows artifact до `0.69.0` (`SHA256 E33117F8438A9A0CF526BA1574731CDB85FF5793AEFA85F1056FFA656EE28A66`); предыдущий `0.67.0` сохранён отдельным backup в managed `CODE_INDEX_HOME`.
- После обновления выполнен `index --force` для всех пяти aliases. Графы пересобраны полностью: `kafka-adapter` — 2 763 ребра, `kafka-adapter-base` — 28 262, `kafka-adapter-examples` — 89, `kafka-adapter-conv` — 443, `kafka-adapter-tests-unit` — 307.
- Добавлен managed stdio proxy с read-only tools `get_callers_bsl`, `get_callees_bsl`, `get_call_tree_bsl`. Они выполняют только параметризованные `SELECT/WITH` через штатный `bsl_sql` по `proc_call_graph`; upstream generic tools и схема индекса не изменены.
- Новые BSL-tools возвращают `coverage`: источник, полноту в заданных пределах, разрешённые/неразрешённые рёбра, неоднозначность цели, truncation, depth boundary и явное ограничение по динамическим вызовам.
- `$1c-routing` сужен до запросов о конкретном 1С-проекте либо общих вопросов по 1С. Добавлены managed skills `1c-code-index` и `bsl-ls-mcp`.
- Installer синхронизировал user config, шесть skills, root `AGENTS.md` и `CODE_INDEX_HOME/daemon.toml`; backups созданы под `%USERPROFILE%\.codex\backups\workspace-ai`.

Выполненные проверки:

- PowerShell parser: installer, guard и два code-index launchers — без ошибок; `node --check` BSL LS proxy — без ошибок.
- TOML parser: shared config, три repository-local configs и daemon template — 5 файлов успешно разобраны.
- `quick_validate.py`: все 6 managed skills валидны.
- Guard: 8 allow/deny cases пройдены для filesystem, code-index, BSL LS и v8std.
- Installer: portable paths, code-index config, idempotent v8std URL preservation и полная Unica migration — пройдены.
- code-index launcher unit test — согласованные executable, `CODE_INDEX_HOME` и `daemon.toml`.
- Runtime MCP smoke: code-index `tools/list` = 31, `health` = online/ok, все 5 repositories `ready`; BSL LS `tools/list` = 10; proxy outside-root denial проверен.
- После обновления runtime MCP smoke: `tools/list` = 34; `get_callers_bsl('ЗапуститьПотоки')` вернул 2 разрешённых статических ребра, включая 1 межмодульное; `get_callees_bsl` — 7 рёбер; caller tree — 2 ребра. Daemon `0.69.0`, все 5 repositories `ready`.
- Новый proxy unit test проверяет расширение `tools/list`, callers/callees/tree, coverage, depth boundary и отказ на некорректных аргументах; runtime smoke проверяет все три новых tools на реальном индексе.
- `codex mcp list` из `kafka-adapter` показывает `kfk-edt`, `code-index`, `bsl-ls`, `v8std` и не показывает Unica.

Для появления обновлённой surface в уже открытых задачах требуется перезапуск Codex Desktop. Автозапуск daemon после перезагрузки Windows намеренно не устанавливался; до отдельного решения он запускается `tools/ai/mcp/code-index-daemon.ps1 -Action run`.

## Отклонения от спецификации

- BSL LS при команде `version` на текущей Java печатает upstream warning о deprecated `sun.misc.Unsafe`; версия и MCP startup завершаются успешно.

## Связанные документы

- [ADR-0004](../adr/adr-0004-code-index-bsl-ls-analysis-plane.md)
- [SPEC-0010](spec-0010-codex-1c-routing.md)
