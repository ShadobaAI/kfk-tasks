# Валидация и тесты

## Возможности валидатора

Валидатор проверяет и выводит:

- количество документов, общий размер, размер каждого документа и слишком
  большие файлы;
- отсутствующий или некорректный front matter и раздел `Summary`;
- отсутствие источников у проверенных документов;
- битые относительные ссылки и ссылки на заголовки;
- повторяющиеся заголовки, фрагменты и идентификаторы спецификаций или ADR;
- некорректные ссылки на источники и статусы;
- неполные метаданные спецификаций;
- документы без входящих ссылок и пропуски в корневой навигации;
- непереносимые ссылки и машинно-зависимые абсолютные пути.

## Запуск

```powershell
$env:PYTHONPATH = "src"
python -m memory_bank_mcp.cli validate
python -m memory_bank_mcp.cli validate --json
```

При наличии ошибок команда возвращает ненулевой exit code. Предупреждения
требуют проверки, но не приводят к автоматическому завершению с ошибкой.

## Автоматические тесты

```powershell
python -m unittest discover -s tests -v
```

Тесты покрывают tokenizer/normalizer, BM25 field boosts, regression-метрики,
lifecycle индекса, ограниченное чтение, optimistic concurrency и file lock
между экземплярами store, traversal, drive/UNC paths, атомарную запись, health
endpoints, CORS/Origin/body/timeout/concurrency policies, структурированные
логи и graceful shutdown. Интеграционный тест запускает настоящий TCP server,
выполняет MCP initialization и tool call официальным Streamable HTTP client
SDK.

Synthetic regression-набор хранится в `tests/search_regression.json` и содержит
21 запрос. `tests/search_regression_real.json` содержит 20 запросов к реальному
Memory Bank и сравнивает новое ранжирование с прежним линейным `count`.
Benchmark на 100 документах запускается отдельно:

```powershell
$env:PYTHONPATH = "src"
python benchmarks/search_benchmark.py
```

## Зафиксированные результаты

Локальный запуск 2026-07-30, Windows, Python 3.14.4:

| Метрика | Результат |
|---|---:|
| Regression queries | 21 |
| Hit@1 / Hit@3 / MRR | `1.0 / 1.0 / 1.0` |
| Real corpus queries | 20 |
| New search Hit@1 / Hit@3 / MRR | `1.0 / 1.0 / 1.0` |
| Legacy search Hit@1 / Hit@3 / MRR | `0.4 / 0.65 / 0.576` |
| Legacy search p50 / p95 | `16.024 / 21.493 ms` |
| Index build, 100 документов | `476.640 ms` |
| Indexed search p50 / p95 | `28.288 / 32.727 ms` |
| Update одного документа + refresh | `33.365 ms` |
| `tracemalloc` peak | `1,525,181 bytes` |
| Оценка payload индекса | `200,831 bytes` |

Это smoke benchmark, а не CI SLA. На коротком synthetic corpus сложное
ранжирование и обязательный stat-scan дают latency немного выше прежнего
линейного `count`; выигрыш реализации — качество, диагностируемость и отсутствие
повторного чтения нескольких мегабайт текста. Hardware-dependent thresholds не
используются, кроме мягких 10 секунд на build и 1 секунды на p95.

## Markdownlint

`.markdownlint.json` отключает ограничение длины строки для технического текста
и разрешает одинаковые заголовки только под разными родительскими разделами.
Такая конфигурация не мешает поддерживать URL, таблицы, блоки кода и технические
идентификаторы.
