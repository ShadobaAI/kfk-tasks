# Установка и запуск

## Требования

- Windows, Linux или macOS с Python 3.10+.
- PyYAML 6+.
- Рабочая область с каталогом `tasks` и подключёнными репозиториями проекта.

## Установка в режиме разработки

Выполни из каталога `tasks`:

```powershell
$env:KAFKA_PROJECTS_ROOT = Split-Path -Parent $PWD
python -m pip install -e .
memory-bank validate
memory-bank-mcp
```

Последняя команда запускает MCP-сервер через `stdio` и ожидает сообщения
JSON-RPC. Сетевой порт не открывается.

## Запуск без установки

```powershell
$env:KAFKA_PROJECTS_ROOT = Split-Path -Parent $PWD
$env:PYTHONPATH = "src"
python -m memory_bank_mcp.cli validate
python -m memory_bank_mcp.server
```

## Настройка Codex

Адаптируй [переносимый пример](../config/codex-mcp.example.toml) под локальный
механизм настройки MCP. Если используемая среда не подставляет переменные в
значения TOML, укажи вычисленное значение `KAFKA_PROJECTS_ROOT`.

## Проверка

```powershell
python -m unittest discover -s tests -v
memory-bank validate --json
```

Markdown-документы остаются полностью доступными, даже если Python или
MCP-сервер временно недоступны.
