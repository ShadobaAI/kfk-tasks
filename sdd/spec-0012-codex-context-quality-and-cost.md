---
title: Git-backed context plane, deterministic policy enforcement и task orchestration для Codex
id: SPEC-0012
type: specification
status: in-progress
owner:
created: 2026-09-12
updated: 2026-09-15
github_issue:
affected_repositories:
  - kafka-tools
  - kafka-adapter
  - kafka-adapter-base
  - kafka-adapter-examples
  - kafka-adapter-conv
  - kafka-adapter-tests-unit
  - kafka-adapter-tests-reports
  - kafka-adapter-tests-ui
  - kfk-tasks
affected_components:
  - Codex workspace AGENTS.md
  - Codex repository AGENTS.md
  - Codex skills
  - Codex MCP configuration
  - Codex PreToolUse policy
  - OpenViking local runtime and MCP proxy
  - Git-backed context synchronization
  - deterministic 1C policy selector
  - YAxUnit policy selector
  - compliance gates
  - task handoff artifacts
  - task-scoped Codex workflow
  - multi-agent orchestration for large tasks
  - installer and runtime validation
  - regression and benchmark tests
related_adrs:
  - ADR-0002
  - ADR-0004
  - ADR-0005
tags:
  - specification
  - codex
  - openviking
  - context
  - memory
  - mcp
  - 1c
  - quality
  - performance
  - team-development
sources:
  - "repo:kafka-tools:ai/AGENTS.md"
  - "repo:kafka-tools:ai/README.md"
  - "repo:kafka-tools:ai/PORTING.md"
  - "repo:kafka-tools:ai/.codex/config.toml"
  - "repo:kafka-tools:ai/.codex/skills/1c-routing/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-code-change/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-code-change/references/requirements.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-code-index/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-platform-docs/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/1c-standards/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/bsl-ls-mcp/SKILL.md"
  - "repo:kafka-tools:ai/.codex/skills/yaxunit-tests/SKILL.md"
  - "repo:kafka-tools:ai/workspace-policy.json"
  - "repo:kafka-tools:ai/hooks/guard-1c-routing.ps1"
  - "repo:kafka-tools:ai/mcp/code-index-mcp.ps1"
  - "repo:kafka-tools:ai/mcp/code-index-daemon.ps1"
  - "repo:kafka-tools:ai/mcp/code-index-proxy.mjs"
  - "repo:kafka-tools:ai/tests/test-project.ps1"
  - "repo:kafka-tools:ai/tests/test-installation.ps1"
  - "repo:kafka-tools:ai/tests/test-code-index.ps1"
  - "repo:kafka-tools:ai/tests/smoke-code-index-runtime.ps1"
  - "repo:kafka-adapter:AGENTS.md"
  - "repo:kafka-adapter:.codex/config.toml.example"
  - "repo:kafka-adapter:.codex/skills/bsl-ls-mcp/SKILL.md"
  - "repo:kafka-adapter:.codex/mcp/bsl-ls-proxy.mjs"
  - "repo:kfk-tasks:README.md"
  - "repo:kfk-tasks:AGENTS.md"
  - "repo:kfk-tasks:sdd/README.md"
  - "repo:kfk-tasks:sdd/spec-0007-memory-bank-retirement.md"
  - "repo:kfk-tasks:sdd/spec-0010-codex-1c-routing.md"
  - "repo:kfk-tasks:sdd/spec-0011-code-index-bsl-ls-routing.md"
  - "repo:kfk-tasks:adr/adr-0002-repository-documentation-and-agents.md"
  - "repo:kfk-tasks:adr/adr-0004-code-index-bsl-ls-analysis-plane.md"
  - "https://docs.openviking.ai/en/getting-started/01-introduction"
  - "https://docs.openviking.ai/en/guides/03-deployment"
  - "https://docs.openviking.ai/en/guides/06-mcp-integration"
  - "https://docs.openviking.ai/en/concepts/03-context-layers"
---

# Git-backed context plane, deterministic policy enforcement и task orchestration для Codex

## Краткое описание

Спецификация вводит финальную production-архитектуру Codex для экосистемы «1С: Адаптер Kafka» с двумя равноправными целями:

1. повысить качество анализа, проектирования, изменения и review, особенно при командной и multi-repository разработке;
2. снизить потребление model context и лимитов за счёт удаления повторных чтений, уменьшения постоянного prompt surface, отказа от длинноживущих сессий и загрузки только минимально необходимого контекста.

Решение состоит из четырёх обязательных частей:

- Git-backed OpenViking как локальный, полностью перестраиваемый semantic/hierarchical read-model над committed repository knowledge;
- deterministic policy selector вместо интерпретации больших applicability-таблиц моделью;
- обязательный compliance gate, гарантирующий, что выбранные mandatory requirements не только загружены, но и явно проверены до и после изменения;
- task-scoped Codex sessions и bounded orchestration для больших задач с изоляцией research/review контекста и versioned handoff между разработчиками и сессиями.

После внедрения эта архитектура является единственной поддерживаемой. Legacy-mode, dual-read, dual-write, совместимость со старым Memory Bank, параллельные старые selectors и fallback на прежний workflow не допускаются.

## Контекст

Текущая схема уже имеет сильные production-инварианты:

- workspace-level `AGENTS.md` задаёт единые границы repositories, authoritative MCP, bounded navigation, evidence reuse, failure gates, SDD/ADR lifecycle и запрет прямого filesystem-доступа к защищённым `src/**`;
- `$1c-routing` выбирает ровно один primary authority для конкретного факта и запрещает повторять достаточное evidence в другом MCP;
- EDT-MCP остаётся authoritative live model, единственным persistent writer 1С-проектов и primary diagnostics gate;
- federated `code-index` используется как read-only discovery/structure/reference/impact plane при допустимой eventual consistency;
- repository-local BSL LS является secondary focused analyzer и не заменяет EDT;
- `v8std` является standards/policy corpus и не является project/platform authority;
- `$1c-code-change` организует scoped mutation через EDT с pre/post diagnostics, requirement selection и минимальной behaviour validation;
- `$yaxunit-tests` уже выполняет специализированную orchestration тестовых изменений и загружает pattern IDs по механизму задачи;
- `kfk-tasks` является canonical coordination repository для Issues, SDD и ADR, при этом product knowledge принадлежит owning repositories.

Текущая модель deliberately отказалась от прежнего central Memory Bank: SPEC-0007 и ADR-0002 зафиксировали, что central knowledge store стал stale, дублировал owning documentation и создавал дополнительный MCP/maintenance workflow. Новое решение не должно возвращать эту ошибку в другой форме.

OpenViking допускается только как производный read-model. Любое durable знание, используемое командой, должно иметь canonical Git representation и проходить обычный review/merge lifecycle. OpenViking runtime, semantic sidecars, embeddings, indexes, session storage и иные derived artifacts не являются источником истины и могут быть удалены полностью без потери проектных данных.

## Проблема

### P1. Контекст проекта плохо переживает границы Codex session

Связная задача может собирать полезные project-specific сведения, но длинная сессия постепенно накапливает устаревшие гипотезы, tool output и unrelated context. Бесконечная «domain session» не является допустимой архитектурой: finite context window, compaction и prompt-cache misses делают её одновременно менее надёжной и более дорогой.

Новая сессия, напротив, вынуждена повторно читать часть SDD/ADR/docs и заново устанавливать уже известный project context. При multi-repository и командной разработке эта стоимость повторяется у каждого разработчика и каждой модели.

### P2. Наличие требования в `v8std` не гарантирует его применение

Текущий `requirements.md` и pattern routing внутри `$yaxunit-tests` компенсируют проблему полноты retrieval: skill явно описывает, какие standards/sections/patterns должны быть загружены для конкретных mechanisms.

Однако эта логика исполняется самой LLM:

1. модель должна определить все фактические mechanisms;
2. прочитать applicability table;
3. не пропустить ни одну подходящую строку;
4. корректно дедуплицировать requirements;
5. загрузить полное normative evidence;
6. фактически применить каждое правило к proposal/result.

Это дорого, вероятностно и требует постоянного разрастания prompt-инструкций по мере появления новых правил.

### P3. Retrieval не равен compliance

Даже точное попадание mandatory rule в model context не доказывает, что модель проверила конкретный код по этому rule. Текущий prose-gate снижает риск, но не создаёт машинно проверяемой полноты checklist: обязательное правило может быть найдено, прочитано и затем фактически проигнорировано.

### P4. Большие задачи загрязняют основной context

Impact analysis, исследование legacy-кода, анализ больших diagnostic sets, тестовая работа и независимый review могут создавать значительно больше контекста, чем нужен основной implementation thread. Выполнение всех стадий в одной сессии ухудшает locality и увеличивает стоимость последующих turns.

### P5. Командная разработка требует общего, versioned и branch-aware контекста

Любая память, доступная только локальному агенту, непригодна как shared project knowledge. Командная разработка требует:

- reviewable source representation;
- Git merge/conflict semantics;
- branch awareness;
- воспроизводимость после clone/pull;
- отсутствие скрытого персонального state, влияющего на результат;
- возможность полностью перестроить semantic read-model из repository state.

## Цель

Создать единую production-систему Codex, в которой:

- quality определяется authoritative evidence, deterministic policy selection, explicit compliance gates и независимым review там, где он оправдан;
- project context переживает Codex sessions через Git-backed resources, а не через вечную chat history;
- OpenViking выдаёт минимальный релевантный L0/L1/L2 context, но не владеет durable knowledge и не является project authority;
- deterministic applicability logic выполняется кодом, а не дорогой вероятностной интерпретацией lookup tables;
- mandatory requirements имеют проверяемый lifecycle от selection до post-change verification;
- большие задачи могут декомпозироваться на bounded subtasks без переноса полного transcript между агентами;
- каждый разработчик получает локальный OpenViking index, соответствующий committed `HEAD` его текущих checkout;
- после `git pull`, branch switch или rebase semantic index автоматически приводится к актуальному committed state;
- текущие сильные границы EDT/code-index/BSL LS/v8std сохраняются и усиливаются, а не размываются новым retrieval layer;
- permanent prompt surface и MCP surface остаются минимальными.

## Не входит в задачу

- Создание общей сетевой OpenViking-базы для всей команды.
- Использование OpenViking как canonical storage.
- Использование OpenViking `remember`, session auto-memory или иных writable memory механизмов как durable project memory.
- Индексирование dirty/uncommitted working tree как shared context.
- Замена `code-index` semantic search по исходному коду generic RAG.
- Замена EDT live model или EDT diagnostics OpenViking, code-index либо BSL LS.
- Перенос `v8std` standards corpus в OpenViking.
- Сохранение raw MCP output, chain-of-thought/reasoning logs, secrets, credentials, абсолютных локальных путей либо персональной конфигурации в Git-backed context artifacts.
- Создание нового общего Memory Bank.
- Построение постоянной команды долгоживущих «backend/test/reviewer» agents.
- Введение Paperclip или иного отдельного multi-agent control plane.
- Поддержка прежнего managed layout, legacy selectors, dual-read или compatibility shims после cutover.
- Автоматический переход на Git worktrees для 1С-contours: текущие canonical roots и EDT ownership сохраняются.

## Термины и роли

### Canonical state

Versioned данные в Git repositories, которые являются единственным durable source для OpenViking resources и командного handoff.

### OpenViking read-model

Локальный derived semantic/hierarchical index, построенный только из разрешённых committed Git sources. Он предназначен для project-history/context retrieval и не является authority по live code, metadata, platform API или standards.

### Policy registry

Machine-readable versioned mapping `artifact + operation + mechanisms -> required normative IDs/sections/patterns`.

### Policy selector

Детерминированный local tool/MCP, читающий policy registry и возвращающий полный, стабильный и дедуплицированный requirement set.

### Compliance selection

Неизменяемый набор selected requirements с digest/version, относительно которого выполняются pre-change и post-change checks.

### Task-scoped session

Codex session, живущая только пока сохраняется один coherent working context. Session не является project memory.

### Handoff

Короткий versioned task artifact с текущим состоянием работы, необходимый для смены Codex session либо разработчика. Handoff не содержит exploratory transcript и удаляется/закрывается после переноса durable knowledge в SDD/ADR/owning documentation.

## Архитектурные инварианты

Ни один пункт ниже не является рекомендацией. Нарушение любого инварианта блокирует acceptance.

1. **Git is canonical.** Любой durable context, влияющий на командную разработку, должен иметь canonical Git representation.
2. **OpenViking is disposable.** Полное удаление OpenViking workspace/index/cache не должно уничтожать единственный экземпляр project knowledge.
3. **Committed state only.** OpenViking shared resources строятся только из tracked committed state выбранных repositories. Dirty working tree не индексируется.
4. **Local branch awareness.** OpenViking каждого разработчика отражает `HEAD` его локальных tracked repositories, а не фиксированный remote `main`.
5. **No OpenViking writes from Codex.** Codex не получает MCP tools `remember`, `write`, `edit` и другие writable/admin tools OpenViking.
6. **No second source of truth.** OpenViking result является retrieval hint/context. Факты о live source, metadata, platform и mandatory standards подтверждаются соответствующим authoritative plane.
7. **One fact, one primary authority.** Существующий routing invariant сохраняется.
8. **EDT is the only 1C writer.** Все persistent 1C mutations остаются только в EDT-MCP.
9. **code-index remains read-only structural analysis.** OpenViking не получает роль call/reference/impact authority для исходного кода.
10. **v8std remains normative corpus.** Exact normative evidence загружается из v8std после deterministic selection.
11. **Deterministic mappings are not prompt prose.** Lookup tables applicability не должны оставаться обязательной частью LLM context.
12. **Mandatory selected rules require explicit status.** Selection не может считаться проверенным без machine-validated complete compliance ledger.
13. **Task sessions are disposable.** Project continuity обеспечивается Git-backed context/handoff, а не неограниченной chat history.
14. **No compatibility mode.** После cutover старый workflow не поддерживается и не выбирается fallback-логикой.
15. **No silent fallback on required infrastructure failure.** Если required OpenViking/policy-selector scope не готов, зависимая часть задачи останавливается с явной ошибкой.
16. **Unmanaged user configuration and secrets are preserved.** Отказ от backward compatibility относится к managed архитектуре; installer не имеет права уничтожать unrelated user config/credentials.

## Область изменений

### `kafka-tools`

Repository владеет общей реализацией:

- OpenViking manifest/config templates и local runtime integration;
- OpenViking read-only MCP proxy/allowlist;
- Git revision reconciliation/sync;
- deterministic policy registry;
- policy selector MCP/tooling;
- mechanism detection helpers;
- compliance validation tool;
- `task-orchestration` skill;
- обновлённые shared skills и references;
- обновлённый `workspace-policy.json`;
- PreToolUse guard;
- installer/update commands;
- static/runtime regression tests;
- production documentation.

### `kfk-tasks`

Repository остаётся владельцем:

- Issues/task coordination;
- SDD;
- ADR;
- bounded task handoff artifacts, если работа должна пережить session/developer boundary.

Новый general-purpose Memory Bank запрещён. Durable product knowledge по-прежнему перемещается в owning repository documentation, architecture decisions — в ADR, significant requirements/design/results — в SDD.

### Product/test repositories

Repository-local `AGENTS.md` и `.codex` меняются только в части, необходимой для нового routing/context lifecycle. Product source не меняется этой SDD.

## Целевая архитектура

```text
                         Canonical Git state
                                |
        +-----------------------+------------------------+
        |                       |                        |
    kfk-tasks               owning repos            kafka-tools
 Issues/SDD/ADR/work      product/test docs      AI policy/runtime
        |                       |                        |
        +-----------------------+------------------------+
                                |
                         reconcile committed HEAD
                                |
                                v
                         OpenViking local
                       disposable read-model
                                |
                                v
                              Codex
                                |
       +----------------+-------+---------+----------------+
       |                |                 |                |
  code-index           EDT              v8std            BSL LS
structure/impact   live/write/diag   normative text   secondary BSL
                                |
                                v
                         policy selector
                                |
                                v
                         compliance gate
```

Для больших задач поверх этой схемы допускается bounded orchestration:

```text
                         Task session
                              |
                        dependency DAG
             +----------------+----------------+
             |                |                |
       research worker   implementation   test/review worker
             |                |                |
             +---------- structured results --+
                              |
                        integration gate
                              |
                         fresh reviewer
```

## Функциональные требования

### FR-OV-001. Локальный OpenViking runtime

1. OpenViking запускается локально на машине разработчика и не является общим командным mutable server.
2. Windows является обязательной поддерживаемой платформой.
3. Используется официальный prebuilt runtime/package path; source build не является штатным способом установки.
4. Каждый полный запуск installer обязан запросить official PyPI metadata и выбрать текущий latest stable release. Конкретная версия не закрепляется в Git; prerelease, yanked и неподходящие Windows artifacts запрещены.
5. OpenViking configuration template хранится в `kafka-tools`; secrets, API keys, OAuth state и machine-specific credentials в Git не хранятся.
6. Embedding/VLM/provider configuration является локальной user-owned конфигурацией. Installer обязан валидировать её readiness, но не должен угадывать provider/model/credentials.
7. OpenViking storage/workspace размещается вне product repositories и не коммитится.
8. OpenViking runtime должен иметь health/readiness check, используемый installer и MCP proxy.

### FR-OV-002. Read-only MCP surface

1. Codex получает только минимальный read-only OpenViking surface: `find`, `search`, `read`, `list`, `tree` либо эквивалентный официальный read-only набор после проверки фактической версии.
2. `remember`, `write`, `edit`, session commit, memory extraction, administrative mutation и любые новые writable tools не экспонируются Codex.
3. Ограничение выполняется proxy/allowlist, а не только prompt-инструкцией.
4. PreToolUse guard является дополнительным deny barrier для известных OpenViking write/admin tools.
5. Обновление OpenViking не расширяет allowlist автоматически. Изменение фактической MCP surface требует явной переклассификации и regression tests.

### FR-OV-003. Source manifest

1. Все индексируемые Git resources объявляются в versioned manifest под `kafka-tools/ai/openviking/`.
2. Manifest использует repository-relative paths/identifiers и не содержит абсолютных локальных путей.
3. Для каждого source явно задаются include/exclude patterns; broad recursive indexing всего workspace запрещён.
4. Initial source set обязан включать:
   - `kfk-tasks/sdd/**/*.md`;
   - `kfk-tasks/adr/**/*.md`;
   - active bounded handoff artifacts, определённые этой SDD;
   - selected owning repository `README.md`/`docs/**/*.md`;
   - selected `kafka-tools/ai` architecture/operational docs.
5. 1C serialized source under protected `src/**` не индексируется OpenViking.
6. `.codex/skills` не копируются в OpenViking как второй executable skill source. Skills остаются canonical Codex skills в Git и загружаются штатным механизмом Codex.
7. `v8std` corpus не дублируется в OpenViking.

### FR-OV-004. Git reconciliation

1. Для каждого configured source repository локально хранится `indexed_revision`.
2. Перед использованием OpenViking context proxy обязан сравнить `indexed_revision` с текущим committed `HEAD`.
3. После `git pull`/merge выполняется eager incremental sync через repository Git hook/dispatcher или эквивалентный managed trigger.
4. После checkout выполняется sync до текущего `HEAD`.
5. После rebase/amend/post-rewrite выполняется sync до нового `HEAD`.
6. Git hooks считаются optimization, а не correctness boundary: pre-use reconciliation обязателен даже если hook не выполнился.
7. Incremental sync использует tracked Git diff между indexed revision и current `HEAD`:
   - added -> ingest;
   - modified -> replace/reindex;
   - deleted -> remove;
   - renamed -> remove old + ingest new, если OpenViking API не предоставляет доказанно атомарную rename-семантику.
8. Если old revision недоступен, history rewritten, source manifest/schema/runtime version изменены либо index integrity не подтверждается, incremental sync запрещён и выполняется full rebuild соответствующего namespace.
9. Dirty/untracked files не попадают в shared index и не меняют `indexed_revision`.
10. Sync должен быть идемпотентным.
11. Неуспешный partial sync не может пометить source как ready/current.

### FR-OV-005. Readiness semantics

OpenViking proxy возвращает/поддерживает состояния минимум:

- `ready` — runtime healthy и все required sources соответствуют current committed HEAD;
- `stale` — хотя бы один required source имеет revision mismatch либо pending failed sync;
- `error` — runtime/index/configuration непригодны для retrieval.

`stale` и `error` запрещают использовать OpenViking result как актуальный task context. Агент не должен заменять failed OpenViking broad filesystem scan всего workspace.

### FR-OV-006. Retrieval policy и context budget

1. OpenViking применяется только для project history, architecture context, SDD/ADR, previous investigation, documented constraints и handoff.
2. Для current code structure/callers/references/impact используется `code-index`, а не OpenViking.
3. Для live state/metadata/write/primary diagnostics используется EDT.
4. Retrieval выполняется progressive disclosure: сначала semantic candidate/compact tier, затем более глубокий уровень только если он управляет следующим решением.
5. `search` в injection/context mode обязан получать явный `max_tokens`/эквивалентный bounded budget; безлимитный context assembly запрещён.
6. Full L2 document read допускается только когда конкретный документ/раздел подтверждён как необходимый и более компактного уровня недостаточно.
7. OpenViking не вызывается для задачи, где repository/history context не влияет на решение.
8. Один и тот же project fact не должен повторно извлекаться из OpenViking, если достаточное current-session evidence остаётся валидным.

### FR-TASK-001. Versioned handoff

1. Для работы, которая должна пережить Codex session boundary либо передачу другому разработчику, создаётся bounded tracked handoff artifact в `kfk-tasks/work/`.
2. `kfk-tasks/work/` не является general-purpose knowledge base. Один файл соответствует одной активной task/Issue/approved SDD workstream.
3. Handoff содержит только:
   - task/issue/spec identifiers;
   - current status;
   - affected repositories;
   - committed revisions, относительно которых выводы валидны;
   - completed work;
   - changed contracts;
   - accepted decisions, если они ещё не оформлены durable ADR/SDD update;
   - unresolved questions;
   - next actions;
   - verification already performed и gaps.
4. Handoff не содержит raw MCP output, reasoning logs, full code dumps или speculative exploration history.
5. Handoff обновляется только через Git и проходит обычный team review/merge semantics.
6. После завершения task полезные durable conclusions переносятся в SDD result, ADR или owning documentation. Active handoff удаляется; Git history остаётся достаточным historical audit trail.
7. OpenViking индексирует только committed handoff version.

### FR-TASK-002. Task-scoped sessions

1. Codex session должна обслуживать один coherent working context, а не постоянную domain role.
2. Независимая новая feature/bug/investigation начинает новую session, если большая часть предыдущего context не нужна.
3. Session history не считается durable project knowledge.
4. При необходимости продолжить работу после закрытия/compaction новой session передаётся только Git-backed handoff + authoritative sources, а не transcript.
5. Session не должна сохраняться только ради cache reuse, если её active context преимущественно устарел/нерелевантен.

### FR-POL-001. Machine-readable policy registry

1. Applicability mapping из текущего `1c-code-change/references/requirements.md` переносится в versioned machine-readable registry.
2. Pattern routing из `$yaxunit-tests` переносится в тот же policy subsystem либо отдельный typed registry.
3. Registry обязан представлять минимум:
   - artifact type;
   - operation;
   - mechanisms;
   - mandatory/recommended strength;
   - exact v8std document IDs;
   - exact corporate document/heading selectors;
   - exact YAxUnit pattern IDs;
   - applicability conditions/dependencies;
   - stable registry schema/version.
4. Все строки/условия существующих selector tables должны быть мигрированы без потери semantics. Миграция подтверждается table-driven tests.
5. После cutover старые prompt-based applicability tables удаляются. Dual selection запрещён.

### FR-POL-002. Deterministic selector MCP

В `kafka-tools` реализуется небольшой local read-only MCP с минимальным tool surface. Обязательные tools:

- `select_1c_requirements`;
- `select_yaxunit_requirements`;
- `validate_compliance`;
- mechanism detection tool(s), если они не реализованы внутри первых tools.

Selector обязан:

1. принимать explicit artifact/operation/mechanisms;
2. возвращать union всех applicable requirements;
3. выполнять deterministic deduplication и stable ordering;
4. возвращать registry version и selection digest;
5. разделять mandatory/recommended evidence;
6. возвращать exact selectors, достаточные для прямого retrieval из v8std без ranked search, если applicability уже определена;
7. fail closed при неизвестном schema, неизвестном required mechanism либо incomplete registry data;
8. не обращаться к web/RAG и не использовать LLM внутри selector.

### FR-POL-003. Mechanism detection

1. Requirement selection не может зависеть только от свободной классификации LLM.
2. Effective mechanism set формируется как union:
   - explicit mechanisms из task/design;
   - model-classified mechanisms;
   - deterministic detected mechanisms.
3. Первая production schema обязана покрывать как минимум:
   - query presence;
   - query inside loop/batching;
   - exception handler;
   - explicit transaction;
   - exported method/contract;
   - module variable;
   - privileged mode/full-access context;
   - temporary storage/universal container;
   - client/server boundary/annotation;
   - changed method signature;
   - query result processing;
   - predefined values, если detection достоверно реализуем.
4. Detector не читает protected `src/**` через generic filesystem. Источник текста/structure должен поступать из already-authorized EDT/code-index/BSL LS evidence либо через специализированный read-only integration, не создающий второй source authority.
5. Detector обязан быть conservative: невозможность доказать отсутствие mechanism не может превращаться в ложный `false`. Неопределённость возвращается как `unknown` и блокирует зависимый compliance gate до разрешения.
6. Regex-only detector допускается только для syntax, где tests доказывают отсутствие опасных false negatives; иначе нужен parser/structured evidence.

### FR-POL-004. Exact normative retrieval

1. После selector агент загружает только exact selected evidence из `v8std`.
2. Ranked semantic search не используется для уже выбранных IDs/headings.
3. Evidence считается complete только при существующих текущих completeness checks (`found=true`, отсутствие truncation и т.п.).
4. Uncovered mechanism или missing exact normative evidence блокирует design/mutation/review, как и сейчас.
5. OpenViking никогда не заменяет normative retrieval.

### FR-COMP-001. Compliance ledger

Для каждой selection создаётся structured ledger. Минимальная запись mandatory rule:

```yaml
rule_id: std436
selection_digest: <digest>
target: <construct/symbol>
status: passed | violated | unresolved
evidence: <bounded explanation/reference>
```

Требования:

1. Mandatory selected rule не может быть silently omitted.
2. `validate_compliance` сверяет полный набор ledger entries с selection digest.
3. `violated` и `unresolved` для mandatory rule блокируют mutation либо completion соответственно.
4. `not-applicable` не является допустимым статусом для уже selected mandatory rule. Если applicability изменилась, выполняется новая selection с явным reason и новым digest.
5. Recommended rule может быть сознательно отклонён только с explicit reason, сохраняя stated strength.
6. Перед mutation проверяется proposal/pre-change ledger.
7. После mutation проверяется actual result по тому же selection digest.
8. Если implementation добавила mechanism, effective mechanism set только расширяется, пока специальная reclassification не докажет, что прежний mechanism больше не существует. Новый selector result обязан включать прежние ещё применимые requirements и новые requirements.
9. Успех tool write/diagnostics/tests не заменяет compliance validation.

### FR-SKILL-001. Thin skills

После внедрения selector/compliance:

- `$1c-routing` остаётся dispatcher authority и получает отдельную ветку OpenViking только для historical/project context;
- `$1c-code-change` хранит workflow/gates/authority semantics, но не содержит deterministic applicability table;
- `$1c-standards` хранит retrieval/completeness semantics, но не пытается заново вывести уже определённую applicability;
- `$yaxunit-tests` хранит domain workflow/test gates, но его pattern routing table удаляется в пользу selector;
- `$1c-code-index`, `$1c-platform-docs`, repository-local `$bsl-ls-mcp` сохраняют узкие текущие роли;
- shared `bsl-ls-mcp` не должен конкурировать с repository-local override в `kafka-adapter`.

Новый `$task-orchestration` skill должен быть маленьким и не содержать 1С-specific normative logic.

### FR-ORCH-001. Large-task orchestration

Orchestration активируется только если задача имеет хотя бы одно из свойств:

- несколько независимых/substantially separable workstreams;
- multi-repository implementation;
- большой research, который существенно загрязнит основной context;
- независимый review materially повышает quality;
- параллельная работа действительно сокращает critical path.

Для малых scoped changes orchestration/subagents запрещены как default overhead.

### FR-ORCH-002. Subtask contract

Каждый spawned/forked worker получает bounded packet:

```yaml
goal:
scope:
known_facts:
constraints:
authoritative_sources:
expected_output:
```

Worker возвращает только:

```yaml
conclusion:
evidence:
risks:
unknowns:
```

Полный transcript worker не импортируется в main thread.

### FR-ORCH-003. Independent reviewer

Для public API, schema, multi-repository, complex logic и иных high-risk изменений fresh reviewer обязателен.

Reviewer получает:

- acceptance criteria;
- selected mandatory/recommended requirements;
- diff/result artifacts;
- diagnostics/tests summary и evidence;
- relevant handoff/SDD sections.

Reviewer не получает implementation reasoning transcript. Review является read-only; findings не исправляются автоматически без отдельной authorized implementation phase.

### FR-MCP-001. Минимальный permanent MCP surface

1. Постоянная tool surface должна содержать только реально используемые production capabilities.
2. SonarQube остаётся explicit user-operated audit и не должен быть permanent enabled MCP, если его schema передаётся модели при обычной разработке.
3. OpenViking proxy exposes only approved read-only tools.
4. Policy MCP exposes only selector/detector/compliance tools.
5. Новые tools любых MCP default-deny до классификации.
6. `workspace-policy.json`, config allowlists, PreToolUse guard и tests должны обновляться атомарно с изменением MCP surface.

### FR-INST-001. Installer и managed runtime

`ai/install.cmd` должен стать единственным production setup/cutover entrypoint для новой managed архитектуры.

Installer обязан:

1. установить/обновить managed skills/config/hooks/proxies/policy registry;
2. проверить latest stable OpenViking release, доступность official compatible prebuilt package и опубликованный SHA-256;
3. валидировать local OpenViking config через официальную doctor/health процедуру;
4. не создавать provider/model/API secrets автоматически;
5. установить managed Git hook dispatcher для configured repositories либо эквивалентный eager sync trigger, не затирая unrelated existing hooks;
6. materialize OpenViking source manifest из canonical workspace layout;
7. выполнить initial full sync/rebuild;
8. подтвердить `ready` каждого required source;
9. установить policy MCP и выполнить runtime surface smoke test;
10. удалить superseded managed selector references/config и старые incompatible managed artifacts без compatibility mode;
11. сохранить unrelated user Codex settings и secrets;
12. завершиться ненулевым кодом при incomplete required runtime.

### FR-INST-002. Update command

Добавить отдельную production-команду обновления OpenViking runtime/index по модели `update-code-index.cmd`.

Команда должна:

- обновлять только OpenViking runtime/component;
- при каждом полном запуске проверять latest stable по official PyPI metadata;
- устанавливать новую версию в отдельный versioned directory и сохранять предыдущую для отката;
- выполнять safe restart;
- выполнять required full rebuild при несовместимом index/schema/runtime change;
- подтверждать source readiness после обновления;
- не менять skills/policy-selector без общего installer/cutover;
- поддерживать rollback runtime binary/package/config, но derived index не обязан резервироваться и должен перестраиваться из Git.

## Нефункциональные требования

### NFR-001. Quality first

Снижение лимитов не может приниматься, если regression tests показывают потерю requirement coverage, routing correctness, diagnostics gates или team reproducibility.

### NFR-002. Reproducibility

Два чистых checkout одного набора committed revisions с одинаковой OpenViking/policy version и model configuration должны получать одинаковый source manifest, одинаковые policy selector outputs и эквивалентный OpenViking source corpus. Semantic ranking может иметь допустимую model-dependent variation, но canonical resources и readiness state должны совпадать.

### NFR-003. Bounded context

- broad full-document preload запрещён;
- deterministic tables не должны попадать в prompt для выполнения простого lookup;
- tool output должен возвращать только decision-relevant fields;
- raw diagnostic/search corpora должны агрегироваться bounded worker-ом, если они велики.

### NFR-004. No hidden shared state

Ни один team-critical decision не может существовать только в OpenViking DB, local Codex thread либо local agent memory.

### NFR-005. Performance measurement

До destructive cutover должен быть записан baseline текущей схемы на фиксированном benchmark suite. После cutover выполняется тот же suite.

Обязательные метрики:

- размер always-loaded workspace/repository instruction payload;
- суммарный serialized MCP `tools/list` schema payload активных серверов;
- bytes/tokens policy-selection context, попавших в модель;
- bytes/tokens project-context retrieval, попавших в модель;
- число MCP calls по authority category;
- число duplicate authority calls;
- requirement coverage/pass/failure;
- если Codex предоставляет достоверную usage telemetry — input/cached/reasoning usage отдельно; эта telemetry записывается, но отсутствие undocumented metric не блокирует implementation.

### NFR-006. Security

- no secrets in Git;
- no OpenViking write tools in Codex;
- protected `src/**` filesystem policy сохраняется;
- user-owned OpenViking provider config не включается в shared logs/reports;
- hooks остаются defense-in-depth, а не security sandbox.

### NFR-007. Failure policy

Любой required component (`EDT`, `code-index`, `v8std`, OpenViking для task-context-dependent работы, policy selector, required BSL LS) при `error/stale/incomplete` блокирует только зависимый outcome. Замена другим authority или model memory запрещена.

## Изменения текущих файлов и компонентов

### `kafka-tools/ai/AGENTS.md`

Должен быть сокращён до стабильных workspace invariants: routing/authority, repository boundaries, safety, SDD/ADR gates, failure policy, context lifecycle и high-level compliance requirements. Детальные lookup tables и tool-specific procedures должны жить в skills/references/policy registry.

### `kafka-tools/ai/.codex/config.toml`

Добавить managed OpenViking read-only proxy и policy MCP. Удалить permanent SonarQube из общего/default coding surface, если он туда попадёт через repository-local config. Сохранить `v8std` и `code-index` роли.

### `1c-routing`

Добавить project-context route:

```text
historical/project decisions/SDD/ADR/handoff -> OpenViking
```

Не использовать OpenViking для code structure/live/platform/standards.

### `1c-code-change`

Заменить прямое чтение applicability table на:

1. classify/detect mechanisms;
2. deterministic selector;
3. exact v8std retrieval;
4. pre-compliance gate;
5. mutation;
6. existing diagnostics/tests;
7. post-compliance gate с тем же selection digest.

### `requirements.md`

После миграции registry файл не должен содержать полную mapping table. Он либо удаляется, либо остаётся короткой procedural reference без duplicated deterministic data. Наличие двух canonical mappings запрещено.

### `yaxunit-tests`

Pattern routing переносится в policy registry. Skill сохраняет workflow, authoring constraints, authority и completion gates.

### `bsl-ls-mcp`

`kafka-adapter` repository-local skill остаётся authoritative BSL LS workflow для этого repo. Shared variant не должен загружаться как competing policy.

### `workspace-policy.json`

Расширить typed configuration для:

- OpenViking tracked repositories/source groups;
- policy registry paths/version;
- approved OpenViking MCP read-only tools;
- approved policy MCP tools;
- hook/sync ownership.

Не хранить secrets и absolute machine paths.

### `guard-1c-routing.ps1`

Добавить default-deny для OpenViking write/admin tools и policy MCP tools вне allowlist. Сохранить текущий protected-source и code-index alias enforcement.

### `kfk-tasks/AGENTS.md`

Разрешить только bounded active handoff artifacts в `work/`; явно запретить превращать `work/` в новый Memory Bank. Закрепить lifecycle удаления/промоушена knowledge.

## Новый ADR

До первой implementation mutation должен быть создан и утверждён новый ADR `ADR-0005` со смыслом:

**Git-backed disposable semantic read-model for Codex project context.**

ADR обязан:

- сохранить ADR-0002 ownership model: product knowledge остаётся в owning repositories, SDD/ADR — в `kfk-tasks`;
- supersede только запрет ADR-0002 на dedicated derived knowledge MCP/read-model;
- явно запретить canonical knowledge inside OpenViking;
- закрепить local-per-developer/branch-aware model;
- закрепить read-only Codex surface;
- закрепить отсутствие OpenViking auto-memory как shared project state.

ADR-0004 не supersede: EDT/code-index/BSL LS/v8std authority model сохраняется.

## План реализации

### Фаза 0. Baseline и bounded audit

1. Зафиксировать exact current managed files, active skills, MCP surfaces и tool allowlists.
2. Снять deterministic baseline размеров AGENTS/skills/references и MCP schemas.
3. Сформировать benchmark suite минимум из следующих сценариев:
   - read-only symbol/impact discovery;
   - scoped BSL change;
   - platform API question;
   - YAxUnit authoring/change;
   - design requiring standards;
   - large research with noisy evidence;
   - multi-repository change requiring SDD/handoff;
   - independent review.
4. Проверить, что каждый row текущего `requirements.md` и YAxUnit pattern routing покрыт migration test fixture.
5. Не изменять product source.

### Фаза 1. Architecture decision и repository schemas

1. Создать/утвердить ADR-0005.
2. Добавить `kfk-tasks/work/README.md` и template handoff.
3. Обновить `kfk-tasks/AGENTS.md` с bounded lifecycle.
4. Добавить `ai/openviking/` manifest/schema/config templates.
5. Добавить `ai/policy/` schema/registries.

### Фаза 2. Deterministic policy subsystem

1. Мигрировать 100% текущего 1C applicability mapping в registry.
2. Мигрировать 100% YAxUnit pattern routing.
3. Реализовать selector MCP.
4. Реализовать mechanism detectors и unknown semantics.
5. Реализовать selection digest.
6. Реализовать compliance validator.
7. Добавить exhaustive table-driven tests.
8. Только после pass удалить old deterministic tables из skills/references.

### Фаза 3. OpenViking runtime/read-model

1. Добавить repository-owned latest-stable release policy без фиксированного номера версии.
2. Реализовать local server bootstrap/health wrapper.
3. Реализовать read-only MCP proxy.
4. Реализовать manifest-driven ingestion.
5. Реализовать revision state store вне Git.
6. Реализовать incremental reconciliation.
7. Реализовать full rebuild path.
8. Реализовать managed Git hook dispatcher.
9. Реализовать mandatory pre-use reconciliation.
10. Проверить branch switch, merge/pull, rebase/rewrite, delete/rename и dirty-tree behavior.

### Фаза 4. Skill/routing cutover

1. Обновить workspace `AGENTS.md`.
2. Обновить `$1c-routing`.
3. Обновить `$1c-code-change`.
4. Обновить `$1c-standards`.
5. Обновить `$yaxunit-tests`.
6. Устранить shared/repository BSL LS policy ambiguity.
7. Добавить `$task-orchestration`.
8. Добавить OpenViking/policy servers в managed config.
9. Отключить permanent SonarQube surface для обычной разработки.
10. Обновить guard и allowlist tests.

### Фаза 5. Installer и destructive cutover

1. Обновить `install.cmd` под новую mandatory architecture.
2. Выполнить fresh install test.
3. Выполнить cutover test с текущего committed managed state.
4. Удалить superseded managed mappings/config/artifacts.
5. Не оставлять compatibility flag, legacy selector, fallback skill либо old OpenViking-free managed profile.
6. Rebuild OpenViking from Git.
7. Проверить all required readiness.
8. Перезапустить Codex и подтвердить фактический tool surface.

### Фаза 6. End-to-end quality/cost verification

1. Прогнать baseline benchmark suite на новой архитектуре.
2. Подтвердить 100% selector mapping coverage.
3. Подтвердить compliance fail-closed cases.
4. Подтвердить OpenViking team/branch reproducibility cases.
5. Подтвердить отсутствие duplicate authority retrieval.
6. Сравнить context/tool-schema measurements с baseline.
7. Зафиксировать фактический результат, gaps и deviations в SPEC-0012.

## Командная разработка

### Developer-local state

Каждый разработчик имеет собственные:

- Git checkout/branches;
- OpenViking workspace/index;
- OpenViking provider credentials/config;
- Codex session state.

Shared являются только committed repository artifacts.

### Pull/merge semantics

После получения коллегиных commits:

```text
git pull / merge
    -> managed post-merge trigger
    -> reconcile source revisions
    -> incremental reindex
    -> source ready
```

Если trigger пропущен, первый OpenViking query обязан выполнить reconciliation до retrieval.

### Branch semantics

После branch checkout/rebase OpenViking должен отражать новый committed HEAD. Semantic results с предыдущей ветки не могут считаться ready после revision mismatch.

### Conflict semantics

Knowledge conflict разрешается в Git review/merge, а не в OpenViking. OpenViking никогда не выполняет semantic auto-merge canonical content.

### Handoff semantics

Передача незавершённой работы другому разработчику требует committed handoff. Устного/локального OpenViking memory недостаточно для project-critical state.

## Совместимость и миграции

Обратная совместимость **не поддерживается**.

После утверждённого cutover:

- old prompt-based selector tables не используются;
- old managed skills, противоречащие новой схеме, заменяются;
- legacy Memory Bank/MCP не восстанавливается;
- OpenViking writable memory workflow не поддерживается;
- old MCP config profile без required policy selector/OpenViking не считается поддерживаемым production setup;
- installer не обязан сохранять прежний managed layout и может удалить/заменить его целиком;
- unrelated user config, credentials и unmanaged MCP сохраняются, если не конфликтуют с обязательными security/routing invariants;
- откат выполняется через Git/repository version rollback и повторную установку соответствующего целевого commit, а не через runtime compatibility switches.

## Проверка

### Static/config tests

- TOML/JSON/YAML/frontmatter parse всех managed artifacts.
- Skill validator для всех managed skills.
- Policy registry schema validation.
- Duplicate rule/selector detection.
- Exact coverage test каждого migrated applicability row.
- OpenViking source manifest schema validation.
- Guard positive/negative tests.

### Policy selector tests

Обязательные cases:

- single mechanism;
- multiple mechanism union;
- duplicate rule deduplication;
- stable ordering;
- unknown mechanism fail-closed;
- schema/version mismatch fail-closed;
- changed mechanism expands selection;
- YAxUnit multi-pattern union;
- exact corporate heading selectors;
- mandatory/recommended preservation;
- digest reproducibility.

### Compliance tests

- complete pass;
- omitted mandatory rule -> fail;
- mandatory violated -> fail;
- mandatory unresolved -> fail;
- digest mismatch -> fail;
- stale selection after mechanism change -> fail;
- recommended deviation with reason -> allowed according to strength;
- tool/test success with failed compliance -> still fail.

### OpenViking sync tests

- clean initial build;
- no-op repeated sync;
- add;
- modify;
- delete;
- rename;
- merge/pull;
- checkout branch;
- post-rewrite/rebase;
- missing old revision -> full rebuild;
- changed manifest/schema/runtime -> required rebuild;
- dirty tracked file ignored until commit;
- untracked file ignored;
- partial sync failure leaves stale;
- second clean clone of same revisions produces same source inventory/readiness.

### OpenViking MCP tests

- фактический `tools/list` содержит только approved read-only tools;
- `remember`/`write`/`edit` и admin mutation недоступны;
- guard запрещает известные write/admin calls, если runtime unexpectedly exposes их;
- source mismatch blocks retrieval until reconciliation;
- bounded search respects token/context budget;
- no protected `src/**` resources are indexed.

### Installer tests

- fresh temporary workspace/CODEX_HOME;
- repeated idempotent install;
- missing OpenViking provider config -> explicit failure/readiness message, no guessed config;
- missing runtime -> explicit failure;
- cutover from current managed state;
- preservation of unrelated user config;
- Git hook dispatcher does not destroy unrelated existing hooks;
- full readiness after install.

### End-to-end workflow tests

Минимум:

1. scoped BSL change с mechanism detection, selector, v8std, compliance pre/post, EDT diagnostics и BSL LS;
2. YAxUnit change с selector-driven patterns;
3. historical architecture question, решаемый OpenViking без broad file scan;
4. current caller question, который routes в code-index и не использует OpenViking;
5. platform API question, который routes в EDT docs;
6. stale OpenViking source -> fail/reconcile, не fallback;
7. large research worker возвращает bounded summary, а main context не получает transcript;
8. fresh independent review обнаруживает injected defect;
9. handoff между двумя fresh sessions через committed `kfk-tasks/work` artifact;
10. handoff между двумя clean developer checkouts после pull.

## Риски

### R1. OpenViking превращается в новый Memory Bank

Митигация: read-only Codex surface, Git canonical, explicit source manifest, запрет auto-memory, disposable rebuild, ADR-0005.

### R2. Semantic retrieval скрывает релевантный документ

Митигация: OpenViking не используется для mandatory policy completeness; exact known documents/IDs могут читаться напрямую; SDD/ADR identifiers и source provenance сохраняются.

### R3. Policy registry устаревает относительно v8std

Митигация: registry versioned, exact coverage tests, обязательное обновление selector при новых mandatory work rules, unknown mechanism fail-closed. Наличие нового v8std материала само по себе не изменяет deterministic selection без review policy mapping.

### R4. Detector даёт false negative

Митигация: conservative unknown, union с model classification, parser/structured evidence для сложных mechanisms, regression fixtures из реальных patterns.

### R5. Новый MCP surface увеличит permanent prompt

Митигация: OpenViking proxy только 5 read-only tools, policy MCP минимален, Sonar переводится в opt-in, old deterministic tables удаляются из prompt.

### R6. Git hooks не выполняются

Митигация: hooks только eager optimization; pre-use revision gate является correctness boundary.

### R7. Branch switching оставляет stale semantic context

Митигация: current HEAD comparison перед retrieval; mismatch -> reconcile/stale.

### R8. Handoff превращается в мусорный архив

Митигация: bounded template, one active workstream per file, completion cleanup, durable knowledge promotion, prohibition in `kfk-tasks/AGENTS.md`.

### R9. OpenViking provider расходует отдельные model/embedding ресурсы

Митигация: retrieval используется только для project/history context; source sync incremental; provider/model explicit and measurable; OpenViking не индексирует code/v8std corpora, уже покрытые специализированными systems.

### R10. No-backward-compat cutover ломает локальную среду

Митигация: destructive phase разрешена только после successful temporary fresh/cutover tests и Git-backed recovery path. Compatibility mode всё равно не создаётся.

## Критерии приёмки

Спецификация считается реализованной только при выполнении **всех** условий.

### Architecture

- создан и принят ADR-0005;
- ADR-0002 ownership model сохранён, но запрет derived semantic read-model явно superseded;
- ADR-0004 authority model не нарушен;
- Git является единственным canonical source OpenViking resources;
- OpenViking полностью rebuildable из Git;
- OpenViking writable/memory tools недоступны Codex;
- общий Memory Bank не создан.

### Team development

- после `pull`, checkout и rebase OpenViking автоматически или pre-use гарантированно синхронизируется до committed HEAD;
- dirty/untracked content не попадает в shared context;
- два checkout одинаковых revisions получают одинаковый source inventory и readiness;
- task handoff между разработчиками работает только через committed artifact;
- branch mismatch никогда не возвращает `ready`.

### Policy quality

- 100% текущих rows `requirements.md` мигрированы и покрыты tests;
- 100% YAxUnit routing rows мигрированы и покрыты tests;
- old applicability tables удалены как executable policy source;
- selector deterministic и reproducible;
- unknown/incomplete policy fail closed;
- mandatory compliance omission/violation/unresolved блокируют workflow;
- pre/post validation используют один selection digest либо документированно расширенный successor selection.

### Existing authority quality

- EDT остаётся only writer/primary diagnostics;
- code-index остаётся read-only structural/impact plane;
- BSL LS остаётся secondary focused analyzer;
- v8std остаётся only normative corpus;
- OpenViking не используется для live code/metadata/platform/standards authority;
- protected filesystem guard сохраняется.

### Context/limit efficiency

- deterministic applicability mapping больше не загружается в model prompt как большая table;
- OpenViking retrieval bounded и progressive;
- permanent MCP schema payload после добавления OpenViking+policy не превышает baseline без документированного compensating removal; Sonar/default unused surface должен быть удалён/opt-in;
- duplicate authority calls в benchmark suite отсутствуют;
- large research transcript не импортируется в main session;
- task continuity не требует сохранения бесконечного Codex thread;
- benchmark показывает снижение decision-irrelevant context относительно baseline. Если доступна достоверная Codex token telemetry, median fresh input consumption по benchmark suite должна быть ниже baseline; ухудшение требует rollback/rework, а не waiver.

### Operational

- install/update paths документированы и проверены на Windows;
- installer при каждом полном запуске проверяет latest stable OpenViking и валидирует published artifact digest;
- full rebuild работает после удаления local OpenViking state;
- installer idempotent;
- no compatibility/legacy profile остаётся в managed artifacts;
- unrelated user settings/secrets не повреждаются;
- regression suite проходит полностью.

## Открытые вопросы

Blocking questions отсутствуют. Implementation обязана выбирать конкретные внутренние форматы/proxy details только в пределах инвариантов этой SDD; решения, меняющие ownership, authority boundary, canonical storage либо read/write model, требуют изменения SDD и нового одобрения, а не локальной импровизации.

## Результат реализации

Реализация начата 2026-09-14. По прямому указанию пользователя 2026-09-15
восстановлена исходная архитектура доставки: `kafka-tools/ai/install.cmd` владеет
shared skills, MCP declarations и lifecycle/security hooks. Дополнительный
внешний distribution plane, его пакет, pin, exporter, ownership detector,
специализированные smoke/regression tests, SDD-дополнение и связанный ADR удалены.
Compatibility mode и fallback не сохраняются.

Сохранены остальные решения и результаты SPEC-0012:

- ADR-0005: Git-backed disposable read-only semantic context при сохранении EDT,
  code-index, BSL LS и v8std authority boundaries.
- Bounded handoff template/lifecycle в `work/` и task-scoped sessions.
- `ai/openviking/`: source manifest/schema, latest-stable PyPI policy с проверкой
  official Windows wheel SHA-256, Git HEAD reconciler, read-only MCP на пять tools и Windows
  update entrypoint. Mock tests покрывают initial build, no-op, failure/recovery,
  scope и budget; live runtime acceptance ещё не выполнена.
- `ai/policy/`: versioned registry, deterministic selector, conservative detector
  с unknown coverage для 13 критичных механизмов и compliance ledger с digest.
  Каждая строка имеет strength; `std436` рекомендателен, corporate requirement
  обосновывать однотипные запросы в цикле обязательный. Live EDT detector,
  классификация остальных смешанных правил и реальные pre/post checks остаются.
- Thin policy/compliance/OpenViking skills и `task-orchestration` сохранены в
  canonical `ai/.codex/skills`; read-only reviewer — в
  `ai/.codex/agents/kafka-reviewer.toml`. Runtime acceptance остаётся обязательной.
- `ai/doctor.mjs`/`doctor.cmd` остаются fail-closed preflight исходной архитектуры;
  проверка внешнего distribution CLI и конфликт с штатным installer удалены.
  Полный live doctor для code-index, OpenViking, policy, EDT и BSL LS ещё нужен.
- `test-doctor.mjs` вычисляет workspace root от `import.meta.url`, а benchmark
  использует сохранённые staged skills. Inventory измеряет только байты;
  rendered Codex schemas и billed input tokens ещё не измерены.

Production cutover не выполнен. Остаются штатная installer/runtime integration,
production-установка thin skills и reviewer, live update/hooks, policy acceptance, E2E и
quality/cost benchmark. Пользовательская production-конфигурация при удалении
внешнего distribution plane не переключается.

### Проверки удаления внешнего distribution plane, 2026-09-15

- Прошли `test-project.ps1` (EDT ports/aliases и 16 routing guard cases),
  `test-installation.ps1` (portable/offline/idempotency, конфигурация, AGENTS,
  skill discovery, preservation foreign daemon aliases/settings) и
  `test-code-index.ps1` (daemon/launcher/proxy/lifecycle).
- Прошли `test-doctor.mjs`, `test-policy.mjs` без дополнительного checkout
  cross-check, три OpenViking mock suites, `benchmark-context.mjs` и
  `node --check ai/doctor.mjs`.
- В active toolkit, staged resources, SDD/ADR indexes и repository-local
  `.codex`/`.agents` остаточных ссылок внешней интеграции не найдено.
  Task-owned temporary package installation и два smoke consumer profiles удалены.
- В установленном Codex profile отсутствуют отменённые config/hooks/builtin
  skills. Shared MCP block и guard block присутствуют ровно по одному;
  `v8std` и `code-index` зарегистрированы по одному, routing guard сохранён.
  Все семь действующих shared skills присутствуют. Два installed skill bodies
  (`1c-routing`, `1c-code-change`) отличаются от repository-owned source;
  различия относятся к EDT workflow, не внешнему distribution plane. При этом
  удалении эти существующие различия не перезаписывались.
- Действующие `ai/install.cmd`, `ai/.codex`, `ai/hooks`, `ai/mcp` и `ai/AGENTS.md`
  не изменены относительно Git; production installer не запускался.
- Live `v8std` MCP отвечает (`std436`, `found=true`; bounded smoke response,
  не normative acceptance). Live `code-index.health` вернул MCP `error`, daemon
  `offline / stale_runtime_info / fetch failed`, все семь aliases `unavailable`.
  MCP-зависимая проверка остановлена без restart, переиндексации и подмены authority.
- Полную работоспособность live code-index подтвердить нельзя до recovery и
  нового user-triggered run. Doctor сохраняет `not-ready`: runtime environment
  неполна, EDT/BSL LS остаются unverified; live OpenViking/E2E приёмка не выполнена.
### Штатная installer delivery, продолжение 2026-09-15

- Policy/compliance/OpenViking thin skills и `task-orchestration` перенесены в
  единственный canonical `ai/.codex/skills`; существующий `bsl-ls-mcp` сохранён.
  Все прежние reference-файлы присутствуют. `staged/` удалён без compatibility layout.
- Reviewer преобразован в документированный standalone TOML custom agent
  `ai/.codex/agents/kafka-reviewer.toml` с `sandbox_mode = "read-only"` и без
  model override. Installer доставляет его idempotently с существующим backup.
- `kafka-policy` и `kafka-openviking` добавлены в shared managed MCP template с
  точными read-only allowlists. Installer разрешает Node, toolkit/workspace/state
  paths и отклоняет conflicting same-name MCP вне managed block.
- Добавлен `-OpenVikingStateDir`: developer env или default `<CodexHome>/openviking`.
  Production user profile не переключался; `ConfigurationOnly` не доказывает
  backend readiness и не устанавливает OpenViking provider/package.
- Portable installer regression проверяет реальный installed MCP initialize и
  tools/list из постороннего cwd, exact registrations, paths/allowlists и reviewer.
  Прошли `test-installation.ps1`, `test-policy.mjs`, `test-doctor.mjs`, byte inventory.
  Проверка routing ports/aliases также прошла; backend queries, live EDT evidence,
  actual Codex agent discovery и production cutover остаются непроверенными.
- Источники формата: официальные Codex MCP и custom-agent docs, прочитанные
  2026-09-15. Runtime services code-index/EDT ожидаемо остановлены по сообщению
  пользователя; зависимые live-проверки отложены до запуска, не заменяются mocks.
- Завершающие `test-project.ps1`, `test-code-index.ps1`, syntax check нового
  `test-managed-mcp.mjs` и `git diff --check` прошли. Пользователь подтвердил
  endpoint adapter EDT `http://localhost:8765/mcp`; conversion/unit остаются
  назначенными routes 8767/8768.
- После сообщения пользователя о запуске code-index новая проверка назначенного
  `code-index.health` завершилась `Transport closed`. Это ошибка текущего MCP
  соединения, не доказательство offline daemon. Live readiness aliases не
  установлена; зависимая проверка остановлена до reconnect и нового запуска.
### Продолжение route-aware doctor, 2026-09-15

- Назначенный `code-index.health` в новой сессии подтвердил healthy online daemon
  и `ready` всех семи aliases на canonical paths. Предыдущий `Transport closed`
  больше не является текущим блокером. Evidence действует до restart, reindex,
  reconnect, релевантной mutation или противоречащего результата.
- Пользователь подтвердил запуск трёх EDT endpoints на назначенных портах
  8765/8767/8768. В callable tool catalog этой сессии отсутствуют `kfk-edt`,
  `conv-edt` и `unit-edt`; live readiness и реальные detector/compliance checks
  не установлены. Shell/HTTP-подмена assigned MCP не выполнялась.
- Doctor выбирает canonical contour по project root; workspace требует все три
  EDT, non-1C repositories не требуют EDT. Неизвестный или вложенный root
  отклоняется до dependent checks. Добавлен validator managed code-index health:
  healthy daemon, verified endpoint/process, unique alias, ready exact path.
  CLI transport integration ещё не завершена; наличие файлов не даёт `ready`.
- Отдельный v8std gate остаётся `unverified`: наличие URL не доказывает readiness
  нормативного корпуса. BSL LS gate отражает configured adapter owner;
  дополнительные явно настроенные endpoints требуют отдельной проверки.
- Прошли `test-doctor.mjs`, `node --check ai/doctor.mjs` и `git diff --check` в
  tools/tasks. Проверены contour isolation, workspace/non-1C roots и отказы при
  stale/degraded/missing health, duplicate alias и несовпадении canonical path.
  Fixtures не заменяют live acceptance. Production installer/cutover не запускался.

### Продолжение managed runtime transport, 2026-09-15

- CLI doctor подключён к managed code-index stdio MCP: последовательные
  `initialize`, `notifications/initialized`, затем `tools/call health`.
  Installed launcher вызывается с `-SkipDaemonBootstrap`; daemon bootstrap,
  restart и переиндексация не выполняются. Сессия ограничена 10 секундами и
  1 MiB output; ошибки JSON/envelope/initialize, MCP error, timeout и неполная
  health evidence дают отказ. Для non-1C roots code-index не требуется.
- Назначенный `code-index.health` заново подтвердил healthy online daemon 1.2.2
  и ready всех семи canonical aliases. Новый `probeCodeIndex` через installed
  managed launcher независимо прошёл для того же набора aliases. Это runtime
  transport evidence, не evidence live 1C detector/compliance.
- Portable installed-profile smoke теперь использует последовательный MCP
  handshake. `test-installation.ps1` прошёл: foreign cwd, exact allowlists,
  reviewer delivery, offline/idempotency и preservation unrelated settings.
  Actual Codex discovery и два clean checkout не проверены.
- Исторически OpenViking `0.4.19`, Windows wheel и SHA-256 были сверены с
  [официальной PyPI metadata](https://pypi.org/pypi/openviking/0.4.19/json).
  [Pinned upstream readiness](https://github.com/volcengine/OpenViking/blob/v0.4.19/openviking/server/routers/system.py)
  допускает `not_configured`. Toolkit gate усилен: embedding, vector DB и AGFS
  filesystem должны быть рабочими; missing/not-configured checks блокируют
  semantic readiness. Readiness requests ограничены 15 секундами каждый.
- Live OpenViking readiness для `http://127.0.0.1:1933` вернула `fetch failed`.
  Зависимые live sync/retrieval, provider acceptance, runtime update/restart/
  rollback и source readiness остановлены до recovery и нового user-triggered
  run. Mock sync suite прошёл, но не заменяет эти acceptance gates.
- Fresh read-only reviewer обнаружил malformed `null` envelope и truthy
  malformed initialize. Оба дефекта исправлены, regression fixtures добавлены.
  Повторный review не нашёл блокирующих дефектов Windows route. Transport также
  отклоняет одновременные result/error fields. Forced cleanup ограничен секундой;
  exit всех descendants зависшего launcher не доказан и остаётся verification gap.
- EDT исключён из текущего workstream прямым указанием пользователя. Его
  readiness/detector/diagnostics/compliance остаются отдельным acceptance blocker.
  v8std corpus completeness, BSL LS, eager Git hooks, полный clean-install/update
  E2E и branch/handoff acceptance не подтверждены. Rendered Codex schemas и
  token telemetry не измерены; прежний benchmark остаётся byte inventory.
- Production installer/cutover не запускался. Существующие installed EDT skill
  differences и посторонний SPEC-0013 не изменялись. SPEC-0012 остаётся in-progress.

### Bounded mixed-strength policy check, 2026-09-15

- Назначенный v8std вернул `found=true`, `body_truncated=false` для `std436`,
  `corporate:work:query-conventions:overview` и
  `corporate:work:module-organization:overview`. Это complete evidence этих
  selectors, а не доказательство completeness всего корпуса.
- `std436` допускает исключения и имеет рекомендательную формулировку; отдельное
  corporate requirement обосновывать однотипные запросы в цикле имеет
  `level=mandatory`. Существующие strengths registry для этих правил сохранены.
  Corporate query и module clauses обязательны с указанными в тексте условиями,
  без превращения defaults/исключений в безусловные запреты. Остальные общие
  стандарты и mixed-strength rows этим bounded audit не классифицированы.
- Расширены compliance fixtures: recommended exception не позволяет отметить
  selected mandatory corporate rule как `violated`, `deviated` или
  `not-applicable`; result ledger проверяется по тому же selection digest.
  Это fixture coverage, не реальные EDT pre/post checks. Проверка не читала
  protected project source и не использовала filesystem checkout v8std.
- Прошли расширенный `test-policy.mjs` и повторный installed-profile
  `test-installation.ps1` после строгой проверки MCP envelopes. Bounded handoff
  и предлагаемые границы commits подготовлены в `work/SPEC-0012.md`; изменения
  ещё не закоммичены, committed team continuity этим не доказана.

### Eager Git hook manager, 2026-09-16

- Добавлены repository-owned `install-hooks.mjs` и `hook-dispatch.mjs` для
  `post-checkout`, `post-merge` и `post-rewrite` всех Kafka-owned repositories,
  перечисленных в `hookRepositories`; upstream `tests/unit/yaxunit` исключён.
  Manager устанавливает wrappers только после global preflight, защищён
  cross-process lock и отклоняет OpenViking state внутри workspace.
- Existing hook переносится в `<hook>.kafka-user`, вызывается с исходными
  аргументами, а его exit status сохраняется. Наличие одновременно unmanaged hook
  и sidecar считается конфликтом и блокирует установку до mutation. Повторная
  установка byte-idempotent; ошибка применения запускает rollback и отдельно
  сообщает rollback failure.
- Hook dispatch запускает hidden detached reconciliation и не блокирует Git.
  Это eager optimization: async failure не публикует ready state, а обязательный
  `reconcile()` перед каждым read-only MCP retrieval остаётся correctness boundary.
- `test-openviking-hooks.mjs` прошёл: два изолированных Git repositories,
  сохранение foreign hook/exit status, idempotency, global conflict preflight,
  installation lock, shell quoting, outside-workspace state и dispatch process.
  Live backend и production repositories не изменялись.
- Hooks намеренно ещё не подключены к `install.cmd`: installer пока не выполняет
  OpenViking runtime readiness и initial sync. Активация hooks до этих gates
  нарушила бы ordering FR-INST-001. Production integration и rollback wrappers
  остаются следующей задачей после реализации проверяемого runtime lifecycle.
- `test-openviking-checkouts.mjs` создал два независимых local clones одного
  origin. На одинаковых revisions совпали revision/file-OID inventories; изменение
  tracked working file и untracked document не изменило committed inventory.
  После `pull --ff-only` оба checkout вызвали `post-merge` и снова получили
  одинаковый inventory. Отдельно фактически сработали `post-checkout` при создании
  branch и `post-rewrite` после rebase; оба checkout остались clean. Это local Git
  E2E без OpenViking backend и не доказывает semantic source readiness.

### Pinned OpenViking bootstrap, 2026-09-16

- Host audit без чтения provider config обнаружил Python 3.14.4 и отсутствие
  package/CLI `openviking`, `openviking-server`, `ov`. Поэтому live backend
  acceptance по-прежнему заблокирована отсутствующим runtime/provider setup.
- `version.json` дополнен exact immutable PyPI wheel URL; filename и SHA-256 ранее
  сверены с официальной metadata. Добавлен `install-openviking-runtime.ps1`:
  download либо explicit local wheel, hash-before-execution, staging venv,
  package-version verification, atomic first install и cleanup staging.
- Bootstrap запрещает runtime внутри workspace и отказывается перезаписывать
  существующий target. Он сознательно не читает/создаёт provider credentials,
  не запускает interactive `init`, server или production installer. PowerShell
  syntax и manifest URL/filename tests прошли; network installation не запускалась.
- Owning README содержит точные ручные команды `install -> init -> doctor -> server`.
  После выполнения пользователем нужен новый run для live readiness, initial sync
  и retrieval. Safe update/restart/rollback существующего runtime ещё не реализованы.

### Интеграция полного OpenViking setup в installer, 2026-09-16

- Последующее требование пользователя заменило ручную first-install схему единым
  `tools/ai/install.cmd`. Обычная установка теперь владеет bootstrap latest-stable runtime,
  проверкой exact package version, `doctor`, official interactive `init` при
  отсутствии user-owned config, запуском server, readiness wait, initial Git sync,
  MCP smoke и установкой eager Git hooks в указанном порядке.
- Runtime по умолчанию хранится в `<CodexHome>/openviking-runtime/<version>`, derived
  state — в `<CodexHome>/openviking`. Повторный запуск проверяет update и переиспользует
  versioned runtime, если он уже latest. Existing provider config не
  удаляется и не изменяется; failed `doctor` завершает установку с явной ошибкой.
- Для заранее скачанного artifact поддержан explicit `-OpenVikingWheelPath`, но
  latest metadata всё равно требуется; Python и runtime root можно задать явно. `-ConfigurationOnly` не устанавливает
  runtime и не запускает provider/server/sync/hooks. `-SkipOpenVikingRuntime` является
  явным диагностическим opt-out, а не поддерживаемым production profile.
- Portable `test-installation.ps1` прошёл с isolated fake runtimes, без запуска
  EDT-MCP/code-index и без network download. Embedded PowerShell parser также прошёл.
  Live wheel install/provider/server/retrieval на этой машине не выполнялись, поэтому
  production cutover и live automatic update/restart/rebuild остаются gates.
- Этот раздел заменяет исторические утверждения выше о том, что hooks не подключены
  к installer и provider init выполняется отдельной ручной последовательностью.

### Переход на automatic latest-stable update, 2026-09-16

- Пользователь явно принял риски floating update и потребовал убрать fixed version.
  Это решение заменяет первоначальный pin requirement FR-OV-001 и соответствующие
  operational criteria: `version.json` теперь хранит release policy, а не version.
- Каждый полный `install.cmd` запрашивает `https://pypi.org/pypi/openviking/json`,
  отклоняет prerelease/yanked artifacts, выбирает совместимый official Windows x64
  wheel, сверяет published SHA-256 и устанавливает отсутствующую latest version.
- Runtime directories versioned; предыдущие версии не удаляются. Active version и
  runtime path записываются в disposable `<OpenVikingStateDir>/runtime.json`, поэтому
  doctor, probe, reconciler и MCP проверяют фактически выбранную installer версию.
- Explicit `-OpenVikingWheelPath` не отключает update check: offline artifact обязан
  совпасть с текущим latest metadata. Полностью offline floating-latest install по
  определению не поддерживается, поскольку latest нельзя доказать без metadata.
- После изменения прошли portable installer, manifest policy, mock sync/MCP,
  hook manager, two-checkout Git E2E, doctor, Node/PowerShell syntax и diff checks.
  EDT-MCP/code-index не опрашивались по прямому указанию пользователя; production
  installer и live OpenViking package/provider/server acceptance не запускались.
- Eager hooks устанавливаются по отдельному `hookRepositories` contract во все
  девять Kafka-owned repositories. Upstream checkout `tests/unit/yaxunit` явно
  исключён и не получает managed Kafka hooks.

## Отклонения от спецификации

Внешнее дополнение к distribution отменено прямым указанием пользователя.
Сохраняется архитектура authority/read-only/canonical storage SPEC-0012. Release
policy OpenViking изменена отдельным прямым указанием пользователя на latest-stable;
policy selector, compliance, task-scoped sessions и orchestration не изменены.
## Связанные документы

- `ADR-0002` — repository documentation and hierarchical agent instructions.
- `ADR-0004` — code-index и BSL LS как read-only analysis plane.
- `SPEC-0007` — retirement прежнего Memory Bank.
- `SPEC-0010` — authoritative EDT routing.
- `SPEC-0011` — code-index/BSL LS/v8std routing.
- `ADR-0005` — Git-backed disposable semantic read-model, создан до implementation cutover.
