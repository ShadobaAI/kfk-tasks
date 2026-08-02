# Настройка

## Memory Bank

`KAFKA_PROJECTS_ROOT` указывает на родительский каталог, содержащий `tasks`.
Канонические документы читаются из:

```text
<KAFKA_PROJECTS_ROOT>/tasks/memory-bank
```

Если переменная не задана, используется `memory-bank` рядом с editable/install
root пакета.

## HTTP server

| Environment variable | Default | Назначение |
|---|---:|---|
| `MEMORY_BANK_HOST` | `127.0.0.1` | bind address |
| `MEMORY_BANK_PORT` | `8767` | TCP port |
| `MEMORY_BANK_ENDPOINT` | `/mcp` | единый MCP endpoint |
| `MEMORY_BANK_ALLOWED_ORIGINS` | пусто | allowlist Origin через запятую или `;` |
| `MEMORY_BANK_REQUEST_TIMEOUT_SECONDS` | `30` | timeout HTTP request |
| `MEMORY_BANK_MAX_REQUEST_BYTES` | `1048576` | body limit |
| `MEMORY_BANK_MAX_CONCURRENT_REQUESTS` | `32` | HTTP concurrency и размер bounded tool pool |

`--host`, `--port`, `--endpoint` имеют приоритет над соответствующими
environment defaults. Остальные политики задаются environment variables.

Пример для локального browser client:

```powershell
$env:MEMORY_BANK_ALLOWED_ORIGINS = "http://127.0.0.1:3000,http://localhost:3000"
memory-bank-mcp
```

Allowlist включает проверку `Origin`, CORS preflight `OPTIONS` и CORS headers
в ответах. Не указывай wildcard: перечисляй точные browser origins.

Не используй `0.0.0.0` без TLS, authentication/authorization, firewall и
явного Origin allowlist.

## Карта репозиториев

[repositories.example.json](../config/repositories.example.json) задаёт
стабильные имена репозиториев и относительные пути. Локальные отличия храни в
исключённом из Git `config/local.json`.

## Кодировка и секреты

- Markdown хранится в UTF-8 с LF;
- paths в metadata используют `/`;
- секреты и broker credentials не размещаются в Memory Bank;
- application logs не содержат documents, полный query или authorization
  headers.
