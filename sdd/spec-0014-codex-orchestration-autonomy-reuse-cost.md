---
title: Автономность, reuse и контроль стоимости Codex orchestration
id: SPEC-0014
type: specification
status: implemented
owner:
created: 2026-09-21
updated: 2026-09-21
github_issue:
affected_repositories:
  - kafka-tools
  - kafka-adapter
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-reports
  - kafka-adapter-tests-ui
  - kafka-adapter-tests-unit
  - kfk-tasks
affected_components:
  - Codex workspace AGENTS.md
  - Codex repository AGENTS.md
  - Codex skills
  - Codex MCP configuration
  - kafka-policy MCP
  - code-index orchestration
  - EDT-MCP tool exposure
  - discovery and evidence reuse
  - error recovery policy
  - compliance workflow
  - Codex regression scenarios and cost benchmarks
related_adrs:
  - ADR-0002
  - ADR-0004
  - ADR-0005
  - ADR-0006
  - ADR-0007
tags:
  - specification
  - codex
  - orchestration
  - context
  - cost
  - reuse
  - mcp
  - 1c
  - policy
  - autonomy
  - maintainability
sources:
  - "repo:kafka-tools:ai/AGENTS.md"
  - "repo:kafka-tools:ai/workspace-policy.json"
  - "repo:kafka-tools:ai/.codex/config.toml"
  - "repo:kafka-tools:ai/.codex/skills/1c-routing/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-code-change/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-code-index/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-standards/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/task-orchestration/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/yaxunit-tests/SKILL.md"
  - "repo:kafka-tools:ai/policy/README.md"
  - "repo:kafka-tools:ai/policy/detector.mjs"
  - "repo:kafka-tools:ai/policy/selector.mjs"
  - "repo:kafka-tools:ai/policy/read-only-mcp.mjs"
  - "repo:kafka-adapter:AGENTS.md"
  - "repo:kafka-adapter-base:README.md"
  - "repo:kafka-adapter-examples:README.md"
  - "repo:kafka-adapter-conv:README.md"
  - "repo:kafka-adapter-tests-reports:README.md"
  - "repo:kafka-adapter-tests-ui:README.md"
  - "repo:kafka-adapter-tests-unit:AGENTS.md"
  - "repo:kfk-tasks:sdd/spec-0012-codex-context-quality-and-cost.md"
---

# Автономность, reuse и контроль стоимости Codex orchestration

## Краткое описание

Спецификация является follow-up к `SPEC-0012` и устраняет проблемы, выявленные при анализе реальных длинных Codex-сессий разработки в workspace «1С: Адаптер Kafka».

`SPEC-0012` ввёл правильные базовые инварианты:

- authoritative routing;
- bounded navigation;
- deterministic policy selection;
- mandatory compliance;
- task-scoped context;
- read-only analysis plane;
- запрет неконтролируемого доступа к защищённому `src/**`;
- обязательные pre/post diagnostics для 1С mutation.

Практическая эксплуатация показала, что текущая orchestration-модель всё ещё перекошена в сторону максимального fail-closed контроля и недостаточно оптимизирована по четырём другим свойствам:

1. стоимости model context и количества tool calls;
2. обязательному повторному использованию уже существующей реализации;
3. автономному восстановлению после безопасно устранимых ошибок;
4. пропорциональности compliance-процесса риску изменения.

Цель этой спецификации — сохранить correctness, authority boundaries и обязательные normative gates, одновременно сделать агента:

- менее расточительным по context и tool calls;
- менее склонным к повторному discovery;
- обязательным потребителем уже существующей reusable logic;
- способным самостоятельно восстанавливаться после локальных ожидаемых ошибок;
- пропорциональным по verification cost реальному риску изменения.

Спецификация применяется ко всему workspace, определённому `ai/AGENTS.md`, а не только к `kafka-adapter-tests-unit`.

История работы с `kafka-adapter-tests-unit` используется лишь как один из regression examples, в котором одновременно проявились excessive discovery, premature fail-fast и дорогостоящий compliance loop.

Спецификация не изменяет роль `v8std`, EDT-MCP или `code-index` как источников данных. Основные изменения выполняются в `kafka-tools`: shared instructions, skills, `kafka-policy` MCP, MCP schemas, configuration/tool exposure и regression/benchmark tests.

## Контекст

### Workspace

Текущий workspace является фиксированным набором независимых Git repositories:

| Repository | Canonical path |
|---|---|
| `kafka-adapter` | `adapter/adapter` |
| `kafka-adapter-base` | `adapter/base` |
| `kafka-adapter-examples` | `adapter/examples` |
| `kafka-adapter-conv` | `conversion/KFK` |
| `kafka-adapter-tests-reports` | `tests/reports` |
| `kafka-adapter-tests-ui` | `tests/ui` |
| `kafka-adapter-tests-unit` | `tests/unit/unit` |
| `YAxUnit` upstream checkout | `tests/unit/yaxunit` |
| `kafka-tools` | `tools` |
| `kfk-tasks` | `tasks` |

`YAxUnit` рассматривается как external/upstream dependency и test corpus. Спецификация не предполагает изменение его source.

### EDT routing

1С-контуры разделены между тремя EDT-MCP workspace:

| Scope | EDT-MCP |
|---|---|
| `adapter/adapter`, `adapter/base`, `adapter/examples` | `kfk-edt:8765` |
| `conversion/KFK`, `conversion/КД` | `conv-edt:8767` |
| `tests/unit/base`, `tests/unit/examples`, `tests/unit/unit`, `tests/unit/yaxunit` | `unit-edt:8768` |

### code-index routing

Используются canonical aliases:

| Scope | Alias |
|---|---|
| `adapter/adapter` | `kfk` |
| `adapter/base` | `kfk-base` |
| `adapter/examples` | `kfk-examples` |
| `conversion/KFK` | `kfk-conv` |
| `conversion/КД` | `kfk-conv-kd` |
| `tests/unit/unit` | `kfk-unit` |
| `tests/unit/yaxunit` | `kfk-yaxunit` |

Для assembled unit configuration повторно используются canonical aliases tested dependencies согласно `ai/AGENTS.md`.

### Существующая архитектура

`ai/AGENTS.md` задаёт workspace-wide routing, bounded navigation, evidence reuse, failure gates, правила изменения 1С, authority boundaries и запрет прямого filesystem-доступа к защищённому `src/**`.

`$1c-code-index` задаёт приоритет:

```text
structured metadata/symbol query
-> exact function/symbol
-> bounded BSL callers/callees/references at depth 1
-> bounded grep/read_file
-> bounded bsl_sql only when no named tool fits
```

и требует останавливаться, когда индекс уже дал достаточный ответ.

`$1c-code-change` организует mutation через authoritative EDT-MCP:

```text
target inspection
-> mechanism detection
-> requirement selection
-> normative evidence
-> proposal compliance
-> EDT baseline diagnostics
-> atomic mutation
-> EDT post diagnostics
-> result compliance
-> focused tests
```

`kafka-policy` реализует deterministic mechanism detection, requirement selection и compliance validation.

`v8std` является normative corpus и предоставляет bounded retrieval API, включая `v8std_get_section`, `v8std_get_summary`, `v8std_get_pattern`, `v8std_get_api_card` и другие специализированные операции.

`code-index` уже способен искать реализации по смысловым терминам, имени, сигнатуре, комментариям, объекту-владельцу, вызовам, references, call graph и data graph.

`SPEC-0012` завершена со статусом `implemented`. Новое изменение не переписывает её историю и оформляется отдельной спецификацией.

### Наблюдаемое эксплуатационное поведение

Анализ реальных Codex histories показал системные симптомы:

1. служебные MCP-вызовы и normative workflow способны создать context значительно больший, чем полезное изменение;
2. агент способен повторно получать уже подтверждённые факты;
3. broad discovery способен продолжаться после достаточного evidence;
4. агент способен создавать новую helper/function implementation без предварительного поиска существующего решения;
5. fail-fast policy способна останавливать задачу на локальном ожидаемом состоянии, которое агент может безопасно исправить сам;
6. небольшая test-only wrapper-функция способна проходить почти тот же orchestration, что и существенно более рискованное изменение;
7. недостаточно строгая MCP schema способна заставлять LLM угадывать допустимые значения аргументов и повторять failed tool calls;
8. EDT-MCP может раскрывать десятки tools одновременно, хотя конкретной задаче требуется лишь несколько.

Эти симптомы не означают ошибочность authority-модели `SPEC-0012`. Они показывают отсутствие второго слоя: cost-aware, reuse-aware и autonomy-aware orchestration поверх уже существующих correctness boundaries.

## Проблема

### P1. Чрезмерный расход токенов и tool calls

Текущие правила требуют bounded navigation и reuse evidence, но значительная часть контроля остаётся prose-policy, исполняемой самой моделью.

Модель может повторить discovery другим инструментом, снова проверить health/readiness без invalidation, повторно загрузить normative evidence, запросить слишком широкий result set, вызвать compliance несколько раз с эквивалентным state, передавать крупные повторяющиеся structures между policy calls, держать широкий EDT tool surface в model context и исследовать весь module inventory вместо нескольких релевантных symbols.

Часть проблемы уже смягчена: текущий `validateCompliance()` возвращает компактный итог `{status, digest, checked}`. Однако input contract всё ещё включает `selection`, `ledger` и, для 1С, `current.detection` с coverage critical mechanisms.

Стоимость возникает не из одного большого ответа, а из отсутствия сквозного механизма, делающего повторное discovery и compliance логически ненужным.

### P2. Отсутствует mandatory reuse-gate

`$1c-code-index` хорошо описывает способ поиска, но `$1c-code-change` требует его главным образом для неизвестного location или impact analysis.

Перед созданием нового самостоятельного поведения агент не обязан доказать отсутствие подходящей реализации.

Для крупной 1С-конфигурации это создаёт системный риск дублирования существующих функций, обхода БСП и типовых механизмов, нескольких реализаций одного правила, расхождения поведения, увеличения maintenance surface и ухудшения discoverability.

Память модели о кодовой базе не является допустимым evidence отсутствия реализации.

### P3. Failure gate не различает recoverable workflow-state и blocking failure

Текущий workspace policy требует остановки при required-tool/required-scope failure и в ряде случаев требует новый user-triggered run.

Это корректно для unavailable authoritative service, stale/incomplete required index, противоречия authoritative sources, high-risk recovery, scope expansion и отсутствующего пользовательского разрешения.

Но правило слишком широко для объекта, который ещё не adopted, объекта, который текущая задача должна создать, отключённого, но безопасно включаемого toolset, ошибочно выбранного scope, неверного enum/parameter, однозначно исправимого по schema, transient documented retry или ожидаемой precondition, входящей в workflow.

В таких случаях остановка и запрос «продолжай» не добавляют новых данных или полномочий.

### P4. Discovery budget существует только как soft policy

`AGENTS.md` уже требует сформулировать unresolved fact, выбрать один authoritative source, использовать established evidence, остановиться после достаточного результата и не дублировать один вопрос несколькими маршрутами.

Но runtime не имеет формального понятия `discovery question` и не контролирует эквивалентные повторные запросы, чрезмерный candidate fan-out, escalation без новой неопределённости и повторное чтение уже установленного source.

Глобальный лимит вида `max 10 tool calls` не подходит. Ограничивать требуется отдельный unresolved fact и его escalation chain.

### P5. Compliance workflow непропорционально дорог для низкорисковых изменений

Текущий workflow:

```text
inspect
-> detect
-> select requirements
-> load normative evidence
-> validate proposal
-> baseline diagnostics
-> mutation
-> post diagnostics
-> detect again
-> validate result
-> test
```

правильно fail-closed для public API, metadata, queries, transactions, client/server boundaries, privileged code, persistent state и complex business behavior.

Но для test-only wrapper, internal delegate, test registration и testability seam полный orchestration может стоить существенно дороже реализации.

Проблема не должна решаться выключением standards или diagnostics. Требуется сделать процесс пропорциональным риску, сохраняя нормативную полноту.

### P6. MCP schema не полностью отражает runtime contract

Текущий `validateCompliance()` фактически требует для mandatory `status = passed`, а для recommended `status = passed | deviated`; `deviated` требует `reason`.

Однако публичная MCP schema описывает ledger item как generic object без enum и required fields. В результате LLM может узнавать contract через последовательные failed calls.

Ошибка, которую способна исключить JSON Schema, не должна превращаться в reasoning loop.

## Цель

После реализации:

1. агент переиспользует ранее установленный evidence до явной invalidation;
2. один unresolved fact создаёт bounded discovery chain;
3. discovery прекращается после достаточного evidence;
4. перед созданием самостоятельной reusable logic выполняется обязательный reuse-check;
5. существующий compatible method предпочитается новой реализации;
6. recoverable workflow errors исправляются автоматически;
7. infrastructure/authority/safety failures остаются fail-closed;
8. новый user-triggered run не требуется после безопасного автоматического recovery;
9. compliance остаётся нормативно полным;
10. orchestration compliance становится пропорциональным риску;
11. MCP schemas исключают guessing loops;
12. EDT tool exposure минимизируется там, где это позволяет runtime;
13. все project routes из `ai/AGENTS.md` покрыты regression scenarios;
14. реальный выигрыш измеряется deterministic regression scenarios;
15. cost измеряется serialized request/response bytes и tool-call trace;
16. `v8std` не требуется изменять без доказанной нехватки его API;
17. внешний EDT-MCP не требуется изменять без доказанной невозможности решить проблему configuration/orchestration уровнем.

## Не входит в задачу

Не входят:

- изменение нормативного содержания `v8std`;
- изменение стандартов 1С;
- изменение YAxUnit standards;
- изменение source upstream `YAxUnit`;
- перенос normative corpus внутрь `kafka-policy`;
- отказ от EDT-MCP как authoritative live source;
- отказ от EDT-MCP как единственного sanctioned writer;
- отказ от eventual consistency `code-index`;
- автоматическая модификация product code только ради reuse;
- глобальный fixed tool-call limit;
- hidden persistent model memory;
- восстановление Memory Bank;
- отключение mandatory diagnostics;
- подавление EDT findings;
- обход SDD/ADR требований high-risk изменений;
- ослабление concurrency guards;
- blind retry mutation;
- изменение `v8std` или внешнего EDT-MCP, если acceptance достигается изменениями `kafka-tools`.

## Область изменений

### Основной implementation repository: `kafka-tools`

Планируемые области:

- `ai/AGENTS.md`;
- `ai/.codex/skills/1c-routing/SKILL.md`, если требуется уточнение общей маршрутизации;
- `ai/.codex/skills/1c-code-change/SKILL.md`;
- `ai/.codex/skills/1c-code-index/SKILL.md`;
- `ai/.codex/skills/1c-standards/SKILL.md`, если изменяется evidence reuse contract;
- `ai/.codex/skills/yaxunit-tests/SKILL.md`;
- `ai/.codex/config.toml`;
- `ai/policy/read-only-mcp.mjs`;
- `ai/policy/detector.mjs`;
- `ai/policy/selector.mjs`;
- policy tests;
- orchestration regression fixtures;
- benchmark tests;
- installer/doctor validation;
- `ai/README.md`;
- `ai/PORTING.md` только при изменении deployment/installation contract.

### Workspace repositories, на поведение агента в которых влияет спецификация

- `kafka-adapter`;
- `kafka-adapter-base`;
- `kafka-adapter-examples`;
- `kafka-adapter-conv`;
- `kafka-adapter-tests-reports`;
- `kafka-adapter-tests-ui`;
- `kafka-adapter-tests-unit`.

По умолчанию спецификация не требует изменения этих repositories. Они входят в `affected_repositories`, потому что изменяется shared Codex policy их обслуживания.

### Coordination repository: `kfk-tasks`

- этот SDD;
- ADR только при появлении нового durable component boundary или persistent orchestration state;
- bounded handoff при implementation.

### Repository-specific configs

Не входят в default implementation scope.

Если progressive disclosure невозможно обеспечить shared tooling и потребуется менять repository-owned `.codex/config.toml`, до mutation необходимо определить точный список repositories, обновить `affected_repositories`, если необходимый repo отсутствует, и получить явное утверждение multi-repository mutation scope.

## Функциональные требования

### FR-DISC-001. Session evidence reuse

Агент обязан переиспользовать установленный факт до события invalidation.

Минимальные reusable facts:

- MCP health;
- project readiness;
- alias binding;
- repository/project routing;
- source fragment/hash;
- symbol identity;
- function contract;
- requirement selection;
- loaded normative evidence;
- fixture ownership;
- dependency relationship;
- caller relationship.

Минимальные invalidation events:

- service restart/reconnect;
- reindex;
- branch/revision change;
- mutation затронутого объекта;
- explicit relevant tool error;
- contradiction;
- documented staleness boundary.

Повторная проверка reusable fact без invalidation запрещена, если она не отвечает на новый вопрос.

### FR-DISC-002. Explicit unresolved-fact gate

Перед search/read/discovery call orchestration должна концептуально определить:

```text
fact
decision
source
scope
stop condition
```

где `fact` — неизвестный факт, `decision` — решение, зависящее от факта, `source` — один primary tool, `scope` — минимальный достаточный scope, `stop condition` — результат, после которого discovery прекращается.

Структуру не требуется показывать пользователю, сохранять как reasoning log или помещать в repository. Это orchestration invariant.

### FR-DISC-003. Bounded escalation chain

Для одного unresolved fact:

```text
primary narrow query
-> bounded candidate inspection
-> one justified escalation
-> stop
```

После достаточного evidence дальнейшие запросы по тому же факту запрещены.

Для `code-index` default escalation:

```text
structured/symbol
-> exact function
-> depth-1 callers/callees
-> bounded grep/read
-> bsl_sql only when no named tool fits
```

### FR-DISC-004. Candidate fan-out

Для semantic discovery/reuse:

1. `search_terms` получает 1–3 содержательных термина;
2. по умолчанию рассматривается не более 5 наиболее релевантных кандидатов;
3. `get_function` вызывается только для кандидатов, способных изменить решение;
4. callers/callees используются только при неоднозначном contract/use;
5. расширение сверх 5 кандидатов требует ambiguity, insufficient coverage или conflicting candidates.

Число 5 является default budget, а не safety hard limit.

### FR-REUSE-001. Mandatory reuse-gate

Перед созданием новой процедуры, функции, reusable helper, standalone query logic, самостоятельного преобразования, валидации, сериализации, parsing utility, reusable collection logic или иной самостоятельной типовой логики агент обязан определить, образует ли планируемый код самостоятельное повторно используемое поведение.

Если да, reuse-check обязателен до design decision.

### FR-REUSE-002. Reuse search sequence

Reuse-check:

1. сформулировать purpose в 1–3 терминах;
2. выбрать текущий project scope по workspace routing;
3. определить минимальный набор code-index aliases, соответствующих текущему scope и его фактическим dependencies;
4. выполнить `search_terms`;
5. проверить релевантных кандидатов через `get_function`;
6. при необходимости проверить callers/callees/references;
7. определить semantic compatibility, parameters, return contract, client/server context, export availability и repository ownership;
8. использовать подходящий существующий метод;
9. создавать новую реализацию только если кандидат отсутствует, contract/context/ownership несовместимы или найденная реализация не покрывает требование.

### FR-REUSE-003. Existing non-export method

Если найдена подходящая неэкспортная реализация:

- не создавать дубликат автоматически;
- сначала определить возможность использования через существующий owner;
- определить допустимость расширения существующего contract;
- public/export contract не изменять без отдельного основания.

### FR-REUSE-004. Exemptions

Reuse-check не требуется для простого `Если`, присваивания, элементарного цикла, локального формирования `Структура`/`Массив`, формирования параметров вызова, короткого промежуточного вычисления, call-site-specific glue code и локальной части алгоритма без самостоятельной semantic responsibility.

Правило применяется к поведению, а не к каждой синтаксической функции.

### FR-REUSE-005. Workspace-aware search scope

Reuse search должен следовать route из `ai/AGENTS.md`.

Минимальный mapping:

```text
adapter/adapter     -> kfk
adapter/base        -> kfk-base
adapter/examples    -> kfk-examples
conversion/KFK      -> kfk-conv
conversion/КД       -> kfk-conv-kd
tests/unit/unit     -> kfk-unit + необходимые canonical dependency aliases
tests/unit/yaxunit  -> kfk-yaxunit
```

Нельзя автоматически искать во всём workspace.

Расширение поиска допускается только при evidence, что соседний repository является реальной dependency текущей конфигурации или tested behavior.

Нахождение метода в другом repository не расширяет mutation scope.

### FR-REUSE-006. Non-1C repositories

Reuse-gate для 1С не должен активироваться в `kafka-adapter-tests-reports`, `kafka-adapter-tests-ui` или иной non-1C задаче только потому, что workspace содержит 1С repositories.

Для non-1C задач действуют их собственные language/runtime reuse mechanisms и repository instructions.

### FR-ERR-001. Error taxonomy

Каждая material workflow error классифицируется:

```text
recoverable-workflow
correctable-invocation
transient-retryable
infrastructure
authority-contradiction
unsafe-or-out-of-scope
unknown
```

### FR-ERR-002. Recoverable workflow

`recoverable-workflow` автоматически устраняется, если recovery входит в уже утверждённый scope, не destructive, не high-risk, не требует новых credentials или пользовательских данных, не изменяет user intent и допускает authoritative validation после восстановления.

Примеры: target ещё не adopted, объект текущей задачи ещё не создан, toolset ещё не включён, documented prerequisite ещё не выполнен.

После recovery выполняется focused validation, затем работа продолжается.

### FR-ERR-003. Correctable invocation

Для `correctable-invocation` допускается одна исправленная попытка без обращения к пользователю, если ошибка однозначно определяется JSON Schema, tool guide, error message или уже установленным routing.

После второй ошибки автоматическое угадывание прекращается.

### FR-ERR-004. Transient retry

Автоматический retry допускается только если ошибка явно transient и operation idempotent либо documented safe-to-retry.

По умолчанию `max automatic retry = 1`.

Mutation не повторяется автоматически, если неизвестно, был ли write применён. Timeout write-operation считается `indeterminate` до authoritative verification.

### FR-ERR-005. Blocking errors

Обязательная остановка для `infrastructure`, `authority-contradiction`, `unsafe-or-out-of-scope` и `unknown`.

Infrastructure включает unavailable EDT, required project `not ready`, stale/incomplete required index и недоступный required normative source.

Authority contradiction включает конфликт обязательных authoritative results.

Unsafe/out-of-scope включает destructive operation, credentials, database mutation вне scope, новый repository mutation, branch operation и изменение user-owned configuration без разрешения.

### FR-ERR-006. No artificial user-trigger gate

Новый user-triggered run не нужен после успешно обработанного `recoverable-workflow`, `correctable-invocation` или разрешённого `transient-retryable`.

Новое сообщение пользователя требуется только если нужны новые данные, новое разрешение, scope expansion, manual external recovery или разрешение contradiction.

### FR-POL-001. Strict compliance schema

`validate_compliance` должен публиковать explicit schema ledger item минимум с `rule_id`, `selection_digest`, `target`, `status`, `evidence`, optional `reason` и `additionalProperties: false`.

Mandatory requirements runtime допускают только `passed`.

Recommended допускают `passed` и `deviated`; `deviated` требует непустой `reason`.

### FR-POL-002. Schema, description и runtime должны совпадать

Недопустима ситуация, когда schema разрешает значение, которое обычный documented runtime contract затем отклоняет.

Если JSON Schema не может выразить contextual restriction, tool description должна явно перечислять допустимые варианты.

### FR-POL-003. Compliance phase

Compliance API должен различать `proposal` и `result`. Ошибка должна указывать phase.

### FR-POL-004. Immutable selection reuse

Post-validation использует тот же selection digest, если applicability не изменилась.

Повторный `select_*_requirements` запрещён без нового/изменённого mechanism, registry version change, artifact/operation scope change, contradiction или invalidation.

### FR-POL-005. Normative evidence reuse

После успешной загрузки полного mandatory selector из `v8std` его текст считается reusable для selection в текущей task/session.

Повторно загружать его перед result validation запрещено без invalidation.

### FR-POL-006. Process risk tiers

Вводятся process tiers. Они регулируют orchestration cost и не меняют normative strength.

#### Tier L — low-risk local

Кандидаты: test-only delegate/wrapper, test registration, testability seam, internal test helper и локальное изменение тестовой инфраструктуры без production contract.

Tier L запрещён при production public API, changed production method contract, metadata schema, query behavior, explicit transaction, privileged/full-access behavior, client/server boundary, module persistent state, access/security change, external protocol contract, cross-repository behavior и destructive operation.

Workflow Tier L:

```text
bounded inspection
-> reuse-gate if applicable
-> requirements selection
-> normative evidence load once
-> proposal compliance
-> focused EDT baseline
-> atomic mutation
-> focused EDT result diagnostics
-> result compliance using unchanged selection/evidence
-> focused behavior test
```

Не требуется повторный full normative retrieval и repeated selection без applicability change.

#### Tier M — normal behavior change

Используется полный current pre/post workflow с result detection и compliance.

#### Tier H — high-risk

Дополнительно применяются существующие SDD, impact analysis, architecture review, fresh reviewer, extended validation и multi-repository controls.

### FR-POL-007. Conservative promotion

Tier определяется не размером diff. Любой high-risk mechanism повышает tier. Если risk нельзя уверенно определить, используется более строгий tier.

### FR-POL-008. Detection payload optimization

Policy implementation должна уменьшить повторный model-facing payload critical mechanism coverage.

Допустимы compact canonical detection, reusable digest, opaque stateless token или разделение verbose evidence и reusable status.

Недопустимо считать отсутствие text cue доказательством `absent`, скрывать unresolved mechanisms, ослаблять contradiction detection или принимать недоказанный mechanism state.

Реализация выбирается после benchmark.

### FR-POL-009. Equivalent compliance calls

Эквивалентный request определяется минимум по phase, selection digest, target, ledger semantics и current applicability.

Повтор successful equivalent compliance call в одной стадии является orchestration defect.

Server-side dedup не обязателен, если MCP остаётся stateless.

### FR-EDT-001. Progressive disclosure

Если текущий EDT-MCP поддерживает progressive disclosure/toolsets, workflow должен начинаться с минимального доступного tool surface.

Не фиксируется единый список toolsets для всех проектов: минимальный набор определяется текущим route и задачей.

Общий принцип: `core/read essentials + только необходимые task-specific toolsets`.

### FR-EDT-002. Toolset state reuse

После успешного включения toolset его состояние считается established до server restart, reconnect, explicit error или contradictory status.

Не выполнять повторный `enable_toolset` без invalidation.

### FR-EDT-003. Environment limitation

Если progressive disclosure выключен server-side, не управляется client config или недоступен в используемой версии, это должно быть явно обнаружено doctor/runtime check.

Не считать десятки exposed tools production-optimal состоянием молча.

### FR-EDT-004. No unsafe hiding

Tool exposure optimisation не является authorization. Нельзя скрыть единственный sanctioned tool обязательной операции так, что агент будет вынужден использовать filesystem, shell, другой MCP или unsafe fallback.

### FR-WS-001. Adapter contour

Проверить routing через `kfk-edt`, reuse через `kfk`, `kfk-base`, `kfk-examples` только по необходимости, отсутствие duplicate discovery между code-index и EDT и корректную остановку при недоступном `kfk-edt`.

### FR-WS-002. Conversion contour

Проверить routing через `conv-edt`, reuse через `kfk-conv` и `kfk-conv-kd`, сохранение repository boundaries и отсутствие автоматического перехода на adapter/unit aliases.

### FR-WS-003. Unit contour

Проверить routing через `unit-edt`, primary reuse через `kfk-unit`, bounded reuse tested dependencies, recoverable adopted-object scenario, YAxUnit requirement flow и отсутствие mutation upstream `kfk-yaxunit`.

### FR-WS-004. Non-1C contours

Для `kafka-adapter-tests-reports` и `kafka-adapter-tests-ui` проверить, что 1С-specific skill не активируется без 1С-задачи, EDT/code-index/v8std не вызываются только потому, что workspace содержит 1С, а общие discovery/error rules применяются без 1С-specific overhead.

### FR-OBS-001. Canonical regression scenarios

В `kafka-tools` создаются deterministic/simulated scenarios минимум для:

1. reuse существующего exported method;
2. отсутствие reusable candidate;
3. candidate найден, но context/signature несовместим;
4. recoverable missing adopted object;
5. unavailable EDT;
6. stale code-index;
7. invalid compliance status;
8. low-risk test wrapper;
9. normal query change;
10. high-risk metadata/public API change;
11. repeated discovery после established fact;
12. repeated requirement retrieval;
13. repeated requirement selection без invalidation;
14. mutation timeout;
15. cross-repository reusable candidate;
16. adapter route;
17. conversion route;
18. unit route;
19. non-1C report/UI task.

Тесты не обязаны использовать реальную LLM. Предпочтительны deterministic policy tests, trace fixtures, schema validation и simulated tool result sequences.

### FR-OBS-002. Metrics

Для canonical scenario измеряются MCP call count, serialized request bytes, serialized response bytes, число normative full-text retrievals, repeated-equivalent calls, discovery fan-out, schema validation failures, retries и число distinct authoritative sources.

Если доступен стабильный tokenizer, допускается token metric. Обязательный baseline — bytes.

### FR-OBS-003. Baseline before implementation

До изменения фиксируется current baseline. После изменения запускается тот же scenario set.

## Нефункциональные требования

### NFR-001. Correctness before cost

Оптимизация не должна ослаблять authoritative routing, обходить mandatory requirement, скрывать diagnostics, принимать stale index как live truth, выполнять mutation без required baseline, blind retry write, обходить concurrency guard или менять strength standards.

### NFR-002. Stateless by default

`kafka-policy` остаётся stateless, если benchmark не доказывает необходимость stateful architecture.

Persistent state требует отдельного ADR с source-of-truth model, invalidation, concurrency, crash recovery, cleanup, privacy и versioning.

### NFR-003. Minimal prompt growth

Исправление не должно состоять из бесконечного увеличения `AGENTS.md`.

Общие invariants размещаются в `AGENTS.md`, operation-specific algorithms — в skills, machine-checkable contracts — в MCP, enforcement — в tests.

### NFR-004. Backward compatibility

Существующие valid calls policy MCP не должны молча менять семантику.

При incompatible contract change меняется version, skills/tests обновляются atomically, installer доставляет согласованный комплект, doctor обнаруживает mixed installation.

### NFR-005. Determinism

При одинаковых registry version, artifact, operation, mechanisms, evidence и ledger результат selection/compliance должен быть идентичен.

### NFR-006. Explainable recovery

Решение продолжить после ошибки должно иметь классификацию recoverable/correctable/retryable, а решение остановиться — material blocking reason.

### NFR-007. Repository boundaries

Reuse не расширяет mutation scope. Поиск existing implementation и разрешение её изменения — разные решения.

### NFR-008. Workspace-wide applicability

Shared policy не должна содержать hard-coded предположение, что active project — `tests/unit/unit`.

Любая project-specific логика должна выводиться из workspace routing и локальных repository instructions.

## Архитектура и дизайн

### A. Responsibility boundaries

```text
LLM orchestration
    |
    +-- discovery/reuse ----------> code-index
    |
    +-- live state/write ---------> assigned EDT-MCP
    |
    +-- normative text -----------> v8std
    |
    +-- applicability/compliance -> kafka-policy
```

`code-index` отвечает за существующие implementations, symbols, references и call/data graphs, но не за live truth или mutation.

Assigned EDT-MCP отвечает за live model, mutation, diagnostics и platform-aware state; конкретный server определяется route текущего project scope.

`v8std` отвечает за normative text и pattern/API documentation.

`kafka-policy` отвечает за applicability, deterministic selection и compliance completeness.

LLM orchestration отвечает за stop conditions, reuse decision, recovery и process tier.

### B. Evidence lifecycle

```text
unknown
   |
   v
established
   |
   v
reusable
   |
   +---- no invalidation ----> reuse
   |
   v
invalidated
   |
   v
re-establish
```

Повторная проверка `reusable` fact без invalidation считается defect. Новый central Memory Bank не вводится.

### C. Reuse-gate placement

Mandatory gate располагается в `$1c-code-change`, поскольку там принимается implementation decision.

`$1c-code-index` содержит bounded search algorithm.

Целевой общий contract:

```text
Перед выбором новой самостоятельной реализации:

1. Определи её observable purpose.
2. Определи текущий project scope через workspace routing.
3. Если поведение потенциально reusable, выполни reuse-check через $1c-code-index
   только по aliases текущего scope и реальных dependencies.
4. Если найден совместимый существующий метод, используй его.
5. Новая реализация допускается только после отрицательного bounded search
   или конкретного contract/context/ownership mismatch.
```

### D. Error state machine

```text
tool result / error
        |
        v
     classify
        |
        +-- recoverable-workflow --> repair prerequisite -> validate -> continue
        +-- correctable-invocation -> correct once -> retry
        +-- transient-retryable ---> one safe retry
        +-- infrastructure --------> STOP
        +-- authority contradiction -> STOP
        +-- unsafe/out-of-scope ---> STOP / authorization
        +-- unknown ---------------> STOP
```

### E. Compliance proportionality

```text
actual mechanisms
       |
       v
deterministic requirements
       |
       +------ always enforced
       |
       v
process tier
       |
       +-- L: eliminate redundant stages
       +-- M: complete current workflow
       +-- H: complete workflow + architecture controls
```

Экономия достигается за счёт elimination of repetition, а не снижения нормативной планки.

### F. Policy schema hardening

`read-only-mcp.mjs` должен публиковать максимально точные schemas, особенно для ledger, phase, status, reason, additionalProperties и mechanism enums.

### G. Progressive disclosure design

Предпочтительный workflow:

```text
assigned EDT starts
   |
   v
minimal core visible
   |
   +-- task requires toolset --> enable exact toolset
   |
   +-- reuse state until invalidation
```

Конкретный toolset зависит от task/project route.

Если это требует изменения внешнего EDT-MCP, сначала должен быть доказан capability gap. Без такого evidence внешний MCP не меняется.

### H. Почему `v8std` не изменяется

Текущий `v8std` уже имеет bounded operations. Проблема состоит в orchestration, повторном retrieval, выборе слишком большого объёма и повторной загрузке unchanged evidence.

Изменение `v8std` отсутствует в implementation plan. Отдельная задача создаётся только если benchmark докажет отсутствующую capability.

## План реализации

### Этап 0. Baseline

До изменения:

1. создать synthetic canonical scenarios;
2. не сохранять raw chat transcript;
3. зафиксировать tool traces;
4. измерить request/response bytes;
5. измерить retrieval count;
6. измерить candidate fan-out;
7. зафиксировать correctness outcome;
8. включить минимум по одному сценарию для adapter, conversion, unit и non-1C contour.

Добавить historical regression, моделирующий guessing loop `compliant -> satisfied -> passed`; после schema hardening такой trace должен стать невозможным.

### Этап 1. Reuse-gate

Изменить `ai/.codex/skills/1c-code-change/SKILL.md`, `ai/.codex/skills/1c-code-index/SKILL.md` и при необходимости краткий invariant в `ai/AGENTS.md`.

Добавить tests: existing exported method, incompatible method, no candidate, trivial exemption, cross-repository candidate и route-specific aliases.

### Этап 2. Error taxonomy

Изменить failure section `ai/AGENTS.md`.

Удалить blanket requirement нового user-triggered run после recoverable failures.

Сохранить fail-closed для infrastructure, authority contradiction, unsafe operation и unknown state.

### Этап 3. Policy schema hardening

Изменить `ai/policy/read-only-mcp.mjs`, добавить explicit ledger schema и обновить owning policy tests.

Проверить rendered MCP schema установленного profile, а не только internal JS functions.

### Этап 4. Compliance tiers

Формализовать L/M/H. Tier L сначала ограничить явно безопасными test/internal сценариями. При сомнении повышать до M/H.

### Этап 5. Payload optimisation

Измерить текущий payload и применять оптимизации в порядке: strict schemas, elimination invalid retries, selection reuse, normative evidence reuse, compact detection representation, stateless opaque token только при необходимости.

Persistent server cache не вводить первым решением.

### Этап 6. Discovery budget

Уточнить `$1c-code-index`: 1–3 terms, default max 5 candidates, one escalation, stop condition, новый unresolved fact перед дальнейшим расширением.

### Этап 7. Workspace routing regression

Добавить сценарии adapter, conversion, unit и non-1C с проверкой корректных EDT/code-index routes.

### Этап 8. EDT tool exposure

Проверить live capability каждого EDT contour: server-side preference, `enable_toolset`, client `enabled_tools`, actual tool list. Если невозможно — диагностировать limitation, не fork внешнего MCP автоматически.

### Этап 9. Installer/doctor

Если появляется новый managed configuration, обновить installer и doctor с проверками idempotency, сохранения unrelated settings, policy/schema version, code-index capabilities и route correctness.

### Этап 10. Documentation

Обновить только durable contracts. Не копировать SDD целиком в README.

### Этап 11. Fresh review

Независимый read-only review проверяет correctness gates, отсутствие hidden state, bounded reuse, безопасный recovery, tier promotion, schema/runtime consistency, benchmark, repository boundaries, workspace-wide applicability и отсутствие 1С-specific overhead в non-1C задачах.

## Совместимость и миграции

### Policy registry

Registry version меняется только если изменяется applicability/mechanism model. Schema hardening без изменения selection semantics может потребовать отдельную protocol/tool version, но не обязана менять registry version.

### Installed profile

Skill и MCP contract обновляются atomically. Doctor обязан обнаруживать mixed installation.

### Existing repository configs

Не изменяются по умолчанию. Любое требование изменить repository-owned `.codex/config.toml` сначала расширяет approved mutation scope.

### `SPEC-0012`

Не модифицируется как active implementation plan и остаётся historical architectural baseline.

## Проверка

### Policy MCP unit tests

Обязательные cases:

- valid mandatory `passed`;
- valid recommended `passed`;
- valid recommended `deviated`;
- `deviated` without reason;
- invalid `compliant`;
- invalid `satisfied`;
- missing status;
- missing evidence;
- unknown property;
- duplicate rule;
- stale digest;
- changed mechanisms;
- proposal phase;
- result phase.

### Skill contract tests

Проверить mandatory reuse-gate, trivial exemption, candidate budget, stop condition, error taxonomy, automatic recoverable continuation, blocking infrastructure, conservative tier promotion, workspace-aware alias selection и отсутствие 1С-specific routing в non-1C task.

### Scenario tests

#### S1. Existing helper

Expected: `search_terms -> get_function -> reuse`. Forbidden: новая helper implementation.

#### S2. Existing incompatible helper

Expected: candidate inspection -> contract mismatch -> bounded continuation.

#### S3. No existing helper

Expected: bounded search -> no suitable implementation -> new implementation allowed.

#### S4. Missing adopted object

Expected: diagnostics -> object absent -> recoverable workflow -> adopt -> focused diagnostics -> continue.

#### S5. EDT unavailable

Expected: stop before mutation.

#### S6. Stale index

Expected: stop indexed workflow. Не выполнять silent duplicate discovery через EDT, если EDT не нужен для отдельного authoritative fact.

#### S7. Invalid compliance status

Input `status = compliant`. Expected schema rejection без guessing sequence.

#### S8. Low-risk test wrapper

Expected Tier L, mandatory requirements enforced, duplicate normative retrieval отсутствует.

#### S9. Query behavior change

Expected Tier M или H; full mechanism detection сохранён.

#### S10. Public API or metadata schema

Expected Tier H и существующие SDD/review controls.

#### S11. Repeated discovery

Second equivalent discovery после established fact считается regression failure.

#### S12. Mutation timeout

Expected `indeterminate -> authoritative verification`; blind retry write запрещён.

#### S13. Adapter route

Expected adapter aliases only as applicable и `kfk-edt`.

#### S14. Conversion route

Expected `kfk-conv`/`kfk-conv-kd` и `conv-edt`.

#### S15. Unit route

Expected `kfk-unit` + required tested aliases и `unit-edt`.

#### S16. Non-1C report/UI task

Expected отсутствие `$1c-routing`, EDT, `v8std` и 1С `code-index` без 1С-задачи.

## Benchmark

### Обязательные метрики

Для каждого canonical scenario:

```text
mcp_call_count
serialized_request_bytes
serialized_response_bytes
full_normative_retrieval_count
repeated_equivalent_call_count
candidate_fanout
schema_failure_count
retry_count
distinct_authoritative_source_count
```

### Acceptance benchmark

Для canonical low-risk 1С scenario новая версия относительно baseline должна:

1. сократить combined serialized MCP bytes минимум на 30%;
2. иметь 0 repeated-equivalent successful discovery calls;
3. иметь 0 schema-guess retries;
4. загружать каждый full normative selector не более 1 раза для unchanged selection;
5. не выполнять repeated requirement selection без invalidation;
6. проверять по умолчанию не более 5 reuse candidates;
7. не уменьшать mandatory authoritative checks.

Дополнительно adapter/conversion/unit scenarios должны выбирать правильные route, а non-1C scenario не должен активировать 1С-specific MCP.

Если снижение 30% не достигнуто, completion требует documented анализа remaining mandatory payload и проверенных альтернатив.

## Риски

### R1. Reuse-gate сам увеличит расход

Mitigation: только reusable behavior, 1–3 terms, максимум 5 default candidates, bounded aliases, early stop.

### R2. Recoverable classification будет слишком смелой

Mitigation: uncertainty => stop; no destructive auto recovery; no credentials; no scope expansion; no blind mutation retry.

### R3. Tier L станет обходом standards

Mitigation: tier влияет только на orchestration repetition; mandatory selector неизменен; high-risk mechanism и uncertainty повышают tier.

### R4. Compact policy потеряет evidence

Mitigation: canonical state остаётся auditable; digest связан с полным state; old/new equivalence tests; unresolved mechanisms не скрываются.

### R5. Progressive disclosure отключит нужный sanctioned tool

Mitigation: management/core остаётся доступен; enable path tested; unsafe fallback запрещён.

### R6. Strict schema сломает installed profile

Mitigation: atomic rollout; version checks; installer tests; doctor mismatch detection.

### R7. Discovery dedup объединит разные вопросы

Mitigation: не вводить hard server-side semantic dedup на первом этапе; bounded orchestration policy; semantic key только после отдельного design.

### R8. Shared policy станет оптимизирована только под unit contour

Mitigation: обязательная workspace regression matrix; adapter/conversion/unit/non-1C scenarios; никаких hard-coded `unit-edt` или `kfk-unit` в shared rules вне route examples.

## Критерии приёмки

Спецификация считается `implemented` только если выполнены все условия:

1. `$1c-code-change` содержит mandatory reuse-gate.
2. `$1c-code-index` содержит bounded reuse workflow.
3. Есть explicit exemptions для trivial local logic.
4. Default candidate budget определён.
5. Reuse search выбирает aliases через workspace routing.
6. Shared policy не содержит hard-coded active `unit` assumption.
7. `AGENTS.md` содержит error taxonomy.
8. Recoverable workflow не требует нового user-triggered run.
9. Infrastructure failures остаются fail-closed.
10. Authority contradictions остаются fail-closed.
11. Unsafe/out-of-scope recovery требует authorization.
12. Blind mutation retry запрещён.
13. `validate_compliance` имеет strict ledger schema.
14. `compliant` и `satisfied` отклоняются без guessing loop.
15. Compliance phase явно различает proposal/result.
16. Unchanged selection переиспользуется.
17. Normative evidence при unchanged selection не загружается повторно.
18. Tier L реализован.
19. Tier L не допускает high-risk mechanisms.
20. Tier determination conservative.
21. Detection/compliance payload измерен до и после.
22. Canonical low-risk benchmark даёт минимум 30% reduction serialized bytes либо оформлено отдельное доказанное исключение.
23. Repeated-equivalent discovery count равен 0 в canonical scenarios.
24. Schema-guess retry count равен 0.
25. Adapter regression выбирает `kfk-edt` и корректные adapter aliases.
26. Conversion regression выбирает `conv-edt` и `kfk-conv`/`kfk-conv-kd`.
27. Unit regression выбирает `unit-edt` и только необходимые unit/tested aliases.
28. Non-1C regression не активирует 1С-specific MCP без 1С-задачи.
29. Existing relevant policy tests проходят.
30. Installer tests проходят при изменении managed configuration.
31. Doctor tests проходят при изменении health/config checks.
32. Relevant code-index tests проходят.
33. Protected `src/**` access policy не ослаблена.
34. Progressive disclosure либо используется, либо limitation явно диагностируется.
35. `v8std` не требуется менять для достижения acceptance.
36. Любое изменение внешнего EDT-MCP вынесено за scope либо отдельно утверждено.
37. Upstream `YAxUnit` source не изменяется.
38. Fresh read-only reviewer не обнаруживает ослабления correctness/safety/authority.
39. Реальный implementation result записан в SDD.
40. Benchmark before/after записан в SDD.
41. Verification gaps записаны явно.
42. `verified` устанавливается только после независимой проверки acceptance evidence.

## Открытые вопросы

### Q1. Нужен ли `classify_change_risk` tool?

Предпочтение — не добавлять новый tool без необходимости. Сначала проверить skill-based conservative classifier. Если classification оказывается сложной, повторяющейся и нестабильной, возможен deterministic policy helper.

### Q2. Как compactly переносить detection state?

Кандидаты: compact canonical object, opaque stateless token, digest + retained evidence или текущий shape. Решение принимается после baseline benchmark.

### Q3. Как включается progressive disclosure используемых EDT-MCP?

Не угадывать config. Проверить каждый contour: `kfk-edt`, `conv-edt`, `unit-edt`; проверить server preference, `enable_toolset`, client `enabled_tools` и actual tool list.

Если это user-owned EDT preference, automatic modification требует отдельного решения.

### Q4. Нужен ли persistent evidence ledger?

На первом этапе — нет. Session evidence остаётся orchestration concept. Persistent shared state требует ADR.

### Q5. Нужно ли менять `v8std`?

Default: нет. Отдельная задача допускается только при benchmark/evidence, что существующие bounded APIs недостаточны.

### Q6. Нужно ли менять EDT-MCP?

Default: нет. Сначала используются доступные server settings, toolsets и client configuration. External MCP change только при доказанном capability gap.

## Результат реализации

2026-09-21 пользователь явно утвердил SPEC-0014 и перевод в `approved`.
Scope исполнения: только файлы Git repositories Kafka; установленный профиль,
workspace-файлы вне repositories и user-owned settings не изменяются.
Репозиторная реализация завершена в working tree `kafka-tools` и `kfk-tasks`;
commits не создавались. Развёртывание и live-приёмка не выполнялись; по указанию
пользователя изменения ограничены файлами репозиториев. Ограничения проверки указаны ниже.

### Реализованные контракты

- Mandatory bounded reuse перед самостоятельным поведением: 1–3 terms, default
  до 5 candidates, одна обоснованная эскалация, проверка совместимости/ownership,
  исключения для trivial glue, запрет расширять mutation scope из-за кандидата.
- Семь категорий ошибок; безопасные recovery/correction/retry продолжаются без
  искусственного user-trigger gate. Infrastructure, contradiction, unsafe и unknown
  блокируют работу; timeout записи требует authoritative verification.
- Policy protocol `2.0.0`: strict ledger/assessments/detection schemas, phase
  `proposal`/`result`, runtime strength/digest/coverage checks. Registry не менялся.
  Legacy phase omission означает proposal; managed skills передают phase явно.
- Выбран stateless `compact-v1`: все 13 именованных assessment tuples с evidence,
  без derived detected/unknown arrays. Verbose остаётся совместимым default.
  Selection/compliance разворачивают compact и проверяют те же инварианты.
  Digest связывает applicability, не является evidence/concurrency proof token.
- Tier L — доказанно локальные test delegates/registration/helpers/seams без
  исключённых механизмов; сохраняет requirements, proposal/result, focused EDT
  baseline/result и behavior tests. M — полный pre/post detection/compliance;
  H — дополнительно SDD/impact/architecture/fresh review и repository controls.
  Неопределённость повышает tier и не разрешает неизвестные mandatory mechanisms.
- Doctor проверяет actual policy schema и согласованность bounded managed skill
  set с исходным комплектом; mixed profile даёт error. EDT exposure показывает
  server/visible tool counts, management filtering и явную непроверенность
  server preference/enable path. Конфигурация и services не меняются.

### Изменённые файлы

В `kafka-tools`:

```text
ai/AGENTS.md
ai/.codex/skills/1c-code-change/SKILL.md
ai/.codex/skills/1c-code-change/references/requirements.md
ai/.codex/skills/1c-code-index/SKILL.md
ai/.codex/skills/1c-routing/SKILL.md
ai/.codex/skills/1c-standards/SKILL.md
ai/.codex/skills/yaxunit-tests/SKILL.md
ai/policy/detector.mjs
ai/policy/selector.mjs
ai/policy/read-only-mcp.mjs
ai/policy/schema.mjs
ai/policy/profile.mjs
ai/policy/README.md
ai/doctor.mjs
ai/mcp/doctor-probes.mjs
ai/tests/test-policy.mjs
ai/tests/test-policy-contract.mjs
ai/tests/test-orchestration.mjs
ai/tests/orchestration-scenarios.mjs
ai/tests/benchmark-orchestration.mjs
ai/tests/fixtures/orchestration-baseline.json
ai/tests/test-doctor.mjs
ai/tests/test-managed-mcp.mjs
ai/tests/test-installation.ps1
ai/README.md
```

В `kfk-tasks` изменён этот SDD. Product repositories, upstream YAxUnit,
`src/**`, registry, external MCP implementations и repository configs не изменены.

### Benchmark before/after

Baseline сохранён **до изменения runtime policy** командой
`node tools/ai/tests/benchmark-orchestration.mjs --capture-baseline`.
Frozen traces — synthetic fixtures, не raw chat и не normative corpus.
После изменения выполняется тот же canonical scenario set.

| Scenario | Calls до → после | Request bytes до → после | Response bytes до → после | Снижение combined bytes |
|---|---:|---:|---:|---:|
| adapter | 37 → 22 | 31246 → 15027 | 9585 → 4321 | 52,61% |
| conversion | 37 → 22 | 31261 → 15037 | 9590 → 4326 | 52,60% |
| unit | 37 → 22 | 31261 → 15037 | 9590 → 4326 | 52,60% |
| reports | 2 → 2 | 124 → 124 | 50 → 50 | 0% |
| UI | 2 → 2 | 114 → 114 | 50 → 50 | 0% |

Для каждого 1С scenario: full normative retrievals 20 → 10 (каждый selector один
раз), repeated successful discovery 1 → 0, schema failures 2 → 0, guessing retries
2 → 0, candidate fan-out 1 → 1, distinct authorities 4 → 4. Requirement selection
2 → 1. Состав target/baseline/mutation/result/behavior checks сохранён. Для non-1C
normative/discovery/schema/retry counters равны 0; один repository источник.

Метрика — JSON bytes tool name/arguments и результата без transport envelope,
startup tool schemas или billed tokens. Policy functions реальные, другие
authority responses синтетические. Legacy trace моделирует наблюдавшиеся
повторы; это не универсальное обещание экономии для реальной LLM-сессии.
Persistent cache и opaque token не понадобились. Отдельно выполнен
`benchmark-context.mjs`: повторяющиеся descriptions assessment schemas сокращены
через `propertyNames` enum и typed `additionalProperties`, без ослабления проверки.
Combined policy/OpenViking static schema — 16297 bytes против 26017 bytes у первой
строгой реализации. Это отдельная static метрика, не добавленная к warm trace экономии.

### Выполненные проверки

| Проверка | Результат |
|---|---|
| `node tools/ai/tests/test-policy.mjs` | passed: существующие selection/compliance gates |
| `node tools/ai/tests/test-policy-contract.mjs` | passed: phases, строгие schemas, compact/verbose equivalence, ошибки, actual stdio tools/list, mixed profile |
| `node tools/ai/tests/test-orchestration.mjs` | passed: synthetic reuse/recovery/tier/route и отрицательные trace cases |
| `node tools/ai/tests/benchmark-orchestration.mjs` | passed: five contours, >=30%, нулевые повторные discovery/guessing, сохранённые checks |
| `node tools/ai/tests/test-doctor.mjs` | passed: readiness/routing/transport tests |
| `tools/ai/tests/test-installation.ps1` | passed: isolated installed MCP schema/skills, idempotency, foreign aliases/settings, rollback, offline и v8std URL preservation |
| `tools/ai/tests/test-code-index.ps1` | passed: daemon/launcher/proxy/lifecycle regression |
| `tools/ai/tests/test-project.ps1` | passed: repository routing и 16 guard cases |

Installer regression сначала обнаружил устаревший тестовый fixture: отсутствовала
обязательная repository BSL LS registration и использовалась Java 21 вместо уже
требуемой Java 25. Исправлен только fixture с корректным форматом версии;
production installer и его operational defaults не изменены. Временные тестовые
профили создавались внутри `kafka-tools`, реальная установка не выполнялась.

### Независимая проверка и verification gaps

Предварительный read-only reviewer подтвердил сохранение compact coverage и
выявил generic assessment schema; замечание исправлено explicit status/evidence
и проверкой имён critical mechanisms, добавлены отрицательные tests.
Итоговый fresh read-only review финального diff и acceptance evidence завершён
без подтверждённых замечаний. Reviewer проверил schema/runtime, compact,
authority/recovery/concurrency boundaries, mixed-profile checks и сценарии.
Выявленный недостаток invalidation coverage устранён: добавлены проверки
релевантного reindex, нерелевантной mutation, registry/selection/evidence invalidation
и сохранения неизменного normative evidence после reconnect.
Reviewer использовал статическую проверку и результаты исполнителя, самостоятельно
tests не повторял. Репозиторная часть принята; live ограничения остаются открытыми.
`git diff --check` также прошёл.

- Live EDT tools для `kfk-edt`, `conv-edt`, `unit-edt` не доступны в tool surface
  этой сессии. Server preference, live toolsets/enable transition не проверены;
  отсутствие клиентского инструмента не выдаётся за доказательство отключённого
  server-side progressive disclosure. Doctor/runtime limitation реализован и
  протестирован на synthetic surfaces; изменение external EDT-MCP не требуется.
- Текущий пользовательский Codex profile не устанавливался/не читался. Rendered
  schema проверена у реальных stdio MCP в изолированной installer fixture, не в
  перезапущенном Codex UI пользователя. Live LLM acceptance не выполнялась.
- `v8std` не менялся и не вызывался: нормативная применимость/strength registry
  сохранены, выполнялись tooling tests, а не изменение 1С или оценка норм.
  Дополнительная сверка с user-provided `V8STD_REPO` не выполнялась.
- `verified` не устанавливается без независимой проверки acceptance evidence.

## Отклонения от спецификации

Гарантии correctness/safety/authority не ослаблены. Live EDT/toolset и пользовательский
UI/profile этапы не выполнялись из-за доступности tools и согласованного repo-only
scope; они перечислены в verification gaps и не считаются подтверждёнными.

Любое отклонение, уменьшающее correctness guarantees ради token cost, требует явного утверждения пользователя и изменения этого SDD до реализации.

## Связанные документы

- `SPEC-0010` — authoritative EDT routing.
- `SPEC-0011` — code-index/BSL LS/v8std routing.
- `SPEC-0012` — Git-backed context plane, deterministic policy enforcement и task orchestration.
- `ADR-0002` — repository documentation and hierarchical agent instructions.
- `ADR-0004` — code-index и BSL LS analysis plane.
- `ADR-0005`/`ADR-0006`/`ADR-0007` — runtime/context-plane decisions, введённые вокруг `SPEC-0012`.
