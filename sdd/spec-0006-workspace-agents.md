---
title: Общие инструкции мультирепозитория
id: SPEC-0006
type: specification
status: verified
owner:
created: 2026-08-03
updated: 2026-08-03
github_issue:
affected_repositories:
  - kafka-adapter
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-reports
  - kafka-adapter-tests-ui
  - kafka-adapter-tests-unit
  - kafka-tools
  - kfk-tasks
affected_components:
  - workspace-agent-instructions
  - repository-agent-instructions
related_adrs: []
tags:
  - specification
  - agents
sources:
  - "repo:kfk-tasks:sdd/spec-0004-adapter-agents-pilot.md"
  - "repo:kfk-tasks:sdd/spec-0005-repository-agents-rollout.md"
---

# Общие инструкции мультирепозитория

## Краткое описание

- Создать обязательный общий англоязычный `AGENTS.md` в корне мультирепозитория.
- Перенести в него общие правила из восьми локальных `AGENTS.md`.
- В локальных файлах оставить относительную ссылку на общий файл и только repository-specific instructions.
- Считать структуру каталогов под `KAFKA_PROJECTS_ROOT` фиксированной частью требований разработки проекта.

## Контекст

Рабочая структура `C:\EDT\projects\kafka\*` фиксирована проектными требованиями. В документации и инструкциях используется переносимый идентификатор `KAFKA_PROJECTS_ROOT`, а не абсолютный локальный путь. Все восемь Git-репозиториев располагаются по известным относительным путям, поэтому локальные `AGENTS.md` могут обязательно ссылаться на один общий файл в корне workspace.

Пилот и первый rollout создали самодостаточные локальные файлы. После уточнения требований эта модель заменяется централизованной: общие правила хранятся один раз, локальные файлы описывают только роль и исключения репозитория.

## Проблема

Повторение SDD/ADR workflow, bounded navigation, network, safety и общих правил проверки во всех локальных файлах усложняет сопровождение и создаёт риск расхождений. Фиксированная workspace topology позволяет устранить дублирование.

## Цель

Сделать `KAFKA_PROJECTS_ROOT/AGENTS.md` обязательным каноническим источником общих agent instructions, а восемь локальных файлов — компактными дополнениями со ссылкой на общий файл.

## Не входит в задачу

- Не поддерживать standalone clone вне утверждённой структуры каталогов.
- Не удалять или переносить Memory Bank, SDD либо ADR.
- Не создавать `AGENTS.md` в `conversion/КД`, `tests/unit` или других каталогах.
- Не изменять исходники, тесты, generated reports, tooling, CI или product documentation.

## Фиксированная структура

Все пути указаны относительно `KAFKA_PROJECTS_ROOT`:

| Репозиторий | Канонический путь | Ссылка на общий файл |
|---|---|---|
| `kafka-adapter` | `adapter/adapter` | `../../AGENTS.md` |
| `kafka-adapter-base` | `adapter/base` | `../../AGENTS.md` |
| `kafka-adapter-examples` | `adapter/examples` | `../../AGENTS.md` |
| `kafka-adapter-conv` | `conversion/KFK` | `../../AGENTS.md` |
| `kafka-adapter-tests-reports` | `tests/reports` | `../../AGENTS.md` |
| `kafka-adapter-tests-ui` | `tests/ui` | `../../AGENTS.md` |
| `kafka-adapter-tests-unit` | `tests/unit/unit` | `../../../AGENTS.md` |
| `kafka-tools` | `tools` | `../AGENTS.md` |

`conversion/КД` — локальная supporting base configuration, не Git-репозиторий. `tests/unit/unit` — канонический корень unit-test repository; `tests/unit` им не является.

## Область изменений

Создать:

- `KAFKA_PROJECTS_ROOT/AGENTS.md`.

Изменить:

- `adapter/adapter/AGENTS.md`;
- `adapter/base/AGENTS.md`;
- `adapter/examples/AGENTS.md`;
- `conversion/KFK/AGENTS.md`;
- `tests/reports/AGENTS.md`;
- `tests/ui/AGENTS.md`;
- `tests/unit/unit/AGENTS.md`;
- `tools/AGENTS.md`;
- эту SDD — только для статуса, результата и проверок.

## Функциональные требования

### Общий `AGENTS.md`

- Написать файл на английском языке в UTF-8.
- Определить workspace как фиксированный набор независимых Git-репозиториев под `KAFKA_PROJECTS_ROOT`.
- Привести карту канонических repository roots.
- Требовать определить затронутый репозиторий и прочитать его локальный `AGENTS.md` до анализа или изменений.
- Зафиксировать приоритет: инструкции пользователя, затем локальный `AGENTS.md`, затем общий `AGENTS.md`.

Общий файл должен содержать единый набор правил:

- запрет рекурсивного сканирования всего workspace или repository;
- bounded navigation, узкие result limits и запрос каталога/файла у пользователя, когда расположение неизвестно;
- запрет изменения нескольких репозиториев без явно заданного multi-repository scope или утверждённого SDD;
- SDD на русском языке;
- обязательный approved SDD для нетривиального поведения, public API, data schema и multi-repository changes;
- разрешение создать `draft` и запрет реализации до явного утверждения пользователя;
- ADR только для долгосрочных architecture decisions и component boundaries;
- documentation duties и фиксацию result/checks/deviations в SDD;
- прямое редактирование не-1С файлов в UTF-8 с сохранением existing style;
- запрет прямого изменения любых 1С-файлов в `src/**`;
- ошибка и остановка 1С-изменений при недоступности назначенного EDT MCP;
- использование `SyntaxCheckServer`, `HelpSearchServer` и `v8std` при решении задач 1С;
- `v8std` как базовый стандарт и project source style в допустимых вариантах;
- focused EDT diagnostics и эскалацию к пользователю, если diagnostic не устранён за одну correction iteration;
- запуск релевантных YAxUnit/UI tests при доступном environment;
- запрет ручного изменения generated artifacts;
- запрет destructive operations без явного разрешения;
- сохранение unrelated user changes;
- запрет чтения, вывода и commit secrets, tokens, credentials и personal configuration;
- запрет любого скачивания из глобального интернета свыше 100 MB или неизвестного размера без явного разрешения пользователя;
- разрешение использовать local cache;
- обязательный отчёт о выполненных и недоступных проверках.

Общий файл должен содержать MCP routing table:

| Scope | Editing/current-state MCP | Дополнительная навигация |
|---|---|---|
| `adapter/adapter` | `kfk_edt` | `code-metadata-mcp`, `graph-metadata-mcp` |
| `adapter/base` | `kfk_edt` | только `kfk_edt` |
| `adapter/examples` | `kfk_edt` | только `kfk_edt` |
| `conversion/KFK` | `conv_edt` | только `conv_edt` |
| `tests/unit/unit` | `kfk-unit-edt` | только `kfk-unit-edt` |

`code-metadata-mcp` и `graph-metadata-mcp` используются только для навигации по `adapter/adapter`; актуальная информация и изменения всегда идут через `kfk_edt`.

### Локальные `AGENTS.md`

Каждый локальный файл должен:

- начинаться с раздела `Workspace Instructions`;
- содержать обязательную относительную Markdown-ссылку на общий `AGENTS.md`;
- требовать прочитать общий файл до выполнения задачи;
- считать отсутствие общего файла ошибкой структуры workspace и сообщать её пользователю;
- явно указывать, что локальные repository-specific rules дополняют общий файл и имеют над ним приоритет при конфликте;
- содержать только repository role, canonical local documentation links и repository-specific routing/editing/validation/safety rules;
- не повторять общий SDD/ADR workflow, network limit, generic bounded-navigation rules, generic secret policy и generic completion rules.

### Repository-specific content

- `adapter/adapter`: product/library role, local documentation, `кфк` prefix, разрешение `code-metadata-mcp`/`graph-metadata-mcp` только для navigation, `kfk_edt` как current state.
- `adapter/base`: BSP host role, только `kfk_edt`.
- `adapter/examples`: development-only examples role, только `kfk_edt`, prefix `кфк_т_`.
- `conversion/KFK`: Conversion Data/XDTO role, только `conv_edt`, `conversion/КД` только supporting base вне repository scope.
- `tests/reports`: generated-only role, запрет ручного изменения `latest/`, run directories, Allure и Sonar output; editable scope только publication documentation/configuration по явной задаче.
- `tests/ui`: Vanessa Automation role, прямое UTF-8 редактирование feature/config files, focused scenario validation, отсутствие product-source changes без multi-repository scope.
- `tests/unit/unit`: YAxUnit role, только `kfk-unit-edt` для `src/**`, assembly scripts как direct-edit non-1C files, focused YAxUnit validation.
- `tools`: infrastructure/tooling role, component-scoped navigation/validation, запрет долгоживущих services без необходимости, explicit confirmation для `down -v`, `prune`, volume/database deletion и restore, `.env` не читать и не выводить.

## Нефункциональные требования

- Все `AGENTS.md` написаны на английском языке и в UTF-8.
- Общий файл остаётся достаточно кратким для чтения в начале каждой задачи.
- Локальные файлы существенно короче текущих и не дублируют общие правила.
- Используются только относительные пути и `KAFKA_PROJECTS_ROOT`; абсолютный локальный путь не сохраняется.
- Не добавлять ссылки на Memory Bank.

## План реализации

1. Создать общий `AGENTS.md` с общей картой, workflow, MCP routing и safety rules.
2. Переписать восемь локальных файлов, заменив общий текст обязательной ссылкой.
3. Сохранить в каждом локальном файле только repository-specific content.
4. Проверить разрешение каждой ссылки до общего файла.
5. Проверить UTF-8, Markdown headings, отсутствие common-rule duplication и ссылок на Memory Bank.
6. Проверить Git status восьми репозиториев: изменён только `AGENTS.md`.
7. Зафиксировать результат и проверки в этой SDD.

## Совместимость и миграции

После изменения работа вне фиксированной структуры `KAFKA_PROJECTS_ROOT` не поддерживается. Отсутствующий общий `AGENTS.md` считается ошибкой development environment. Это осознанный trade-off ради единого сопровождаемого набора правил.

Удаление Memory Bank и перенос существующих SDD/ADR остаются отдельной миграцией.

## Проверка

- Общий `AGENTS.md` существует и читается строгим UTF-8 decoder.
- Каждый локальный файл содержит ровно одну обязательную относительную ссылку на общий файл.
- Все восемь ссылок разрешаются в один workspace-level `AGENTS.md`.
- В общем файле присутствуют repo map, precedence, bounded navigation, MCP routing, SDD/ADR, validation, network и safety rules.
- В локальных файлах отсутствуют продублированные общие разделы SDD/ADR, generic network и generic bounded navigation.
- В каждом локальном файле сохранены все repository-specific требования.
- Общий и локальные файлы не ссылаются на Memory Bank и не содержат абсолютный локальный путь.
- В каждом Git-репозитории изменён только `AGENTS.md`.

## Риски

- Общий файл находится вне Git-репозиториев и требует отдельного механизма распространения workspace configuration.
- Ошибка в фиксированной topology ломает относительные ссылки и должна явно диагностироваться.
- Централизация создаёт обязательную зависимость локальных файлов от общего файла.
- Слишком подробный общий файл ухудшит context efficiency; repository-specific детали должны оставаться локальными.
- При переносе общего правила важно не потерять ограничения, уже согласованные в SPEC-0004 и SPEC-0005.

## Критерии приёмки

- Создан один обязательный общий workspace-level `AGENTS.md`.
- Восемь локальных файлов содержат корректные обязательные ссылки и только repository-specific instructions.
- Общие правила определены в одном месте без функциональных потерь.
- Фиксированная repository topology и MCP routing отражены точно.
- Никакие другие файлы в product repositories не изменены.
- Результаты проверки зафиксированы в этой SDD.

## Открытые вопросы

Блокирующих вопросов нет. Перед реализацией пользователь должен утвердить обновлённую SDD.

## Результат реализации

Создан обязательный общий `KAFKA_PROJECTS_ROOT/AGENTS.md`. Восемь локальных файлов переписаны как repository-specific дополнения с обязательными относительными ссылками на общий файл.

Общие bounded-navigation, multi-repository, MCP, 1C editing/validation, SDD/ADR, documentation, network, secret и destructive-operation rules перенесены в общий файл. Из локальных файлов удалено их дублирование; сохранены роли репозиториев, локальные documentation links, точная MCP routing и специфичные ограничения.

После пользовательской проверки сведения о supporting base configurations перенесены из общего файла в owning local instructions: `conversion/КД` описана в `conversion/KFK/AGENTS.md`, а assembled `tests/unit/base` — в `tests/unit/unit/AGENTS.md`.

Выполнены проверки:

- общий и восемь локальных файлов прочитаны строгим UTF-8 decoder без ошибок;
- каждая локальная Markdown-ссылка разрешается точно в один `KAFKA_PROJECTS_ROOT/AGENTS.md`;
- в общем файле подтверждены обязательные repo map, bounded navigation, MCP routing, SDD language/gates, validation escalation и network limit;
- в локальных файлах отсутствуют продублированные sections `Bounded Navigation`, `SDD` и `Network`;
- подтверждены repository-specific правила: prefixes `кфк`/`кфк_т_`, `kfk_edt`, `conv_edt`, `kfk-unit-edt`, generated-only reports, Vanessa Automation и destructive tooling operations;
- общий и локальные файлы не содержат ссылок на Memory Bank или абсолютный локальный workspace path;
- `git status` каждого из восьми репозиториев показывает только `AGENTS.md`.

Исходники, тесты, generated reports, tooling, CI и product documentation не изменялись. Пользователь подтвердил итоговую структуру 2026-08-03.

## Отклонения от спецификации

Не зафиксированы.

## Связанные документы

- `tasks/sdd/spec-0004-adapter-agents-pilot.md`
- `tasks/sdd/spec-0005-repository-agents-rollout.md`
- `adapter/adapter/AGENTS.md`
