# Memory Bank MCP

## Транспорт и процесс

Сервер использует штатный Streamable HTTP transport из официального Python MCP
SDK `mcp>=1.27.2,<2`. Реализация проверена с SDK 1.27.2 и MCP protocol
`2025-11-25`; release candidate протокола `2026-07-28` не заявлен как
поддерживаемый этой версией SDK.

Конфигурация по умолчанию:

```text
transport: streamable-http
mode: stateless
URL: http://127.0.0.1:8767/mcp
JSON response: enabled
```

`POST /mcp` обслуживает MCP-вызовы. `GET /mcp` передаётся штатному transport и
в stateless-конфигурации может вернуть `405`, если отдельный SSE stream не
нужен. Legacy HTTP+SSE endpoints отсутствуют.

Health endpoints отделены от MCP:

```text
GET /health/live
GET /health/ready
```

Ответы health содержат только статус и не раскрывают документы.
`ready` становится успешным только после чтения и построения поискового индекса.
Оба health endpoint не занимают semaphore MCP-запросов и остаются доступными
при исчерпании concurrency limit или долгом tool-вызове.

## Поисковый индекс

Markdown остаётся единственным источником истины. При первом поиске строится
in-memory индекс. Перед каждым последующим поиском сервер сравнивает набор
файлов, `mtime_ns` и размер; изменённые документы перечитываются, добавленные
включаются, удалённые исключаются. Ручная переиндексация не нужна.

Ранжирование использует BM25-подобные вклады полей:

| Поле | Вес |
|---|---:|
| точное совпадение `id` | 100 |
| `title` | 12 |
| `aliases`, `keywords` | 10 |
| `component`, `repository` и их множественные варианты | 8 |
| Markdown headings | 6 |
| `summary` | 4 |
| основной текст | 1 |

Дополнительно применяются бонусы точной фразы, наличия всех термов и близкого
расположения термов. Нормализатор использует `casefold`, сводит `ё` к `е`,
разбирает CamelCase и поддерживает варианты с `-`, `_`, `/`, не применяя
агрессивный stemming к identifiers.

Результат сохраняет прежние обязательные поля и добавляет:

- `matched_fields`;
- детерминированный `score_details`;
- лучший по покрытию термов фрагмент тела документа.

Необязательные metadata:

```yaml
aliases:
  - альтернативное название
keywords:
  - технический термин
```

Документы без этих полей индексируются как раньше.

## Инструменты

Публичные имена tools сохранены. Группы:

- чтение: `list_documents`, `get_tree`, `get_metadata`, `get_summary`,
  `read_document`, `read_section`, `read_lines`;
- поиск: `search_text`, `find_exact`, `filter_documents`, `list_related`;
- SDD/ADR: `list_adrs`, `get_adr`, `list_specifications`,
  `get_specification`, `get_task_context`;
- запись: `create_document`, `update_document`, `update_section`, `create_adr`,
  `create_specification`, `update_specification_status`,
  `update_implementation_result`, `update_deviations`;
- проверка: `validate_memory_bank`.

## Конкурентная запись

`get_metadata`, `get_summary` и карточки `list_documents` возвращают
`revision` — SHA-256 текущего нормализованного UTF-8 содержимого.

Все update-tools требуют `expected_revision`. Записи всех экземпляров MCP,
работающих с одним Memory Bank, сериализуются advisory file lock. Сервер
повторно вычисляет revision непосредственно перед атомарной заменой.
Несовпадение возвращается как явный `Revision conflict`; устаревший клиент не
перезаписывает чужое изменение.

Create-tools не требуют revision и по-прежнему не перезаписывают существующий
файл: публикация выполняется атомарно без окна `exists`/overwrite. Разрешены
только нормализованные относительные `.md` paths внутри Memory Bank. Absolute,
drive, UNC, traversal и выход через существующий symlink/junction отклоняются.

## Ограничения ответа

Используй `limit`, `max_chars`, `section`, `start_line`, `end_line`, `scope`,
`repository`, `component`, `type` и `status`. Поиск ограничивает число
результатов до 100 и общий JSON payload через `max_chars`.

## Наблюдаемость

Приложение пишет JSON-события в `stderr`:

- `server_started`, `server_stopped`;
- `http_request` с request ID, MCP method/tool, duration и status;
- `tool_call` без содержимого и полного query;
- `search_index_updated` с количеством документов и длительностью.

Сообщения SDK и ASGI server также оборачиваются в JSON-событие
`dependency_log`; traceback в production log не печатается.
Authorization headers, secrets и содержимое документов не логируются.

## Security model

По умолчанию сервер слушает только `127.0.0.1`. MCP SDK проверяет `Host`,
`Content-Type` и `Origin`; Origin без явного allowlist отклоняется. Перед
transport применяются лимиты body, timeout и конкурентных запросов.
Разрешённые browser origins получают CORS preflight/response headers.
Синхронные операции выполняются в bounded thread pool, поэтому не блокируют
event loop; завершившийся timeout не освобождает execution slot до фактического
завершения операции.

Localhost не является authentication boundary против других процессов того же
пользователя. Для bind не на loopback production deployment обязан добавить
TLS, полноценную authentication/authorization, явный Origin allowlist и
сетевые ограничения. Встроенной фиктивной authentication нет.

## Проверка клиента

После запуска:

```powershell
codex mcp add memory-bank --url http://127.0.0.1:8767/mcp
codex mcp get memory-bank
```

Интеграционный тест использует официальный `streamable_http_client`,
`ClientSession.initialize()` и `ClientSession.call_tool()`.

См. [конфигурацию](configuration.md).

## Проверенные источники

- [MCP Streamable HTTP specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
- [Official Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Python MCP SDK 1.27.2 release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v1.27.2)
