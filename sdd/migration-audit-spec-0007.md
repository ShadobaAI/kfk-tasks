# Аудит вывода Memory Bank из эксплуатации

Статус: завершён.

Этот отчёт относится только к SPEC-0007 и не является новой базой знаний. Он фиксирует migration classification, точные сохраняемые материалы, MCP deletion set и блокирующие решения.

## Итог

- Проверено 36 Markdown documents в `tasks/memory-bank`.
- 8 файлов SDD/ADR необходимо перенести с сохранением stable IDs и истории.
- Общие agent/process/navigation rules уже перенесены в hierarchical `AGENTS.md`.
- Применён value filter: сохраняются только долговечные, неочевидные boundaries, risks и decisions.
- Inventories, counts, method/field lists, current diagnostics и checkout observations не переносятся, если их легко повторно получить из source/EDT.
- Из architecture documents перенесены только durable architecture/failure/change boundaries.
- Из Conversion Data documents перенесены только attachment и compatibility boundaries.
- Из шести прежних pending items сохранены два durable external compatibility gaps.
- Весь Python/MCP implementation изолирован и может быть удалён после переноса знаний и отдельного подтверждения destructive phase.

## Классификация документов

| Документ | Категория | Решение |
|---|---|---|
| `agents/instructions.md` | `operational-migration` | Общие правила перенесены в workspace/local `AGENTS.md`; удалить после проверки |
| `architecture/background-processing.md` | `value-filtered` | Status/retry/operations уже покрыты product docs; сохранён только durable change-impact checklist |
| `architecture/components.md` | `duplicate` | Component ownership уже покрыт `metadata.md`, `modules.md` и architecture docs; line/method counts отброшены |
| `architecture/data-flows.md` | `value-filtered` | Failure/recovery ownership перенесён в product data-flow documentation |
| `architecture/integrations.md` | `value-filtered` | Durable external compatibility gaps перенесены в SPEC-0008; текущий integration inventory отброшен |
| `architecture/metadata-model.md` | `value-filtered` | Field inventories и counts легко получить из EDT и не переносятся; durable metadata change-impact checklist сохранён |
| `architecture/overview.md` | `value-filtered` | Durable layer/change-boundary sections перенесены в product architecture docs |
| `architecture/public-api.md` | `value-filtered` | API details уже покрыты `api.md`/`direct-api.md`; сохранено только durable compatibility rule |
| `decisions/adr-0001-markdown-canonical-storage.md` | `preserve` | Перенести в `tasks/adr`, отметить superseded новым ADR-0002 |
| `decisions/README.md` | `preserve` | Перенести и обновить index/lifecycle |
| `decisions/template.md` | `preserve` | Перенести в `tasks/adr/template.md` |
| `development/adapter-navigation.md` | `operational-migration` | Routing/bounded navigation уже в `AGENTS.md`; product links остаются в owning docs |
| `development/change-process.md` | `operational-migration` | Перенести применимые lifecycle details в `tasks/sdd/README.md`; остальное уже в `AGENTS.md` |
| `development/conventions.md` | `operational-migration` | Общие правила уже в `AGENTS.md`; product conventions остаются в product docs/source style |
| `development/navigation.md` | `operational-migration` | Workspace map и MCP routing уже в общем `AGENTS.md` |
| `development/testing.md` | `duplicate` | Test ownership в repository README/local `AGENTS.md`; common validation в workspace `AGENTS.md` |
| `glossary.md` | `duplicate` | Канонический product glossary: `adapter/adapter/docs/glossary.md` |
| `maintenance/pending-verification.md` | `value-filtered` | Два durable compatibility gaps перенесены в draft SPEC-0008; четыре быстро устаревающих/easy-to-query observation отброшены |
| `maintenance/update-process.md` | `obsolete` | Заменено SDD result/deviation rules и documentation duties в `AGENTS.md` |
| `project-overview.md` | `duplicate` | Канонические product overview docs находятся в `adapter/adapter/docs/overview` |
| `README.md` | `obsolete` | Удалить вместе с Memory Bank после создания новых SDD/ADR indexes |
| `repositories.md` | `duplicate` | Fixed workspace map находится в root `AGENTS.md`, product ecosystem map — в `adapter/adapter/docs/project/repositories.md` |
| `repositories/conversion-data.md` | `value-filtered` | Base attachment и compatibility risk перенесены; names/versions, доступные через `conv_edt`, не копируются |
| `repositories/kafka-adapter.md` | `duplicate` | README, product docs и current `kfk_edt` являются owning sources |
| `repositories/kafka-adapter-base.md` | `duplicate` | README, local `AGENTS.md` и current `kfk_edt` |
| `repositories/kafka-adapter-conv.md` | `value-filtered` | Adopted-object и compatibility boundaries перенесены; current entry points/diagnostic counts не копируются |
| `repositories/kafka-adapter-examples.md` | `duplicate` | README, local `AGENTS.md` и current `kfk_edt`; current baseline легко проверить повторно |
| `repositories/kafka-adapter-tests-reports.md` | `duplicate` | Repository README и local `AGENTS.md` |
| `repositories/kafka-adapter-tests-ui.md` | `duplicate` | Repository README и current test files; feature count не является durable knowledge |
| `repositories/kafka-adapter-tests-unit.md` | `duplicate` | Repository README и local `AGENTS.md`, включая assembled `tests/unit/base` |
| `repositories/kafka-tools.md` | `duplicate` | Repository README/local `AGENTS.md`; current layout нужно получать из checkout, не из центрального backlog |
| `specifications/README.md` | `preserve` | Перенести в `tasks/sdd/README.md`, обновить lifecycle/index и убрать MCP instructions |
| `specifications/spec-0001-memory-bank-foundation.md` | `preserve` | Перенести как historical SDD, отметить superseded SPEC-0007 без переписывания истории |
| `specifications/spec-0002-simple-kafka-adapter-1-9-2.md` | `preserve` | Перенести и заменить retired Memory Bank links на owning docs/new indexes |
| `specifications/spec-0003-bsl-sonarqube-remediation.md` | `preserve` | Перенести draft и заменить retired Memory Bank links |
| `specifications/template.md` | `preserve` | Перенести в `tasks/sdd/template.md`, русифицировать template для новых SDD |

## Сохранённые product knowledge blocks

### `kafka-adapter`

После value filtering сохранены:

- architecture layers и change boundaries;
- failure/recovery ownership в data flows;
- metadata/queue и worker/status change-impact checklists;
- public API compatibility rule.

Перенос выполнен в:

- `adapter/adapter/docs/overview/architecture.md`;
- `adapter/adapter/docs/overview/data-flow.md`;
- `adapter/adapter/docs/project/contributing.md`.

Не перенесены как неценные для durable documentation: metadata field inventories, object/method/line counts, current entry-point lists и данные, быстро получаемые через `kfk_edt`.

### `kafka-adapter-conv`

В `conversion/KFK/README.md` сохранены:

- `conversion/КД` как base configuration и adopted-object attachment boundary;
- риск совместимости с изменениями линии `КД 3.1+`;
- distinction между contract authoring/generation и Kafka transport.

Не перенесены current metadata versions, diagnostics counts и exported entry-point inventory: они быстро устаревают и должны запрашиваться через `conv_edt`.

## Verification backlog

В draft SPEC-0008 сохранены только два долговечных ограничения:

1. Runtime Kafka/connector validation для baseline `1.9.2+` была waived.
2. Совместимость со всеми обновлениями линии Conversion Data `3.1+` не доказана.

Не сохранены: current platform metadata conflict, diagnostic counts, tools checkout layout и feature count. Эти сведения быстро устаревают либо тривиально повторно получаются из owning repository/EDT.

## SDD/ADR migration set

Перенести без потери stable IDs:

- `memory-bank/specifications/README.md`;
- `memory-bank/specifications/template.md`;
- `memory-bank/specifications/spec-0001-memory-bank-foundation.md`;
- `memory-bank/specifications/spec-0002-simple-kafka-adapter-1-9-2.md`;
- `memory-bank/specifications/spec-0003-bsl-sonarqube-remediation.md`;
- `memory-bank/decisions/README.md`;
- `memory-bank/decisions/template.md`;
- `memory-bank/decisions/adr-0001-markdown-canonical-storage.md`.

Обязательные изменения ссылок:

- SPEC-0001: ADR link переводится на `../adr/adr-0001-...`; retired Memory Bank index link удаляется или заменяется SDD index.
- SPEC-0002: ссылки на public API/repository/testing переводятся в owning repository references либо удаляются как retired local links.
- SPEC-0003: ссылки на repository/testing/change process переводятся в owning docs/new SDD workflow.
- ADR-0001: specification link переводится в `../sdd/spec-0001-...`.

ADR-0001 нельзя оставить единственным `accepted` decision: он прямо требует knowledge under `memory-bank/` и local scanning MCP. Нужен ADR-0002, superseding ADR-0001 и фиксирующий repository documentation + hierarchical `AGENTS.md` + `tasks/sdd`/`tasks/adr` без Memory Bank MCP.

## MCP deletion set

Следующие tracked files относятся только к retired Memory Bank/MCP и могут быть удалены после readiness confirmation:

```text
benchmarks/search_benchmark.py
config/codex-mcp.example.toml
config/repositories.example.json
docs/configuration.md
docs/installation.md
docs/limitations.md
docs/mcp.md
docs/validation-and-tests.md
docs/vscode-obsidian.md
pyproject.toml
run-memory-bank-mcp.sh
src/memory_bank_mcp/__init__.py
src/memory_bank_mcp/api.py
src/memory_bank_mcp/cli.py
src/memory_bank_mcp/evaluation.py
src/memory_bank_mcp/search.py
src/memory_bank_mcp/server.py
src/memory_bank_mcp/store.py
src/memory_bank_mcp/validator.py
tests/__init__.py
tests/search_regression.json
tests/search_regression_real.json
tests/test_api_server.py
tests/test_http_server.py
tests/test_search.py
tests/test_store.py
tests/test_validator.py
```

Дополнительные tracked changes:

- переписать `tasks/README.md` под Issues + SDD + ADR без Python/MCP quick start;
- очистить `.gitignore` от Python/MCP/Obsidian entries, если они больше не нужны;
- удалить весь оставшийся `tasks/memory-bank/**` после переноса 8 сохраняемых файлов.

Сохранить как shared Markdown tooling:

```text
.editorconfig
.gitattributes
.markdownlint.json
.vscode/extensions.json
```

## Readiness status

| Gate | Статус |
|---|---|
| Все Memory Bank documents классифицированы | выполнено |
| SDD/ADR migration set определён | выполнено |
| MCP deletion set определён | выполнено |
| Shared infrastructure отделена | выполнено |
| Durable `unique-external` перенесены после value filtering | выполнено |
| Durable verification backlog сохранён | выполнено |
| ADR-0002 создан | выполнено |
| Internal references обновлены | выполнено |
| Пользователь подтвердил destructive phase | выполнено 2026-08-03 |

Все migration readiness gates выполнены. Удалены ровно 64 утверждённых tracked-файла; ignored/untracked файлов в deletion targets не было.
