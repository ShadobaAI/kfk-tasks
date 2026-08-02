from __future__ import annotations

import json
import hashlib
import hmac
import logging
import os
import re
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml

from .search import SearchIndex

if os.name == "nt":
    import msvcrt
else:
    import fcntl


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
LOGGER = logging.getLogger("memory_bank_mcp")


class MemoryBankError(ValueError):
    """Expected client-facing error."""


@contextmanager
def exclusive_file_lock(path: Path, timeout_seconds: float = 30.0):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
        )
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "wb") as initializer:
            initializer.write(b"\0")
            initializer.flush()
            os.fsync(initializer.fileno())
    deadline = time.monotonic() + timeout_seconds
    while True:
        handle = path.open("r+b")
        if path.stat().st_size:
            break
        handle.close()
        if time.monotonic() >= deadline:
            raise MemoryBankError("Timed out initializing the write lock")
        time.sleep(0.01)
    try:
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as error:
                if time.monotonic() >= deadline:
                    raise MemoryBankError("Timed out waiting for the write lock") from error
                time.sleep(0.05)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def _json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


@dataclass(frozen=True)
class Document:
    path: str
    metadata: dict[str, Any]
    body: str
    text: str
    summary: str
    headings: tuple[str, ...]

    @property
    def title(self) -> str:
        return str(self.metadata.get("title") or Path(self.path).stem)

    @property
    def revision(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def parse_markdown(text: str, path: str = "") -> Document:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    metadata: dict[str, Any] = {}
    body = normalized
    if normalized.startswith("---\n"):
        marker = normalized.find("\n---\n", 4)
        if marker >= 0:
            raw = normalized[4:marker]
            loaded = yaml.safe_load(raw) or {}
            if not isinstance(loaded, dict):
                raise MemoryBankError(f"Front matter must be a mapping: {path}")
            metadata = _json_safe(loaded)
            body = normalized[marker + 5 :]
    summary = extract_section(body, "Summary") or ""
    headings = tuple(match.group(2).strip() for match in HEADING_RE.finditer(body))
    return Document(path, metadata, body, normalized, summary.strip(), headings)


def extract_section(text: str, section: str) -> str | None:
    matches = list(HEADING_RE.finditer(text))
    wanted = section.strip().lstrip("#").strip().casefold()
    for index, match in enumerate(matches):
        title = match.group(2).strip()
        title = re.sub(r"\s+\{#[^}]+\}\s*$", "", title)
        if title.casefold() != wanted:
            continue
        level = len(match.group(1))
        end = len(text)
        for following in matches[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        return text[match.end() : end].strip()
    return None


def replace_section(text: str, section: str, content: str, append: bool) -> str:
    matches = list(HEADING_RE.finditer(text))
    wanted = section.strip().lstrip("#").strip().casefold()
    for index, match in enumerate(matches):
        title = re.sub(r"\s+\{#[^}]+\}\s*$", "", match.group(2).strip())
        if title.casefold() != wanted:
            continue
        level = len(match.group(1))
        end = len(text)
        for following in matches[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        existing = text[match.end() : end].strip()
        replacement = existing + "\n\n" + content.strip() if append and existing else content.strip()
        suffix = text[end:].lstrip("\n")
        return text[: match.end()] + "\n\n" + replacement + "\n\n" + suffix
    heading = section.strip()
    if not heading.startswith("#"):
        heading = "## " + heading
    return text.rstrip() + "\n\n" + heading + "\n\n" + content.strip() + "\n"


def slugify_heading(value: str) -> str:
    value = re.sub(r"\s+\{#([^}]+)\}\s*$", r"\1", value.strip())
    value = value.casefold()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


class MemoryBankStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self._cache: dict[str, tuple[int, int, Document]] = {}
        self._search_index = SearchIndex()
        self._write_lock = threading.RLock()
        self._cache_lock = threading.RLock()
        self._index_lock = threading.RLock()
        self._cross_process_lock_path = self.root / ".memory-bank-write.lock"
        self._prepared = False

    @classmethod
    def from_environment(cls) -> "MemoryBankStore":
        package_root = Path(__file__).resolve().parents[2]
        workspace = os.environ.get("KAFKA_PROJECTS_ROOT")
        if workspace:
            root = Path(workspace) / "tasks" / "memory-bank"
        else:
            root = package_root / "memory-bank"
        return cls(root)

    def _relative(self, value: str) -> PurePosixPath:
        if not isinstance(value, str) or not value.strip():
            raise MemoryBankError("A non-empty relative path is required")
        raw = value.strip()
        if DRIVE_RE.match(raw) or raw.startswith(("\\\\", "//")):
            raise MemoryBankError("Absolute, drive, and UNC paths are rejected")
        normalized = raw.replace("\\", "/")
        path = PurePosixPath(normalized)
        if path.is_absolute() or ".." in path.parts:
            raise MemoryBankError("Path traversal is rejected")
        if any(part in ("", ".") for part in path.parts):
            raise MemoryBankError("Path must be normalized")
        if path.suffix.casefold() != ".md":
            raise MemoryBankError("Only Markdown documents are allowed")
        return path

    def resolve(self, value: str, *, for_write: bool = False) -> Path:
        relative = self._relative(value)
        candidate = self.root.joinpath(*relative.parts)
        parent = candidate.parent.resolve(strict=False)
        try:
            common = os.path.commonpath((str(self.root), str(parent)))
        except ValueError as error:
            raise MemoryBankError("Path is outside the Memory Bank") from error
        if Path(common) != self.root:
            raise MemoryBankError("Path is outside the Memory Bank")
        if candidate.exists() or not for_write:
            resolved = candidate.resolve(strict=False)
            if os.path.commonpath((str(self.root), str(resolved))) != str(self.root):
                raise MemoryBankError("Resolved path escapes the Memory Bank")
        return candidate

    def _relative_name(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def paths(self) -> list[Path]:
        if not self.root.exists():
            return []
        return sorted(
            (
                path
                for path in self.root.rglob("*.md")
                if ".obsidian" not in path.parts and path.is_file()
            ),
            key=lambda path: path.as_posix().casefold(),
        )

    def get(self, value: str) -> Document:
        with self._cache_lock:
            path = self.resolve(value)
            if not path.is_file():
                raise MemoryBankError(f"Document not found: {value}")
            stat = path.stat()
            key = self._relative_name(path)
            cached = self._cache.get(key)
            if cached and cached[0] == stat.st_mtime_ns and cached[1] == stat.st_size:
                return cached[2]
            text = path.read_text(encoding="utf-8")
            document = parse_markdown(text, key)
            self._cache[key] = (stat.st_mtime_ns, stat.st_size, document)
            return document

    def documents(self) -> list[Document]:
        return [self.get(self._relative_name(path)) for path in self.paths()]

    def _refresh_search_index(self) -> None:
        with self._index_lock:
            started = time.perf_counter()
            paths = self.paths()
            signatures: dict[str, tuple[int, int]] = {}
            changed: dict[str, Document] = {}
            for path in paths:
                name = self._relative_name(path)
                stat = path.stat()
                signature = (stat.st_mtime_ns, stat.st_size)
                signatures[name] = signature
                if self._search_index.signatures.get(name) != signature:
                    changed[name] = self.get(name)
            removed_count = len(set(self._search_index.documents) - set(signatures))
            with self._cache_lock:
                for removed in set(self._cache) - set(signatures):
                    self._cache.pop(removed, None)
            if self._search_index.refresh(signatures, changed):
                LOGGER.info(
                    json.dumps(
                        {
                            "event": "search_index_updated",
                            "documents": len(signatures),
                            "changed": len(changed),
                            "removed": removed_count,
                            "duration_ms": round(
                                (time.perf_counter() - started) * 1000, 3
                            ),
                        },
                        separators=(",", ":"),
                    )
                )
            self._prepared = True

    def prepare(self) -> None:
        if not self.root.is_dir():
            raise MemoryBankError(f"Memory Bank root not found: {self.root}")
        self._refresh_search_index()

    def is_ready(self) -> bool:
        return self._prepared and self.root.is_dir()

    @staticmethod
    def _matches(document: Document, filters: dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if expected in (None, "", []):
                continue
            fields = {
                "repository": ("repository", "affected_repositories", "scope"),
                "component": ("component", "components", "affected_components"),
            }.get(key, (key,))
            values = {
                str(item).casefold()
                for field in fields
                for item in _as_list(document.metadata.get(field))
            }
            expected_values = expected if isinstance(expected, list) else [expected]
            if not any(str(item).casefold() in values for item in expected_values):
                return False
        return True

    def list_documents(self, limit: int = 100, **filters: Any) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 1000))
        output = []
        for document in self.documents():
            if not self._matches(document, filters):
                continue
            output.append(
                {
                    "path": document.path,
                    "title": document.title,
                    "metadata": document.metadata,
                    "summary": document.summary[:800],
                    "revision": document.revision,
                }
            )
            if len(output) >= limit:
                break
        return output

    def tree(self, max_chars: int = 20_000) -> str:
        lines: list[str] = []
        for path in self.paths():
            relative = path.relative_to(self.root)
            lines.append("  " * (len(relative.parts) - 1) + relative.name)
        return bounded("\n".join(lines), max_chars)

    def read_document(self, path: str, max_chars: int = 20_000) -> str:
        return bounded(self.get(path).text, max_chars)

    def read_summary(self, path: str, max_chars: int = 4_000) -> dict[str, Any]:
        document = self.get(path)
        return {
            "path": document.path,
            "metadata": document.metadata,
            "summary": bounded(document.summary, max_chars),
            "revision": document.revision,
        }

    def read_section(self, path: str, section: str, max_chars: int = 10_000) -> str:
        content = extract_section(self.get(path).body, section)
        if content is None:
            raise MemoryBankError(f"Section not found: {section}")
        return bounded(content, max_chars)

    def read_lines(
        self, path: str, start_line: int, end_line: int, max_chars: int = 10_000
    ) -> dict[str, Any]:
        lines = self.get(path).text.splitlines()
        start = max(1, int(start_line))
        end = min(len(lines), int(end_line))
        if end < start:
            raise MemoryBankError("end_line must be greater than or equal to start_line")
        return {
            "path": path,
            "start_line": start,
            "end_line": end,
            "total_lines": len(lines),
            "content": bounded("\n".join(lines[start - 1 : end]), max_chars),
        }

    def search(
        self,
        query: str,
        *,
        exact: bool = False,
        limit: int = 20,
        max_chars: int = 12_000,
        **filters: Any,
    ) -> dict[str, Any]:
        if not query:
            raise MemoryBankError("query is required")
        with self._index_lock:
            self._refresh_search_index()
            results = self._search_index.search(
                query,
                exact=exact,
                predicate=lambda document: self._matches(document, filters),
            )
        selected = results[: max(1, min(int(limit), 100))]
        maximum = max(256, min(int(max_chars), 1_000_000))
        payload = {
            "query": bounded(query, min(1000, max(64, maximum // 4))),
            "exact": exact,
            "count": len(selected),
            "results": selected,
        }
        if len(json.dumps(payload, ensure_ascii=False)) > maximum:
            while selected and len(json.dumps(payload, ensure_ascii=False)) > maximum:
                selected.pop()
            payload["omitted"] = len(results) - len(selected)
            payload["count"] = len(selected)
        if len(json.dumps(payload, ensure_ascii=False)) > maximum:
            payload["query"] = bounded(query, 64)
        return payload

    def related(self, path: str, limit: int = 50) -> list[dict[str, str]]:
        document = self.get(path)
        related = document.metadata.get("related") or []
        if isinstance(related, str):
            related = [related]
        output: list[dict[str, str]] = []
        for target in related[: max(1, min(int(limit), 100))]:
            target_text = str(target).partition("#")[0]
            try:
                normalized = normalize_relative_document_path(document.path, target_text)
                resolved = self.get(normalized)
                output.append({"path": resolved.path, "title": resolved.title})
            except MemoryBankError:
                output.append({"path": target_text, "title": "Missing"})
        return output

    def get_by_id(self, identifier: str, doc_type: str) -> Document:
        wanted = identifier.casefold()
        for document in self.documents():
            if str(document.metadata.get("type", "")).casefold() != doc_type.casefold():
                continue
            if str(document.metadata.get("id", "")).casefold() == wanted:
                return document
        raise MemoryBankError(f"{doc_type} not found: {identifier}")

    def task_context(
        self,
        *,
        issue_id: str | None = None,
        specification_id: str | None = None,
        repositories: list[str] | None = None,
        components: list[str] | None = None,
        max_chars: int = 16_000,
    ) -> dict[str, Any]:
        selected: list[dict[str, Any]] = []
        seen: set[str] = set()
        candidates: list[Document] = []
        for fixed in ("project-overview.md", "repositories.md"):
            try:
                candidates.append(self.get(fixed))
            except MemoryBankError:
                pass
        for repository in repositories or []:
            candidates.extend(
                document
                for document in self.documents()
                if self._matches(document, {"repository": repository})
                or str(document.metadata.get("scope", "")).casefold()
                == repository.casefold()
            )
        for component in components or []:
            candidates.extend(
                document
                for document in self.documents()
                if self._matches(document, {"component": component})
            )
        if specification_id:
            candidates.append(self.get_by_id(specification_id, "specification"))
        elif issue_id:
            candidates.extend(
                document
                for document in self.documents()
                if str(document.metadata.get("github_issue", "")).casefold()
                == str(issue_id).casefold()
            )
        affected_ids = {
            str(value).casefold()
            for document in candidates
            for value in _as_list(document.metadata.get("related_adrs"))
        }
        candidates.extend(
            document
            for document in self.documents()
            if str(document.metadata.get("id", "")).casefold() in affected_ids
        )
        omitted: list[str] = []
        used = 0
        for document in candidates:
            if document.path in seen:
                continue
            seen.add(document.path)
            entry = {
                "path": document.path,
                "title": document.title,
                "metadata": document.metadata,
                "summary": document.summary,
            }
            size = len(json.dumps(entry, ensure_ascii=False))
            if used + size > max_chars:
                omitted.append(document.path)
                continue
            selected.append(entry)
            used += size
        return {
            "issue_id": issue_id,
            "specification_id": specification_id,
            "documents": selected,
            "omitted": omitted,
            "max_chars": max_chars,
        }

    def _validate_write(self, text: str, path: str) -> None:
        document = parse_markdown(text, path)
        if not document.metadata:
            raise MemoryBankError("Front matter is required")
        for required in ("title", "type", "status", "updated"):
            if not document.metadata.get(required):
                raise MemoryBankError(f"Missing required front matter field: {required}")
        if not document.summary:
            raise MemoryBankError("A non-empty '## Summary' section is required")

    def create(self, path: str, content: str) -> dict[str, Any]:
        with self._write_lock:
            with exclusive_file_lock(self._cross_process_lock_path):
                target = self.resolve(path, for_write=True)
                if target.exists():
                    raise MemoryBankError(f"Create will not overwrite: {path}")
                self._validate_write(content, path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target = self.resolve(path, for_write=True)
                revision = self._write_atomic(target, content, create=True)
                return {"created": path, "revision": revision}

    def update(
        self, path: str, content: str, *, expected_revision: str
    ) -> dict[str, Any]:
        with self._write_lock:
            with exclusive_file_lock(self._cross_process_lock_path):
                target = self.resolve(path, for_write=True)
                if not target.is_file():
                    raise MemoryBankError(
                        f"Update requires an existing document: {path}"
                    )
                self._assert_revision(path, expected_revision)
                self._validate_write(content, path)
                revision = self._write_atomic(
                    target,
                    content,
                    expected_revision=expected_revision,
                )
                return {"updated": path, "revision": revision}

    def update_section(
        self,
        path: str,
        section: str,
        content: str,
        *,
        expected_revision: str,
        append: bool = False,
    ) -> dict[str, Any]:
        with self._write_lock:
            document = self.get(path)
            self._assert_revision(path, expected_revision)
            updated = replace_section(document.text, section, content, append)
            return self.update(path, updated, expected_revision=expected_revision)

    def create_from_template(
        self,
        *,
        template_path: str,
        path: str,
        replacements: dict[str, str],
    ) -> dict[str, Any]:
        text = self.get(template_path).text
        for source, target in replacements.items():
            text = text.replace(source, target)
        return self.create(path, text)

    def update_front_matter(
        self, path: str, updates: dict[str, Any], *, expected_revision: str
    ) -> dict[str, Any]:
        with self._write_lock:
            document = self.get(path)
            self._assert_revision(path, expected_revision)
            metadata = dict(document.metadata)
            metadata.update(updates)
            front = yaml.safe_dump(
                metadata, allow_unicode=True, sort_keys=False, default_flow_style=False
            ).strip()
            content = f"---\n{front}\n---\n{document.body.lstrip()}"
            return self.update(path, content, expected_revision=expected_revision)

    def _assert_revision(self, path: str, expected_revision: str) -> None:
        if not expected_revision:
            raise MemoryBankError("expected_revision is required for updates")
        actual = self._file_revision(self.resolve(path))
        if not secrets_compare(actual, expected_revision):
            raise MemoryBankError(
                f"Revision conflict for {path}: document changed since it was read"
            )

    @staticmethod
    def _file_revision(path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _write_atomic(
        self,
        target: Path,
        content: str,
        *,
        create: bool = False,
        expected_revision: str | None = None,
    ) -> str:
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        if not normalized.endswith("\n"):
            normalized += "\n"
        fd, temporary = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(normalized)
                handle.flush()
                os.fsync(handle.fileno())
            key = self._relative_name(target)
            target = self.resolve(key, for_write=True)
            if create:
                try:
                    os.link(temporary, target)
                except FileExistsError as error:
                    raise MemoryBankError(f"Create will not overwrite: {key}") from error
            else:
                if expected_revision is None:
                    raise MemoryBankError("expected_revision is required for updates")
                if not target.is_file():
                    raise MemoryBankError(
                        f"Update requires an existing document: {key}"
                    )
                actual = self._file_revision(target)
                if not secrets_compare(actual, expected_revision):
                    raise MemoryBankError(
                        f"Revision conflict for {key}: document changed during update"
                    )
                os.replace(temporary, target)
                temporary = ""
            with self._cache_lock:
                self._cache.pop(key, None)
            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        finally:
            try:
                if temporary:
                    os.unlink(temporary)
            except OSError:
                pass


def secrets_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def normalize_relative_document_path(source: str, target: str) -> str:
    combined = PurePosixPath(source).parent / target.replace("\\", "/")
    parts: list[str] = []
    for part in combined.parts:
        if part == "..":
            if not parts:
                raise MemoryBankError("Related path escapes the Memory Bank")
            parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    normalized = PurePosixPath(*parts)
    if normalized.suffix.casefold() != ".md":
        raise MemoryBankError("Related path must reference Markdown")
    return normalized.as_posix()


def bounded(value: str, max_chars: int) -> str:
    maximum = max(1, min(int(max_chars), 1_000_000))
    if len(value) <= maximum:
        return value
    marker = "\n\n[truncated]"
    return value[: max(0, maximum - len(marker))] + marker


def repository_names(config_path: Path | None = None) -> set[str]:
    if config_path is None:
        config_directory = Path(__file__).resolve().parents[2] / "config"
        local = config_directory / "local.json"
        config_path = local if local.is_file() else config_directory / "repositories.example.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return set(data.get("repositories", {}))
    except (OSError, ValueError):
        return set()
