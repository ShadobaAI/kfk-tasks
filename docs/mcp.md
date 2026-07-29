# Memory Bank MCP

## Транспорт и хранение

Сервер использует MCP поверх JSON-RPC через `stdio`. Markdown-файлы читаются
напрямую. Внутрипроцессный кеш сбрасывается при изменении времени модификации
или размера файла. База данных, сетевой listener и облачные зависимости
отсутствуют.

## Инструменты чтения

| Инструмент | Назначение |
|---|---|
| `list_documents` | Ограниченный список документов с метаданными и краткими описаниями |
| `get_tree` | Компактное дерево документов |
| `get_metadata` | Только YAML front matter |
| `get_summary` | Front matter и раздел `Summary` |
| `read_document` | Полный документ с ограничением размера |
| `read_section` | Один раздел по имени заголовка |
| `read_lines` | Включительный диапазон строк с нумерацией от 1 |
| `search_text` | Ранжированный лексический поиск |
| `find_exact` | Поиск точного текста |
| `filter_documents` | Фильтры по scope, репозиторию, компоненту, типу и статусу |
| `list_related` | Связи из front matter |
| `list_adrs`, `get_adr` | Поиск и чтение ADR |
| `list_specifications`, `get_specification` | Поиск и чтение спецификаций |
| `get_task_context` | Компактный контекст задачи без дублирования |
| `validate_memory_bank` | Машиночитаемый результат валидации |

## Инструменты записи

| Инструмент | Безопасность операции |
|---|---|
| `create_document` | Не перезаписывает существующий файл |
| `update_document` | Требует существующий файл |
| `update_section` | Добавляет или заменяет один раздел |
| `create_adr` | Создаёт ADR по каноническому шаблону |
| `create_specification` | Создаёт SDD-спецификацию по каноническому шаблону |
| `update_specification_status` | Обновляет статус и дату |
| `update_implementation_result` | Заменяет результат реализации |
| `update_deviations` | Заменяет описание отклонений |

Для записи требуются корректный front matter и непустой раздел `Summary`. Пути
задаются относительно `memory-bank/`. Абсолютные пути, Windows drive paths,
UNC, path traversal и файлы не в формате Markdown отклоняются. Перед атомарной
заменой соседнего файла новое содержимое проходит валидацию.

## Ресурсы

`resources/list` возвращает все Markdown-документы и ресурс
`memory-bank:///tree`. Документ можно прочитать по URI:

```text
memory-bank:///architecture/overview.md
```

## Ограничение размера ответа

Используй параметры `limit`, `max_chars`, `section`, `start_line`, `end_line`,
`scope`, `repository`, `component`, `type` и `status`. Если контекст задачи не
помещается в `max_chars`, ответ содержит список исключённых документов.

## Ограничения протокола

Необходимое подмножество MCP реализовано напрямую, без зависимости от MCP SDK.
HTTP/SSE transport, subscriptions, prompts, sampling и roots negotiation
намеренно не поддерживаются.
