# Ограничения и риски

- Поиск лексический: он не понимает семантические синонимы без `aliases` или
  `keywords` и не использует embeddings.
- Индекс существует только в памяти процесса. Первый поиск строит его заново;
  disk index отсутствует.
- Перед поиском проверяются path, `mtime_ns` и size всех Markdown-файлов. Для
  целевых 100 документов это приемлемо, но на коротком synthetic corpus warm
  latency сопоставима с прежним линейным поиском.
- Optimistic concurrency и advisory file lock предотвращают silent lost update
  между экземплярами этого MCP. Прямой editor или другой процесс, не
  использующий lock-файл, не участвует в протоколе; повторная проверка revision
  только сокращает окно гонки с таким процессом.
- HTTP timeout возвращает клиенту `504` и освобождает event loop, но уже
  выполняющийся синхронный Python-код принудительно не прерывается. Его slot
  остаётся занятым до фактического завершения; graceful shutdown также ждёт
  такие операции.
- Symlink/junction escape проверяется через resolved paths. В Windows-тесте
  создание symlink может быть пропущено из-за прав среды.
- Stateless mode не предоставляет durable sessions, resumability,
  subscriptions или server-initiated notifications.
- `GET /mcp` в stateless mode может вернуть `405`; обычные calls используют
  JSON response на `POST /mcp`.
- Реализация проверена с MCP Python SDK 1.27.2 и protocol `2025-11-25`.
  Поддержка release candidate `2026-07-28` не заявляется.
- Localhost bind не защищает от других процессов того же пользователя. Remote
  deployment без TLS и authentication запрещён security model проекта.
- Валидатор приближённо воспроизводит GitHub-style anchors; необычная
  пунктуация заголовков может потребовать явных anchors.
- Kafka runtime и совместимость с Конвертацией данных требуют отдельных
  интеграционных сред.
