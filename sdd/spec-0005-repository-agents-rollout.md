---
title: Инструкции для агентов остальных репозиториев экосистемы
id: SPEC-0005
type: specification
status: verified
owner:
created: 2026-08-03
updated: 2026-08-03
github_issue:
affected_repositories:
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-reports
  - kafka-adapter-tests-ui
  - kafka-adapter-tests-unit
  - kafka-tools
  - kfk-tasks
affected_components:
  - repository-agent-instructions
related_adrs: []
tags:
  - specification
  - agents
sources:
  - "repo:kafka-adapter-base:README.md"
  - "repo:kafka-adapter-examples:README.md"
  - "repo:kafka-adapter-conv:README.md"
  - "repo:kafka-adapter-tests-reports:README.md"
  - "repo:kafka-adapter-tests-ui:README.md"
  - "repo:kafka-adapter-tests-unit:README.md"
  - "repo:kafka-tools:readme.md"
---

# Инструкции для агентов остальных репозиториев экосистемы

## Краткое описание

- Создать англоязычный `AGENTS.md` в корне каждого из семи оставшихся Git-репозиториев.
- Использовать согласованную структуру пилотного `adapter/adapter/AGENTS.md`, сохранив только применимые к конкретному репозиторию правила.
- Зафиксировать отдельную маршрутизацию EDT для adapter, conversion и unit-test проектов.
- Не создавать инструкции в `conversion/КД` и `tests/unit`, поскольку это не корни канонических Git-репозиториев.

## Контекст

Пилотный `adapter/adapter/AGENTS.md` утверждён в SPEC-0004. Остальные репозитории имеют разные обязанности: host configuration, examples, Conversion Data extension, generated reports, Vanessa Automation tests, YAxUnit tests и development infrastructure. Механическое копирование product-инструкций создаст неверные правила редактирования и проверки.

## Проблема

Без локальных инструкций агент может сканировать большой репозиторий целиком, напрямую изменить 1С-файлы, использовать неверный EDT/MCP, вручную исправить generated report или выполнить небезопасную инфраструктурную операцию.

## Цель

Добавить самодостаточные репозиторий-специфичные `AGENTS.md`, которые определяют назначение, ограниченную навигацию, допустимые изменения, MCP routing, проверки, SDD/ADR workflow, documentation duties, сетевой лимит и меры безопасности.

## Не входит в задачу

- Не изменять `adapter/adapter/AGENTS.md`, кроме отдельной явно согласованной корректировки.
- Не создавать `AGENTS.md` в `conversion/КД`, `tests/unit` или в общем корне мультирепозитория.
- Не удалять и не переносить Memory Bank в этой спецификации.
- Не изменять исходники 1С, тестовые сценарии, generated reports, tooling, CI или product documentation.
- Не запускать инфраструктуру, тестовые стенды или сетевые загрузки.

## Область изменений

Создать только следующие файлы:

- `adapter/base/AGENTS.md`;
- `adapter/examples/AGENTS.md`;
- `conversion/KFK/AGENTS.md`;
- `tests/reports/AGENTS.md`;
- `tests/ui/AGENTS.md`;
- `tests/unit/unit/AGENTS.md`;
- `tools/AGENTS.md`.

Обновить эту SDD результатом реализации и проверками.

## Общие функциональные требования

### Формат и источники истины

- Каждый `AGENTS.md` писать на английском языке в UTF-8.
- Все SDD писать на русском языке; technical identifiers, команды и пути не переводить.
- Файл должен быть самодостаточным для отдельного клона репозитория.
- Текущие локальные исходники и тесты считать первичными источниками фактического поведения.
- README и локальную документацию считать каноническим сопровождаемым описанием, если они не противоречат исходникам или тестам.
- Не переносить в `AGENTS.md` подробные знания об архитектуре и API; использовать локальные ссылки.

### Ограниченная навигация

- Запретить рекурсивное сканирование всего репозитория.
- Начинать с README, известного пути, локальной документации, ограниченного MCP-запроса или пути пользователя.
- Использовать узкие лимиты и запрашивать только необходимые объекты, методы, разделы или диапазоны строк.
- Не загружать модуль или крупный файл целиком без необходимости.
- Если расположение неизвестно, запросить у пользователя каталог или файл вместо сканирования репозитория.

### Изменения нескольких репозиториев

- Изменять несколько репозиториев только при явно заданной пользователем multi-repository scope или если они перечислены в утверждённом SDD.
- Не вносить зависимые изменения за пределами текущего scope; перечислить их в результате.

### SDD и ADR

- Требовать утверждённый SDD для нетривиальных изменений поведения, публичного API, схем данных и нескольких репозиториев.
- Разрешить агенту создавать `draft`, но запретить реализацию до явного утверждения пользователем.
- Не требовать повторного подтверждения для уже утверждённого SDD.
- Не требовать SDD для локального bug fix, точечного теста, изменения документации или обычного tooling fix, если контракты не меняются.
- Создавать ADR только для долгосрочного архитектурного решения или изменения границ компонентов.
- Если `tasks/sdd` недоступен, сообщить об ограничении и запросить путь, не создавая новое каноническое расположение.

### Документация и завершение

- Обновлять README или локальную документацию вместе с изменениями публичных interfaces, configuration, deployment, constraints или user-visible behavior.
- Не обновлять документацию при внутреннем refactoring без изменения поведения.
- В утверждённом SDD фиксировать фактический результат, выполненные проверки, недоступную verification и отклонения.

### Сеть и безопасность

- Ограничение применять к любым загрузкам из глобального интернета, включая dependencies, release artifacts и container layers.
- Не начинать загрузку, если артефакт больше 100 MB или размер нельзя установить заранее.
- Попросить пользователя предоставить артефакт локально или явно разрешить загрузку.
- Разрешить использование локального cache.
- Не раскрывать и не коммитить secrets, tokens, credentials и personal configuration.
- Не выполнять destructive operations без явного разрешения пользователя.
- Сохранять unrelated user changes и не использовать destructive Git operations.

## Репозиторий-специфичные требования

### `kafka-adapter-base` — `adapter/base`

- Определить репозиторий как BSP-based host configuration для разработки и тестирования адаптера.
- Для любых изменений 1С в `src/**` использовать только `kfk_edt`.
- При недоступности `kfk_edt` сообщить ошибку и запретить прямое текстовое редактирование 1С-файлов.
- Для навигации использовать `kfk_edt`; не маршрутизировать проект через `code-metadata-mcp` или `graph-metadata-mcp`.
- После изменений использовать focused EDT diagnostics, `SyntaxCheckServer` и `v8std`.
- Сохранять сложившийся source style в пределах правил `v8std`.

### `kafka-adapter-examples` — `adapter/examples`

- Определить репозиторий как development-only extension с примерами API и integration scenarios, не предназначенный для production deployment.
- Для любых изменений 1С в `src/**` использовать только `kfk_edt`.
- При недоступности `kfk_edt` сообщить ошибку и запретить прямое текстовое редактирование 1С-файлов.
- Для новых принадлежащих репозиторию объектов метаданных использовать префикс `кфк_т_`.
- Для навигации использовать `kfk_edt`; не маршрутизировать проект через `code-metadata-mcp` или `graph-metadata-mcp`.
- После изменений использовать focused EDT diagnostics, `SyntaxCheckServer`, `v8std` и релевантные тесты адаптера, если окружение доступно.

### `kafka-adapter-conv` — `conversion/KFK`

- Определить репозиторий как расширение Conversion Data 3.1 для произвольных XDTO contracts и интеграции с Kafka Adapter.
- Для любых изменений 1С в `src/**` использовать только `conv_edt`.
- При недоступности `conv_edt` сообщить ошибку и запретить прямое текстовое редактирование 1С-файлов.
- Для навигации и актуального состояния использовать `conv_edt`; не использовать `kfk_edt`, `code-metadata-mcp` или `graph-metadata-mcp`.
- Учитывать зависимость от локальной base configuration `conversion/КД`, но не изменять её в рамках инструкций этого репозитория.
- После изменений использовать focused EDT diagnostics, `SyntaxCheckServer` и `v8std`.
- В пределах `v8std` сохранять существующие naming conventions и source style.

### `kafka-adapter-tests-reports` — `tests/reports`

- Определить репозиторий как generated-only публикацию Allure и Sonar reports через GitHub Pages.
- Запретить ручное изменение `latest/`, каталогов `<run_id>-<run_attempt>/`, Allure output и Sonar output.
- Разрешить изменения только README, GitHub Pages/Actions configuration и service files, когда задача явно относится к публикации отчётов.
- Предупредить, что generated directories будут перезаписаны или удалены publishing workflow.
- Проверять configuration и ссылки без изменения generated content.

### `kafka-adapter-tests-ui` — `tests/ui`

- Определить репозиторий как набор Vanessa Automation UI scenarios.
- Разрешить прямое редактирование feature-файлов и другой не-1С test configuration в UTF-8 с сохранением существующего стиля.
- Не применять EDT к Vanessa feature-файлам.
- Проверять только затронутые scenarios через доступный Vanessa Automation workflow; если environment недоступен, явно указать это.
- Не изменять product source из test task без явно заданного multi-repository scope.

### `kafka-adapter-tests-unit` — `tests/unit/unit`

- Определить репозиторий как YAxUnit tests и scripts сборки локального EDT test project.
- Для любых изменений 1С в `src/**` использовать только `kfk-unit-edt`.
- При недоступности `kfk-unit-edt` сообщить ошибку и запретить прямое текстовое редактирование 1С-файлов.
- Не использовать для unit-проекта `kfk_edt`, `conv_edt`, `code-metadata-mcp` или `graph-metadata-mcp`.
- После изменения 1С использовать focused EDT diagnostics, `SyntaxCheckServer`, `v8std` и релевантные YAxUnit tests.
- Разрешить прямое изменение assembly scripts и другой не-1С configuration в UTF-8 с сохранением стиля.
- Не изменять adapter/base/examples из unit-test task без явно заданного multi-repository scope.

### `kafka-tools` — `tools`

- Определить репозиторий как набор CI/release scripts, Docker environments, database tools и XDTO generator.
- Разрешить прямое изменение не-1С файлов в UTF-8 с сохранением существующего стиля.
- Использовать минимальную tool-specific verification: syntax check, focused tests и configuration validation, которые уже предусмотрены затронутым component.
- Не запускать долгоживущую инфраструктуру без необходимости задачи.
- Разрешить обычные read-only diagnostics, `docker compose config`, запуск требуемого сервиса и просмотр logs, если это не вызывает запрещённую сетевую загрузку.
- `down -v`, `prune`, удаление volumes/databases, restore и другие destructive operations разрешать только после явного подтверждения.
- Не читать и не выводить `.env`, tokens, passwords или credentials.
- Tracked test credentials не считать production secrets, но не распространять за пределы репозитория.

## Общие правила проверки 1С

После изменения 1С:

1. Выполнить focused EDT diagnostics через назначенный проекту EDT MCP.
2. Проверить изменённый BSL через `SyntaxCheckServer`.
3. Выполнить focused `v8std` checks.
4. Запустить релевантные YAxUnit/UI tests, если они покрывают изменение и окружение доступно.
5. Сообщить результаты и причины невыполненных проверок.

EDT diagnostics могут давать ложные срабатывания. Если diagnostic сохраняется после одной целевой итерации исправления, агент должен остановиться и спросить пользователя, как обработать ошибку, а не продолжать менять код.

## Нефункциональные требования

- Повторить общий layout пилота там, где соответствующий раздел применим.
- Не копировать нерелевантные product-specific правила.
- Использовать только относительные пути репозитория.
- Не добавлять ссылки на Memory Bank.
- Файлы должны быть достаточно краткими для чтения в начале задачи.
- Не придумывать build/test commands, отсутствующие в README, CI или существующих scripts.

## План реализации

1. Создать семь `AGENTS.md` по общему layout пилота.
2. Добавить в каждый файл только его EDT/MCP routing и repository-specific editing/validation rules.
3. Проверить UTF-8, Markdown headings, обязательные ограничения и отсутствие ссылок на Memory Bank.
4. Проверить `git status` каждого репозитория и убедиться, что добавлен только `AGENTS.md`.
5. Зафиксировать результаты и отклонения в этой SDD.
6. Перед удалением Memory Bank отдельно подготовить migration SDD с аудитом уникальной информации и ссылок.

## Совместимость и миграции

Добавление инструкций не меняет runtime behavior. Удаление Memory Bank, перенос существующих SDD/ADR и исправление ссылок остаются отдельной миграцией.

## Проверка

- Все семь файлов существуют и читаются строгим UTF-8 decoder.
- Все файлы имеют корректную Markdown-структуру и написаны на английском языке.
- Во всех файлах запрещено полное сканирование репозитория.
- В 1С-репозиториях запрещено прямое изменение `src/**` и указан ровно один корректный EDT MCP.
- `adapter/examples` содержит префикс `кфк_т_`.
- `tests/unit/unit` маршрутизирован только через `kfk-unit-edt`.
- `tests/reports` запрещает ручное изменение generated reports.
- `tools` содержит destructive-operation, secret и network safeguards.
- Ни один файл не ссылается на Memory Bank.
- В каждом product Git repository изменён только новый `AGENTS.md`.

## Риски

- Различия репозиториев могут потеряться при механическом копировании пилота; каждый файл проверяется отдельно.
- EDT MCP может быть недоступен; прямое редактирование 1С намеренно блокируется.
- Unit-test project зависит от нового `kfk-unit-edt`; неверная fallback-маршрутизация запрещена.
- Generated reports могут быть случайно изменены; `tests/reports/AGENTS.md` должен явно ограничивать editable scope.
- Tool validation может потребовать крупные container images; общий сетевой лимит имеет приоритет.

## Критерии приёмки

- Созданы ровно семь перечисленных `AGENTS.md`.
- Каждый файл самодостаточен, англоязычен и соответствует назначению репозитория.
- Все общие и репозиторий-специфичные требования отражены без противоречий.
- Прямое редактирование 1С невозможно при недоступности назначенного EDT MCP.
- Никакие исходники, тесты, generated reports, tooling, CI или product docs не изменены.
- Результат и проверки записаны в SDD.

## Открытые вопросы

Блокирующих вопросов нет. Перед реализацией пользователь должен утвердить эту SDD.

## Результат реализации

Созданы семь англоязычных файлов:

- `adapter/base/AGENTS.md`;
- `adapter/examples/AGENTS.md`;
- `conversion/KFK/AGENTS.md`;
- `tests/reports/AGENTS.md`;
- `tests/ui/AGENTS.md`;
- `tests/unit/unit/AGENTS.md`;
- `tools/AGENTS.md`.

Выполнены проверки:

- каждый файл прочитан строгим UTF-8 decoder без ошибок;
- во всех файлах подтверждён запрет полного рекурсивного сканирования;
- ссылки на Memory Bank отсутствуют;
- для `adapter/base` и `adapter/examples` указан только `kfk_edt` как editing interface;
- для `conversion/KFK` указан `conv_edt`;
- для `tests/unit/unit` указан `kfk-unit-edt` и запрещены остальные EDT/metadata MCP;
- в `adapter/examples` зафиксирован префикс `кфк_т_`;
- в `tests/reports` запрещено ручное изменение generated reports;
- в `tools` зафиксированы destructive-operation, secret и network safeguards;
- `git status` каждого затронутого product repository показывает только новый `AGENTS.md`.

Исходники, тесты, generated reports, tooling, CI и product documentation не изменялись. Пользователь подтвердил созданные инструкции 2026-08-03.

## Отклонения от спецификации

Не зафиксированы.

## Связанные документы

- `adapter/adapter/AGENTS.md`
- `tasks/sdd/spec-0004-adapter-agents-pilot.md`
- `tasks/adr/`
