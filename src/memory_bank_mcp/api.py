from __future__ import annotations

from datetime import date
from pathlib import PurePosixPath
from typing import Any, Callable

from .store import MemoryBankError, MemoryBankStore
from .validator import MemoryBankValidator


def tool_definitions() -> list[dict[str, Any]]:
    def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
        value: dict[str, Any] = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }
        if required:
            value["required"] = required
        return value

    string = {"type": "string"}
    integer = {"type": "integer"}
    strings = {"type": "array", "items": string}
    filters = {
        "scope": string,
        "repository": string,
        "component": string,
        "type": string,
        "status": string,
    }
    return [
        {"name": "list_documents", "description": "List bounded document cards with metadata and summaries.", "inputSchema": schema({"limit": integer, **filters})},
        {"name": "get_tree", "description": "Return the Memory Bank Markdown tree.", "inputSchema": schema({"max_chars": integer})},
        {"name": "get_metadata", "description": "Get front matter for one document.", "inputSchema": schema({"path": string}, ["path"])},
        {"name": "get_summary", "description": "Get metadata and Summary only.", "inputSchema": schema({"path": string, "max_chars": integer}, ["path"])},
        {"name": "read_document", "description": "Read a complete bounded document.", "inputSchema": schema({"path": string, "max_chars": integer}, ["path"])},
        {"name": "read_section", "description": "Read one named Markdown section.", "inputSchema": schema({"path": string, "section": string, "max_chars": integer}, ["path", "section"])},
        {"name": "read_lines", "description": "Read an inclusive 1-based line range.", "inputSchema": schema({"path": string, "start_line": integer, "end_line": integer, "max_chars": integer}, ["path", "start_line", "end_line"])},
        {"name": "search_text", "description": "Ranked bounded text search.", "inputSchema": schema({"query": string, "limit": integer, "max_chars": integer, **filters}, ["query"])},
        {"name": "find_exact", "description": "Bounded exact-text search.", "inputSchema": schema({"query": string, "limit": integer, "max_chars": integer, **filters}, ["query"])},
        {"name": "filter_documents", "description": "Filter documents by metadata.", "inputSchema": schema({"limit": integer, **filters})},
        {"name": "list_related", "description": "List documents from front-matter related links.", "inputSchema": schema({"path": string, "limit": integer}, ["path"])},
        {"name": "list_adrs", "description": "List architecture decisions.", "inputSchema": schema({"status": string, "limit": integer})},
        {"name": "get_adr", "description": "Retrieve an ADR by stable id.", "inputSchema": schema({"id": string, "max_chars": integer}, ["id"])},
        {"name": "list_specifications", "description": "List SDD specifications.", "inputSchema": schema({"status": string, "repository": string, "component": string, "limit": integer})},
        {"name": "get_specification", "description": "Retrieve a specification by stable id.", "inputSchema": schema({"id": string, "max_chars": integer}, ["id"])},
        {"name": "get_task_context", "description": "Build a compact deduplicated task-context bundle.", "inputSchema": schema({"issue_id": string, "specification_id": string, "repositories": strings, "components": strings, "max_chars": integer})},
        {"name": "create_document", "description": "Create a validated Markdown document without overwrite.", "inputSchema": schema({"path": string, "content": string}, ["path", "content"])},
        {"name": "update_document", "description": "Atomically update an existing validated document with optimistic concurrency.", "inputSchema": schema({"path": string, "content": string, "expected_revision": string}, ["path", "content", "expected_revision"])},
        {"name": "update_section", "description": "Append or replace a named section with optimistic concurrency.", "inputSchema": schema({"path": string, "section": string, "content": string, "expected_revision": string, "append": {"type": "boolean"}}, ["path", "section", "content", "expected_revision"])},
        {"name": "create_adr", "description": "Create an ADR from the canonical template.", "inputSchema": schema({"id": string, "short_name": string, "title": string, "status": string}, ["id", "short_name", "title"])},
        {"name": "create_specification", "description": "Create a specification from the canonical template.", "inputSchema": schema({"id": string, "short_name": string, "title": string, "status": string}, ["id", "short_name", "title"])},
        {"name": "update_specification_status", "description": "Update specification status and updated date with optimistic concurrency.", "inputSchema": schema({"id": string, "status": string, "expected_revision": string}, ["id", "status", "expected_revision"])},
        {"name": "update_implementation_result", "description": "Replace a specification Implementation Result section with optimistic concurrency.", "inputSchema": schema({"id": string, "content": string, "expected_revision": string}, ["id", "content", "expected_revision"])},
        {"name": "update_deviations", "description": "Replace a specification Deviations from Specification section with optimistic concurrency.", "inputSchema": schema({"id": string, "content": string, "expected_revision": string}, ["id", "content", "expected_revision"])},
        {"name": "validate_memory_bank", "description": "Run structural, metadata, link, portability, and SDD validation.", "inputSchema": schema({})},
    ]


class MemoryBankAPI:
    def __init__(self, store: MemoryBankStore):
        self.store = store

    def call(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        args = dict(arguments or {})
        handler = getattr(self, f"tool_{name}", None)
        if handler is None:
            raise MemoryBankError(f"Unknown tool: {name}")
        return handler(**args)

    def tool_list_documents(self, limit: int = 100, **filters: Any) -> Any:
        return self.store.list_documents(limit=limit, **filters)

    def tool_get_tree(self, max_chars: int = 20_000) -> Any:
        return self.store.tree(max_chars)

    def tool_get_metadata(self, path: str) -> Any:
        document = self.store.get(path)
        return {
            "path": document.path,
            "metadata": document.metadata,
            "revision": document.revision,
        }

    def tool_get_summary(self, path: str, max_chars: int = 4_000) -> Any:
        return self.store.read_summary(path, max_chars)

    def tool_read_document(self, path: str, max_chars: int = 20_000) -> Any:
        return self.store.read_document(path, max_chars)

    def tool_read_section(self, path: str, section: str, max_chars: int = 10_000) -> Any:
        return self.store.read_section(path, section, max_chars)

    def tool_read_lines(self, path: str, start_line: int, end_line: int, max_chars: int = 10_000) -> Any:
        return self.store.read_lines(path, start_line, end_line, max_chars)

    def tool_search_text(self, query: str, limit: int = 20, max_chars: int = 12_000, **filters: Any) -> Any:
        return self.store.search(query, limit=limit, max_chars=max_chars, **filters)

    def tool_find_exact(self, query: str, limit: int = 20, max_chars: int = 12_000, **filters: Any) -> Any:
        return self.store.search(query, exact=True, limit=limit, max_chars=max_chars, **filters)

    def tool_filter_documents(self, limit: int = 100, **filters: Any) -> Any:
        return self.store.list_documents(limit=limit, **filters)

    def tool_list_related(self, path: str, limit: int = 50) -> Any:
        return self.store.related(path, limit)

    def tool_list_adrs(self, status: str | None = None, limit: int = 100) -> Any:
        return self.store.list_documents(limit=limit, type="decision", status=status)

    def tool_get_adr(self, id: str, max_chars: int = 20_000) -> Any:
        return self.store.read_document(self.store.get_by_id(id, "decision").path, max_chars)

    def tool_list_specifications(self, status: str | None = None, repository: str | None = None, component: str | None = None, limit: int = 100) -> Any:
        return self.store.list_documents(limit=limit, type="specification", status=status, repository=repository, component=component)

    def tool_get_specification(self, id: str, max_chars: int = 30_000) -> Any:
        return self.store.read_document(self.store.get_by_id(id, "specification").path, max_chars)

    def tool_get_task_context(self, **arguments: Any) -> Any:
        return self.store.task_context(**arguments)

    def tool_create_document(self, path: str, content: str) -> Any:
        return self.store.create(path, content)

    def tool_update_document(
        self, path: str, content: str, expected_revision: str
    ) -> Any:
        return self.store.update(
            path, content, expected_revision=expected_revision
        )

    def tool_update_section(
        self,
        path: str,
        section: str,
        content: str,
        expected_revision: str,
        append: bool = False,
    ) -> Any:
        return self.store.update_section(
            path,
            section,
            content,
            expected_revision=expected_revision,
            append=append,
        )

    def tool_create_adr(self, id: str, short_name: str, title: str, status: str = "proposed") -> Any:
        path = f"decisions/{id.casefold()}-{_safe_name(short_name)}.md"
        return self.store.create_from_template(
            template_path="decisions/template.md",
            path=path,
            replacements={
                "ADR-0000": id,
                "Decision title": title,
                "status: proposed": f"status: {status}",
                "YYYY-MM-DD": date.today().isoformat(),
            },
        )

    def tool_create_specification(self, id: str, short_name: str, title: str, status: str = "draft") -> Any:
        path = f"specifications/{id.casefold()}-{_safe_name(short_name)}.md"
        return self.store.create_from_template(
            template_path="specifications/template.md",
            path=path,
            replacements={
                "SPEC-0000": id,
                "Specification title": title,
                "status: draft": f"status: {status}",
                "YYYY-MM-DD": date.today().isoformat(),
            },
        )

    def tool_update_specification_status(
        self, id: str, status: str, expected_revision: str
    ) -> Any:
        path = self.store.get_by_id(id, "specification").path
        return self.store.update_front_matter(
            path,
            {"status": status, "updated": date.today().isoformat()},
            expected_revision=expected_revision,
        )

    def tool_update_implementation_result(
        self, id: str, content: str, expected_revision: str
    ) -> Any:
        path = self.store.get_by_id(id, "specification").path
        return self.store.update_section(
            path,
            "Implementation Result",
            content,
            expected_revision=expected_revision,
        )

    def tool_update_deviations(
        self, id: str, content: str, expected_revision: str
    ) -> Any:
        path = self.store.get_by_id(id, "specification").path
        return self.store.update_section(
            path,
            "Deviations from Specification",
            content,
            expected_revision=expected_revision,
        )

    def tool_validate_memory_bank(self) -> Any:
        return MemoryBankValidator(self.store).run()


def _safe_name(value: str) -> str:
    cleaned = "".join(character.casefold() if character.isalnum() else "-" for character in value)
    return "-".join(part for part in cleaned.split("-") if part)
