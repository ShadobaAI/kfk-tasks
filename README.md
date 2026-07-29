# Kafka Adapter — задачи, Memory Bank и SDD

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MCP](https://img.shields.io/badge/MCP-stdio-blue)
![Хранилище](https://img.shields.io/badge/Хранилище-Markdown-green)
[![Issues](https://img.shields.io/github/issues/ShadobaAI/kfk-tasks)](https://github.com/ShadobaAI/kfk-tasks/issues)

Задачи, проектная база знаний, Specification-Driven Development и локальный
MCP-сервер для экосистемы
[1С: Адаптер Kafka](https://github.com/ShadobaAI/kafka-adapter).

## Назначение

Репозиторий содержит инструменты и документацию для сопровождения проекта:

- **GitHub Issues** — постановка, обсуждение и контроль проектных задач;
- **GitHub Projects** — визуальное представление текущего хода работ;
- **Memory Bank** — архитектура, карта репозиториев, компоненты, публичный API,
  потоки данных и правила разработки;
- **SDD и ADR** — спецификации изменений и архитектурные решения;
- **Memory Bank MCP** — ограниченное чтение, поиск, формирование контекста задачи
  и контролируемое изменение Markdown-документов;
- **валидатор** — проверка структуры, метаданных, ссылок, якорей и переносимости
  базы знаний.

Начальная точка навигации — [Memory Bank](memory-bank/README.md).

## Issues и управление работами

Задачи проекта создаются в
[GitHub Issues](https://github.com/ShadobaAI/kfk-tasks/issues), а их состояние
отслеживается на
[доске GitHub Projects](https://github.com/users/ShadobaAI/projects/3/views/1).

Перед созданием Issue проверь существующие задачи. В описании укажи:

- затронутые репозитории и компоненты;
- текущее и ожидаемое поведение;
- шаги воспроизведения для ошибки либо ожидаемый результат для изменения;
- ограничения совместимости и критерии приёмки;
- связанные спецификации, ADR, pull requests и commits при их наличии.

Issue используется для обсуждения и контроля работы. Устойчивые требования
значимого изменения фиксируются в SDD-спецификации, а архитектурные решения —
в ADR. Идентификаторы `SPEC-NNNN` и `ADR-NNNN` не зависят от номера Issue.

## Быстрый старт

Требуется Python 3.10 или новее.

```powershell
$env:KAFKA_PROJECTS_ROOT = Split-Path -Parent $PWD
python -m pip install -e .
memory-bank validate
memory-bank-mcp
```

MCP-сервер работает через `stdio`. База данных, облачные сервисы и обязательные
плагины редактора не требуются.

## Структура

| Каталог | Назначение |
|---|---|
| [`memory-bank/`](memory-bank/README.md) | Каноническая проектная база знаний |
| [`memory-bank/specifications/`](memory-bank/specifications/README.md) | SDD-спецификации и их жизненный цикл |
| [`memory-bank/decisions/`](memory-bank/decisions/README.md) | ADR и шаблон архитектурного решения |
| [`src/memory_bank_mcp/`](src/memory_bank_mcp/) | MCP-сервер, хранилище и валидатор |
| [`tests/`](tests/) | Автоматические тесты |
| [`config/`](config/) | Примеры переносимой конфигурации |
| [`docs/`](docs/) | Установка, настройка и эксплуатация |

## Документация

- [Установка и запуск](docs/installation.md) — требования, установка пакета,
  запуск MCP-сервера и проверка работоспособности.
- [Настройка](docs/configuration.md) — `KAFKA_PROJECTS_ROOT`, карта репозиториев,
  кодировка и правила хранения секретов.
- [MCP-инструменты и ресурсы](docs/mcp.md) — транспорт, операции чтения и записи,
  ограничения размера ответа и поддерживаемое подмножество протокола.
- [VS Code и Obsidian](docs/vscode-obsidian.md) — открытие Memory Bank,
  навигация по ссылкам и ручная проверка.
- [Валидация и тесты](docs/validation-and-tests.md) — состав проверок, команды
  запуска и покрытые сценарии.
- [Ограничения и риски](docs/limitations.md) — границы поиска, кеширования,
  конкурентной записи, файловой безопасности и интеграционной проверки.

Markdown-файлы в `memory-bank/` являются единственным источником проектного
контекста. Они читаются и редактируются без MCP-сервера.
