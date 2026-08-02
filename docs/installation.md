# Установка и запуск

## Требования

- Windows, Linux или macOS с Python 3.10+;
- официальный Python MCP SDK `>=1.27.2,<2`;
- рабочая область с каталогом `tasks`.

Проверенная при реализации версия SDK — 1.27.2.

## Установка

Из каталога `tasks`:

```powershell
$env:KAFKA_PROJECTS_ROOT = Split-Path -Parent $PWD
python -m pip install -e .
memory-bank validate
memory-bank-mcp
```

Последняя команда запускает отдельный Streamable HTTP server на
`http://127.0.0.1:8767/mcp`. Процесс должен работать независимо от MCP-клиента.

Эквивалентный запуск:

```powershell
$env:PYTHONPATH = "src"
python -m memory_bank_mcp.server --host 127.0.0.1 --port 8767 --endpoint /mcp
```

CLI-форма:

```powershell
memory-bank serve --host 127.0.0.1 --port 8767 --endpoint /mcp
```

## Подключение Codex

Формат проверен по установленному `codex mcp add --help`:

```powershell
codex mcp add memory-bank --url http://127.0.0.1:8767/mcp
```

Или добавь [пример TOML](../config/codex-mcp.example.toml) в Codex config:

```toml
[mcp_servers.memory-bank]
url = "http://127.0.0.1:8767/mcp"
```

## Проверка

```powershell
Invoke-RestMethod http://127.0.0.1:8767/health/ready
python -m unittest discover -s tests -v
memory-bank validate --json
```

Для проверки performance:

```powershell
$env:PYTHONPATH = "src"
python benchmarks/search_benchmark.py
```

Markdown остаётся доступным напрямую, если MCP server остановлен.
