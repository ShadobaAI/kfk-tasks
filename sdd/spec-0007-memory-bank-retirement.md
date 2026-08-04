---
title: Вывод Memory Bank из эксплуатации и миграция tasks
id: SPEC-0007
type: specification
status: verified
owner:
created: 2026-08-03
updated: 2026-08-03
github_issue:
affected_repositories:
  - kfk-tasks
  - kafka-adapter
  - kafka-adapter-conv
affected_components:
  - repository-agent-instructions
  - specifications
  - architecture-decisions
  - memory-bank
  - memory-bank-mcp
related_adrs:
  - ADR-0001
tags:
  - specification
  - migration
  - documentation
sources:
  - "repo:kfk-tasks:sdd/migration-audit-spec-0007.md"
  - "repo:kfk-tasks:sdd/spec-0001-memory-bank-foundation.md"
  - "repo:kfk-tasks:adr/adr-0001-markdown-canonical-storage.md"
---

# Вывод Memory Bank из эксплуатации и миграция tasks

## Краткое описание

- Создать локальный `tasks/AGENTS.md` со ссылкой на общий workspace-level `AGENTS.md`.
- Перенести сохраняемые SDD из `tasks/memory-bank/specifications` в `tasks/sdd`.
- Перенести сохраняемые ADR из `tasks/memory-bank/decisions` в `tasks/adr`.
- Провести ограниченный аудит остальных документов Memory Bank и не удалить уникальную информацию без явного решения.
- Удалить Memory Bank и связанный MCP только после прохождения migration readiness gate.

## Контекст

Проект перешёл на централизованный `KAFKA_PROJECTS_ROOT/AGENTS.md` и repository-specific локальные инструкции. Архитектура и API продукта должны сопровождаться в owning repository documentation, прежде всего в `adapter/adapter/docs`. SDD и ADR остаются в `kfk-tasks`, но больше не должны находиться внутри Memory Bank.

В `tasks/sdd` уже созданы SPEC-0004—SPEC-0007. В старом каталоге остаются ранние specifications, index и template. Аналогично ADR, index и template находятся в `tasks/memory-bank/decisions`.

## Проблема

Memory Bank дублирует repository documentation, требует отдельного maintenance workflow и MCP, а часть его инструкций уже перенесена в `AGENTS.md`. Прямое удаление каталога без аудита может потерять уникальные сведения, исторические SDD/ADR и оставить битые ссылки или неиспользуемый MCP implementation.

## Цель

Оставить в `kfk-tasks` минимальный сопровождаемый набор:

- `AGENTS.md` — repository-specific инструкции tasks;
- `sdd/` — индекс, template и все сохраняемые specifications;
- `adr/` — индекс, template и все сохраняемые architecture decisions;
- task tracking и иные файлы репозитория, не относящиеся к Memory Bank.

Memory Bank, его maintenance workflow и MCP должны быть удалены без потери уникальных знаний и без битых tracked references.

## Не входит в задачу

- Не изменять product source, tests, generated reports или tooling других репозиториев.
- Не переносить архитектурную документацию автоматически в другие репозитории без предварительного подтверждения пользователя.
- Не сохранять Memory Bank как архивный или deprecated каталог.
- Не менять фактическое поведение Kafka Adapter.
- Не переписывать историческое содержание SDD/ADR, кроме путей, индексов, статусов supersession и необходимых migration notes.

## Область изменений

После bounded audit область миграции расширена на три репозитория:

- создать `tasks/AGENTS.md`;
- создать и наполнить `tasks/adr/`;
- дополнить и нормализовать `tasks/sdd/`;
- обновить tracked references и документацию `tasks`;
- удалить подтверждённые Memory Bank files и MCP implementation/configuration.
- перенести только долговечные и неочевидные product architecture/API/operations boundaries в подходящие файлы `adapter/adapter/docs`;
- перенести только долговечную информацию о base attachment и compatibility boundaries в `conversion/KFK/README.md` или другой явно выбранный локальный документ;
- не переносить inventories, counts, current diagnostics, method/field lists и сведения, которые быстро устаревают либо легко повторно получаются из source/EDT.

Если дальнейший аудит выявит уникальные знания, которые необходимо перенести в иной owning repository, агент должен:

1. остановить destructive migration;
2. перечислить точные документы и целевые файлы;
3. добавить owning repositories в `affected_repositories` и scope;
4. вернуть SPEC-0007 в `draft`;
5. получить повторное одобрение пользователя.

## Функциональные требования

### `tasks/AGENTS.md`

- Написать файл на английском языке в UTF-8.
- Добавить обязательную ссылку `../AGENTS.md` на общий workspace-level файл.
- При отсутствии общего файла сообщать workspace-layout error и останавливать работу.
- Определить `kfk-tasks` как repository для SDD, ADR и task tracking, а не для product source.
- Указать `sdd/` как канонический каталог specifications и `adr/` как канонический каталог decisions.
- Не дублировать общие правила из workspace-level `AGENTS.md`.
- Зафиксировать русский язык SDD и сохранение technical identifiers без перевода.
- Запретить хранить raw MCP output, secrets, absolute workspace paths и reasoning logs.

### Аудит Memory Bank

Аудит ограничивается известным каталогом `tasks/memory-bank` и tracked references на него; он не разрешает сканировать целиком другие repositories.

Для каждого документа вне `specifications/` и `decisions/` определить одну категорию:

- `duplicate` — информация подтверждённо содержится в owning repository docs или актуальных `AGENTS.md`;
- `obsolete` — информация больше не соответствует целевой модели;
- `operational-migration` — правило должно быть перенесено в `tasks/AGENTS.md`, SDD/ADR index или другую tasks documentation;
- `unique-external` — уникальная информация требует переноса в owning repository и повторного одобрения scope;
- `verification-required` — происхождение или актуальность нельзя подтвердить точечно.

Результат аудита оформить как временный migration checklist внутри SPEC-0007 или как отдельный tracked Markdown report в `tasks/sdd/`, на который ссылается SPEC-0007. Отчёт не должен превращаться в новый Memory Bank.

### Migration readiness gate

Удаление Memory Bank и MCP запрещено, пока не выполнены все условия:

- каждый документ классифицирован;
- для `unique-external` нет нерешённых элементов;
- `verification-required` разрешены пользователем или перенесены в явно сопровождаемый backlog;
- SDD/ADR перенесены и их индексы валидны;
- все tracked references на старые пути перечислены и имеют новое назначение либо подтверждены для удаления;
- определены точные MCP files/configuration, которые относятся только к Memory Bank;
- пользователь увидел audit summary и явно подтвердил destructive phase.

### Перенос SDD

- Перенести index, template и сохраняемые `spec-*.md` из `memory-bank/specifications/` в `sdd/`.
- Не перезаписывать существующие SPEC-0004—SPEC-0007.
- Сохранить stable specification IDs и историю статусов.
- Обновить `sdd/README.md`, включив все сохранённые specifications и актуальный lifecycle.
- Удалить Memory Bank-specific wording из текущего SDD workflow, не переписывая исторический контекст старых specifications.
- Историческую SPEC-0001 о создании Memory Bank сохранить; при необходимости отметить supersession со ссылкой на SPEC-0007, не удаляя документ.
- Все новые и изменяемые процессные разделы SDD писать на русском языке. Исторический текст не переводить автоматически в рамках миграции.

### Перенос ADR

- Перенести index, template и сохраняемые ADR в `tasks/adr/`.
- Сохранить stable ADR IDs и historical status.
- Обновить ссылки на новый каталог.
- Проверить ADR-0001 на противоречие новой модели.
- Если ADR-0001 требует supersession, создать новый ADR о замене Memory Bank на repository documentation + hierarchical `AGENTS.md` + `tasks/sdd`/`tasks/adr` и связать решения.
- Язык существующих ADR сохранять; новый ADR следует текущему стилю ADR index/template, если пользователь отдельно не задаст другой язык.

### References и MCP cleanup

- Найти tracked references на `memory-bank`, Memory Bank MCP, старые specification/decision paths и retired commands в пределах `kfk-tasks` и в уже известных `AGENTS.md`.
- Обновить ссылки, которые должны продолжать работать.
- Удалить references, относящиеся только к retired Memory Bank/MCP.
- Перед удалением MCP определить его точные implementation, tests, configuration, dependencies и documentation files.
- Не удалять shared infrastructure, если её использование выходит за Memory Bank MCP или не подтверждено.
- После cleanup не должно оставаться активных инструкций, предлагающих использовать Memory Bank MCP.

### Destructive phase

- Удалять только точно перечисленные tracked files под `tasks/memory-bank` и MCP-specific files/configuration.
- Не использовать broad recursive delete commands.
- Выполнить удаление через reviewable patch или точечные file operations.
- Git обеспечивает восстановление tracked files; untracked files не удалять без отдельного подтверждения.
- После удаления явно сообщить, что удалено и как tracked content может быть восстановлен.

## Нефункциональные требования

- Не сканировать целиком workspace или product repositories.
- Использовать bounded file lists, exact references и section-level comparison.
- Не копировать дублирующую информацию в новое центральное хранилище.
- Не сохранять абсолютный локальный путь; использовать `KAFKA_PROJECTS_ROOT` и repository-relative references.
- Markdown должен оставаться читаемым без MCP.
- Не скачивать внешние материалы для миграции без необходимости и разрешения по общему network policy.

## План реализации

### Фаза 1 — подготовка

1. Создать `tasks/AGENTS.md`.
2. Получить bounded inventory `tasks/memory-bank` и известных MCP-related paths.
3. Собрать tracked references на Memory Bank и старые SDD/ADR paths внутри `kfk-tasks`.
4. Классифицировать документы и подготовить audit summary.

### Фаза 2 — readiness review

1. Представить пользователю audit summary, `unique-external`, `verification-required` и точный deletion set.
2. При необходимости расширить scope и вернуть SDD в `draft`.
3. Получить явное подтверждение destructive phase.

### Фаза 3 — миграция

1. Перенести SDD и ADR в канонические каталоги.
2. Обновить indexes, templates, statuses и references.
3. Создать superseding ADR, если это подтвердит review ADR-0001.
4. Удалить подтверждённые Memory Bank и MCP files.

### Фаза 4 — проверка

1. Проверить Markdown links и отсутствие активных references на retired paths/MCP.
2. Проверить полноту SDD/ADR indexes и stable IDs.
3. Проверить Git diff/status и отсутствие изменений вне scope.
4. Записать результат, deletion set, verification и deviations в SPEC-0007.

## Совместимость и миграции

Старые прямые ссылки на `tasks/memory-bank/**` перестанут работать после удаления. Поддержание redirect/stub files не планируется, поскольку Memory Bank должен быть удалён полностью. Все tracked internal references должны быть обновлены до удаления.

Исторические SDD/ADR сохраняют IDs и содержание, поэтому ссылки по ID остаются концептуально стабильными, но меняют filesystem path.

## Проверка

- `tasks/AGENTS.md` существует, ссылается на `../AGENTS.md` и содержит только tasks-specific rules.
- `tasks/sdd/README.md` перечисляет все сохранённые specifications без duplicate IDs.
- `tasks/adr/README.md` перечисляет все сохранённые decisions без duplicate IDs.
- Templates находятся в новых канонических каталогах.
- Historical documents доступны по новым путям и имеют валидные internal links.
- Каждый бывший Memory Bank document присутствует в audit classification.
- Нет нерешённых `unique-external` перед destructive phase.
- Нет активных tracked references на `memory-bank`, Memory Bank MCP или старые SDD/ADR paths после cleanup, кроме явно допустимого исторического текста.
- MCP-specific implementation/tests/configuration удалены, shared infrastructure сохранена.
- `git status` и diff репозитория `kfk-tasks` содержат только изменения, перечисленные в этой SDD.
- Ни один другой Git-репозиторий не изменён.

## Риски

- Уникальная архитектурная информация может быть ошибочно классифицирована как duplicate.
- Исторические ссылки на SDD/ADR изменят filesystem paths.
- MCP implementation может разделять code/dependencies с другими tasks capabilities.
- Удаление generated или untracked MCP state может быть необратимым; такое состояние не входит в автоматическое удаление.
- SPEC-0001 и ADR-0001 описывают старую модель; удалять их нельзя, но status/supersession должны быть понятны.
- Создание нового центрального audit report может фактически восстановить Memory Bank; отчёт должен быть migration-only и ограниченным.

## Критерии приёмки

- Создан локальный `tasks/AGENTS.md`.
- Все сохраняемые SDD находятся в `tasks/sdd`, все ADR — в `tasks/adr`.
- Stable IDs, historical records, indexes и templates сохранены.
- Уникальные знания не удалены без явного решения пользователя.
- Memory Bank и относящийся только к нему MCP удалены после отдельного подтверждения destructive phase.
- Active references обновлены; допустимый historical text явно отделён от active instructions.
- Изменения не выходят за утверждённый repository scope.
- SPEC-0007 содержит фактический audit summary, deletion set, проверки и отклонения.

## Открытые вопросы

- Расширенный scope `kafka-adapter` и `kafka-adapter-conv` утверждён пользователем 2026-08-03.
- Pending-verification backlog сохраняется в draft SPEC-0008 по решению пользователя от 2026-08-03.
- Пользователь должен отдельно подтвердить destructive phase после переноса уникальных знаний и повторной проверки.

## Результат реализации

Подготовительная фаза выполнена частично:

- создан `tasks/AGENTS.md`;
- собран bounded inventory всех 36 Markdown documents Memory Bank;
- определён точный MCP-related tracked file set;
- проверены shared Markdown configuration files;
- проведён targeted review потенциально уникальных architecture, metadata, Conversion Data и pending-verification документов;
- ADR-0001 проверен и требует superseding ADR;
- создан [audit report](migration-audit-spec-0007.md).

Обнаружены `unique-external` документы. В соответствии с migration readiness gate destructive phase была остановлена, SPEC-0007 возвращена в `draft`, а affected repositories расширены и повторно утверждены пользователем.

После утверждения применён value filter: перенесены только durable architecture/failure/change и Conversion Data compatibility boundaries. Быстро устаревающие inventories, counts, diagnostics и легко запрашиваемые source facts не переносились. Создан минимальный draft SPEC-0008 с двумя durable external compatibility gaps.

Historical SDD/ADR перенесены в новые канонические каталоги.

Созданы SDD/ADR indexes и templates, исправлены surviving links, ADR-0001 отмечен `superseded`, создан accepted ADR-0002. Exact destructive set содержит 64 tracked files; ignored/untracked files внутри targets не обнаружены.

Пользователь подтвердил destructive phase 2026-08-03. Точечным patch удалены:

- все 36 tracked files `tasks/memory-bank`;
- 27 MCP-only implementation/test/docs/config/benchmark/package/launcher files;
- устаревший `.gitignore`, содержавший только Python/MCP/Memory Bank patterns.

Пустые retired directories удалены после отдельной проверки отсутствия файлов. Shared Markdown tooling сохранён. Финальная проверка подтвердила:

- `tasks/memory-bank` отсутствует;
- активных MCP references в README, AGENTS, SDD/ADR indexes/templates и ADR-0002 нет;
- все surviving Markdown files читаются как UTF-8;
- relative Markdown links разрешаются;
- удалено ровно 64 tracked-файла;
- 1С-исходники, tests других репозиториев, generated reports и CI не изменялись.

Пользователь принял результат миграции 2026-08-03.

## Отклонения от спецификации

Не зафиксированы.

## Связанные документы

- `tasks/sdd/migration-audit-spec-0007.md`
- `tasks/sdd/spec-0004-adapter-agents-pilot.md`
- `tasks/sdd/spec-0005-repository-agents-rollout.md`
- `tasks/sdd/spec-0006-workspace-agents.md`
- `tasks/sdd/spec-0001-memory-bank-foundation.md`
- `tasks/adr/adr-0001-markdown-canonical-storage.md`
