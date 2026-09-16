---
title: Docker Compose для OpenViking и Ollama
type: specification-addendum
parent: SPEC-0012
status: in-progress
created: 2026-09-16
affected_repositories:
  - kafka-tools
  - kfk-tasks
---

# Дополнение к SPEC-0012: OpenViking и Ollama в Docker

## Проблема и цель

Windows bootstrap столкнулся с потерей кавычек Python-команд, непереносимыми
venv launchers и предупреждением зависимости о Python 3.14. Перевести сервер
OpenViking и локальные модели Ollama в Linux containers под Docker Desktop.
Сохранить существующие Git-backed sources, read-only MCP и readiness gates.

Дополнение утверждено пользователем 2026-09-16. Реализация начата.

## Границы и решения

- `kafka-tools`: Compose, installer, runtime metadata, HTTP client authentication,
  doctor/probe, проверки и документация в `tools/ai`.
- `kfk-tasks`: это дополнение, результаты приёмки и ADR при реализации.
- OpenViking и Ollama — отдельные сервисы одного Compose project. OpenViking
  обращается к Ollama по имени сервиса `ollama`, а не через `localhost`.
  Уточнение по текущей сессии: для Hyper-V ВМ поддержан внешний Ollama endpoint
  на GPU физического хоста. В этом режиме Compose содержит только OpenViking;
  управление внешним сервером и скачивание его моделей не выполняются из installer.
- API OpenViking публикуется только на `127.0.0.1:1933`; Ollama доступна внутри
  Compose network. Репозитории и Docker socket в контейнеры не монтируются.
- Git sync, hooks и Node MCP остаются на Windows. Передача committed документов
  должна работать через HTTP; Windows filesystem paths не передаются как пути
  контейнера. Сохраняются exclusions, revision checks и пять read-only MCP tools.
- Данные OpenViking и модели Ollama хранятся в отдельных persistent volumes.
  Конфигурация и API key находятся вне Git; ключ не выводится в логи.
  Внутренний абсолютный storage path должен соответствовать persistent mount.

## Installer и обновления

1. Docker становится единственным поддерживаемым runtime полного `install.cmd`.
   Windows venv bootstrap удаляется из toolkit; fallback и параллельный native mode
   не предусмотрены. Проверяются Linux
   Engine и Compose; ошибки содержат конкретную команду диагностики.
2. Сохраняется принятая политика OpenViking latest-stable. Installer разрешает
   официальный образ соответствующего стабильного release, фиксирует фактический
   digest и проверяет package version внутри контейнера. Отсутствие подходящего
   образа — явная ошибка, без молчаливого перехода на main/prerelease.
3. Для Ollama используется официальный образ, фиксируется разрешённый digest.
   Идентификаторы выбранных моделей и доступные digests записываются в local state.
4. Настройка предлагает embedding и VLM с учётом доступной памяти Docker/WSL и GPU,
   показывает модели и объём загрузки перед подтверждением. CPU поддерживается;
   NVIDIA acceleration включается отдельной конфигурацией после проверки доступа.
   RAM хоста сама по себе не считается доказательством вместимости моделей.
5. `init` не запускает вложенную установку Ollama в контейнере OpenViking.
   Provider endpoints указывают на сервис Ollama; существующая конфигурация не
   перезаписывается без необходимости и секреты не читаются в ответ агента.
6. Runtime state описывает только Docker deployment. Clients, probe и doctor
   проверяют фактически установленную версию и передают API authentication.
   Старые Python/wheel/runtime-root параметры и проверки venv удаляются вместе
   с соответствующими тестами и документацией. Совместимость со старым runtime
   state и автоматическая конвертация его формата не реализуются: при обнаружении
   старого состояния требуется явная повторная инициализация Docker state.
7. Образы и модели загружаются с видимым прогрессом. Startup/provider checks имеют
   ограниченные ожидания. Успех объявляется после semantic readiness, Git sync и MCP.

## Миграция и сохранность

Существующие Windows venv и пользовательские настройки автоматически не удаляются,
но installer их не использует и не поддерживает. Настройки Docker создаются отдельно;
импорт прежней provider configuration и миграция venv не входят в scope. Старое
производное содержимое Git namespace можно восстановить из committed HEAD;
произвольные пользовательские данные автоматически не удаляются и не мигрируют.
Конфликт порта диагностируется до запуска; посторонний процесс не останавливается.
Повторный запуск использует существующие volumes и модели. Installer не выполняет
`down -v`, prune или автоматическое удаление данных. Ошибка обновления не означает
безопасность downgrade данных: откат версии допускается только при совместимости.

## Приёмка

- `docker compose config` проходит без вывода секретов; PowerShell/Node syntax и
  актуализированные для Docker installer, manifest, doctor, sync/MCP и hook tests
  проходят. Native bootstrap, старые параметры и ветки venv отсутствуют.
- Focused проверки покрывают Docker metadata, auth, отсутствие Engine, конфликт
  порта, недоступную модель, несовпадение версии и повторную установку.
- Live: контейнеры запускаются; embedding и VLM дают успешный ответ; OpenViking
  проходит provider/vector DB/filesystem readiness; committed fixture загружается
  и находится через MCP. Проверяется загрузка содержимого через границу Windows/Linux.
- После рестарта контейнеров данные и модели сохраняются; повторный installer
  не скачивает неизменившиеся модели заново и не заявляет ready при partial sync.
- Конкретные модели и CPU/GPU режим фиксируются после проверки ресурсов перед
  live-загрузкой. Если ресурсов недостаточно, это отдельный блокер live-приёмки.

## Основания

- https://docs.openviking.ai/en/guides/03-deployment
- https://docs.ollama.com/docker
- https://docs.docker.com/compose/how-tos/gpu-support/

Проверено при подготовке: Docker Linux Engine 29.7.2, Compose 5.5.1 доступны.
Контейнеры и модели в рамках подготовки draft не запускались и не скачивались.

## Результаты реализации, 2026-09-16

- Удалён Windows bootstrap и Python/wheel/runtime-root параметры `install.cmd`.
  Новый Node bootstrap формирует Compose deployment только для Docker, проверяет
  Linux Engine, порт, официальный image digest и package version, запускает
  Ollama и проверяет embedding/VLM до OpenViking semantic readiness.
- Установщик использует отдельное состояние `openviking-docker`; старый формат
  отвергается. Clients, doctor и MCP используют локальный API key без вывода в логи.
- Compose хранит данные и модели в разных volumes, публикует только loopback:1933,
  связывает сервисы через `ollama:11434`, допускает отдельный NVIDIA GPU режим.
  Принят [ADR-0006](../adr/adr-0006-openviking-ollama-docker.md).
- Незавершённый или неудачный Docker setup оставляет pending marker. Проверка
  runtime и каждый авторизованный HTTP request блокируют context reads до
  успешного повторного setup; recovery проверен тестом.
- Прошли `test-installation.ps1`, `test-openviking-docker.mjs`, manifest, sync,
  MCP, doctor, hooks и two-checkout tests. Compose проверен настоящим
  `docker compose config --quiet`. Проверки Docker startup/recovery/idempotency,
  version mismatch и отсутствующей модели пока используют mock Docker/provider.
- Node syntax и focused diff checks прошли. Live-загрузка моделей, provider
  calls, ingestion/query и сохранность данных после рестарта пока не проверены.
  Запрошено подтверждение загрузки минимального набора моделей (~4 ГБ) и образов;
  до ответа загрузка и запуск не выполняются.
- Docker имеет около 7,8 ГиБ RAM, NVIDIA CLI отсутствует. Это не доказывает
  отсутствие GPU, но CPU выбран безопасным исходным режимом. SQL Server и v8std
  используют ту же память; live-приёмка может потребовать увеличения лимита RAM.

Статус остаётся in-progress до завершения live-приёмки или фиксации её блокера.

## Подключение GPU хоста, 2026-09-16

Пользователь развернул Ollama в Docker на физическом хосте с RTX 3060 и передал
успешный ответ `/api/tags` из ВМ. Добавлен `-OllamaUrl` / `KAFKA_OLLAMA_URL`;
внешний адрес сохраняется в runtime state. Локальная Ollama в этом режиме не
создаётся, не запускается и не скачивается. Endpoint проверяется из контейнера;
конфигурационный digest вызывает пересоздание OpenViking при изменении адреса.
Ранее созданные контейнеры/volumes автоматически не удаляются.

Настоящие сетевые проверки подтвердили наличие обеих моделей из Windows и
HTTP 200 от endpoint из одноразового Linux-контейнера без загрузки новых образов.
Прошли installer и Docker tests, включая отсутствие локальных Ollama operations,
проверку отсутствующей remote модели и сохранение endpoint при повторном запуске.
Полная OpenViking deployment/ingestion приёмка остаётся отдельной проверкой.
Прямые live-запросы из ВМ подтвердили embedding размерности 1024 и непустой ответ
VLM с `think=false`, context 16384 и ограничением 16 output tokens. Короткая
генерация заняла 5,23 секунды по метрике provider total_duration; это smoke-check,
а не репрезентативный benchmark индексации. Новые модели не скачивались.

## Registry recovery, 2026-09-16

Docker pull GHCR returned `denied`, включая временную пустую Docker auth config.
Прямой анонимный GHCR API при этом отдал release manifests. Точная причина
различия сетевых путей не установлена; credentials пользователя не изменялись.
Добавлен fallback через Docker Hub исключительно по platform digest официального
GHCR release index, с проверкой SHA-256 самого index. Docker проверяет содержимое
образа по тому же digest; произвольный mirror tag не используется.
Образ 0.4.20 реально скачан, package version внутри контейнера подтверждена.
Тесты проверяют matching digest, отказ при mismatch и связь runtime sourceImage
с фактическим mirror image. Deployment остаётся Docker-only и latest-stable.

Live bootstrap завершён успешно: контейнер OpenViking 0.4.20 запущен; embedding
и VLM проверены из его контейнера через внешний Ollama endpoint. `/ready` подтвердил
embedding, vectordb и AGFS filesystem. `/health` публикует версию `v0.4.20`, поэтому
сравнение нормализует только необязательный префикс `v`; dev/другая версия по-прежнему
отвергается. Этот случай проверен отдельной регрессией. Git ingestion и полная
остальная установка toolkit этим bootstrap запуском не выполнялись.

## Исправление авторизации Git ingestion, 2026-09-16

В установленном OpenViking 0.4.20 режим `api_key` запрещает ROOT-ключам
tenant-scoped data API. Bootstrap использовал ROOT-ключ для синхронизации,
что приводило к HTTP 403 на первом удалении namespace. Теперь bootstrap создаёт
account `kafka` с admin user `git-sync`, сохраняет выданный ключ отдельно в
`tenant-api-key` и проверяет доступ к resources до публикации готового runtime.
ROOT-ключ остаётся для административных запросов. Повторная установка сохраняет
ключи; существующий account без сохранённого tenant key останавливает настройку,
без автоматической ротации или удаления данных.

Синхронизация допускает отсутствие удаляемого ресурса только при HTTP 404 с кодом
`NOT_FOUND`; ошибки доступа и прочие ошибки не подавляются. Добавлен прогресс
по документам. Пройдены Docker/authentication, Git sync, read-only MCP и installer
tests. Live provisioning и повторная проверка tenant scope прошли успешно.
Полный live initial ingestion завершён: `status=ready`, `mode=rebuild`,
94 записи из 9 Git-репозиториев; подтверждены наличие всех файлов, завершение
семантической/векторной обработки и неизменность HEAD. Повторный live reconciliation
вернул `mode=incremental`, 0 writes, 0 deletes. Live вызов `find` через тот же
`callTool`, который использует MCP, вернул непустую выдачу из Git namespace.
Полный installer с остальными компонентами toolkit в этом проверочном запуске
не выполнялся; его focused tests прошли.
