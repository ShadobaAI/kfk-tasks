from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote

from .store import (
    DRIVE_RE,
    HEADING_RE,
    LINK_RE,
    MemoryBankError,
    MemoryBankStore,
    parse_markdown,
    repository_names,
    slugify_heading,
)


VALID_DOCUMENT_STATUSES = {"draft", "partially-verified", "verified", "deprecated"}
VALID_SPEC_STATUSES = {
    "draft",
    "approved",
    "in-progress",
    "implemented",
    "verified",
    "rejected",
    "superseded",
}
VALID_ADR_STATUSES = {"proposed", "accepted", "rejected", "deprecated", "superseded"}
ABSOLUTE_WINDOWS_RE = re.compile(r"\b[A-Za-z]:[\\/][^\s)`]+")
SOURCE_RE = re.compile(r"^repo:([^:]+):(.+)$")


class MemoryBankValidator:
    def __init__(self, store: MemoryBankStore):
        self.store = store
        self.issues: list[dict[str, Any]] = []

    def add(self, code: str, path: str, message: str, severity: str = "error") -> None:
        self.issues.append(
            {"severity": severity, "code": code, "path": path, "message": message}
        )

    def run(self) -> dict[str, Any]:
        paths = self.store.paths()
        documents = []
        sizes: dict[str, int] = {}
        for path in paths:
            relative = path.relative_to(self.store.root).as_posix()
            sizes[relative] = path.stat().st_size
            try:
                documents.append(self.store.get(relative))
            except (MemoryBankError, UnicodeError) as error:
                self.add("parse-error", relative, str(error))
        ids: defaultdict[str, list[str]] = defaultdict(list)
        linked: set[str] = set()
        paragraphs: defaultdict[str, list[str]] = defaultdict(list)
        known_repositories = repository_names()

        for document in documents:
            path = document.path
            metadata = document.metadata
            if not metadata:
                self.add("missing-front-matter", path, "Document has no YAML front matter")
            if not document.summary:
                self.add("missing-summary", path, "Document has no non-empty Summary section")
            if sizes[path] > 80_000:
                self.add("oversized", path, f"Document is {sizes[path]} bytes", "warning")
            headings = [match.group(2).strip() for match in HEADING_RE.finditer(document.body)]
            duplicate_headings = [
                heading for heading, count in Counter(headings).items() if count > 1
            ]
            for heading in duplicate_headings:
                self.add("duplicate-heading", path, f"Duplicate heading: {heading}", "warning")

            doc_type = str(metadata.get("type", ""))
            identifier = metadata.get("id")
            if identifier:
                ids[str(identifier)].append(path)
            status = str(metadata.get("status", ""))
            allowed = (
                VALID_SPEC_STATUSES
                if doc_type == "specification"
                else VALID_ADR_STATUSES
                if doc_type == "decision"
                else VALID_DOCUMENT_STATUSES
            )
            if status and status not in allowed:
                self.add("invalid-status", path, f"Invalid {doc_type or 'document'} status: {status}")
            if doc_type == "specification":
                if not re.fullmatch(r"SPEC-\d{4}", str(identifier or "")):
                    self.add("invalid-spec-id", path, "Specification id must match SPEC-NNNN")
                for field in ("affected_repositories", "affected_components", "related_adrs"):
                    if field not in metadata:
                        self.add("missing-spec-metadata", path, f"Missing field: {field}")
            if doc_type == "decision" and not re.fullmatch(r"ADR-\d{4}", str(identifier or "")):
                self.add("invalid-adr-id", path, "Decision id must match ADR-NNNN")
            if status in {"verified", "partially-verified"} and not metadata.get("sources"):
                self.add("missing-sources", path, "Verified content requires sources")
            self._validate_sources(path, metadata.get("sources"), known_repositories)
            self._validate_links(document, linked)

            for paragraph in re.split(r"\n\s*\n", document.body):
                normalized = re.sub(r"\s+", " ", paragraph.strip()).casefold()
                if len(normalized) >= 180 and not normalized.startswith(("```", "|")):
                    paragraphs[normalized].append(path)
            for match in ABSOLUTE_WINDOWS_RE.finditer(document.text):
                self.add(
                    "machine-path",
                    path,
                    f"Machine-specific absolute path: {match.group(0)}",
                )

        for identifier, locations in ids.items():
            if len(locations) > 1:
                for path in locations:
                    self.add("duplicate-id", path, f"Duplicate id {identifier}: {locations}")
        for _, locations in paragraphs.items():
            unique = sorted(set(locations))
            if len(unique) > 1:
                self.add(
                    "duplicate-fragment",
                    unique[0],
                    f"Possible duplicate paragraph in: {', '.join(unique)}",
                    "warning",
                )
        for document in documents:
            if document.path == "README.md" or document.path.endswith("/template.md"):
                continue
            if document.path not in linked:
                self.add("orphan", document.path, "Document is not linked by another document", "warning")
        for expected in (
            "architecture/overview.md",
            "repositories.md",
            "development/navigation.md",
            "agents/instructions.md",
            "specifications/README.md",
            "decisions/README.md",
        ):
            if expected not in linked:
                self.add("missing-navigation", "README.md", f"Root navigation misses {expected}")

        return {
            "documents": len(documents),
            "total_size": sum(sizes.values()),
            "sizes": sizes,
            "issues": sorted(
                self.issues,
                key=lambda item: (
                    0 if item["severity"] == "error" else 1,
                    item["path"],
                    item["code"],
                ),
            ),
            "errors": sum(issue["severity"] == "error" for issue in self.issues),
            "warnings": sum(issue["severity"] == "warning" for issue in self.issues),
        }

    def _validate_sources(
        self, path: str, sources: Any, known_repositories: set[str]
    ) -> None:
        if not sources:
            return
        values = sources if isinstance(sources, list) else [sources]
        for source in values:
            if isinstance(source, dict):
                repository = source.get("repo")
                source_path = source.get("path")
                if not repository or not source_path:
                    self.add("invalid-source", path, f"Invalid source mapping: {source}")
                elif known_repositories and repository not in known_repositories:
                    self.add("invalid-source", path, f"Unknown repository: {repository}")
                continue
            match = SOURCE_RE.match(str(source))
            if not match:
                self.add("invalid-source", path, f"Invalid source reference: {source}")
            elif known_repositories and match.group(1) not in known_repositories:
                self.add("invalid-source", path, f"Unknown repository: {match.group(1)}")

    def _validate_links(self, document: Any, linked: set[str]) -> None:
        for raw_target in LINK_RE.findall(document.body):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if DRIVE_RE.match(target) or target.startswith(("/", "\\\\")):
                self.add("non-portable-link", document.path, f"Non-portable link: {target}")
                continue
            target_path, _, anchor = target.partition("#")
            target_path = unquote(target_path)
            if not target_path:
                target_document = document
            else:
                combined = PurePosixPath(document.path).parent / target_path.replace("\\", "/")
                parts: list[str] = []
                escaped_root = False
                for part in combined.parts:
                    if part == "..":
                        if parts:
                            parts.pop()
                        else:
                            escaped_root = True
                    elif part not in ("", "."):
                        parts.append(part)
                normalized = PurePosixPath(*parts).as_posix()
                if not normalized.endswith(".md"):
                    continue
                if escaped_root:
                    repository_root = self.store.root.parent
                    source = self.store.root / document.path
                    external_target = (source.parent / target_path).resolve(strict=False)
                    try:
                        external_target.relative_to(repository_root.resolve(strict=False))
                    except ValueError:
                        self.add(
                            "non-portable-link",
                            document.path,
                            f"Link escapes repository: {target}",
                        )
                        continue
                    if not external_target.is_file():
                        self.add("broken-link", document.path, f"Missing target: {target}")
                        continue
                    try:
                        target_document = parse_markdown(
                            external_target.read_text(encoding="utf-8"),
                            external_target.relative_to(repository_root).as_posix(),
                        )
                    except (OSError, UnicodeError, MemoryBankError):
                        self.add("broken-link", document.path, f"Unreadable target: {target}")
                        continue
                else:
                    linked.add(normalized)
                    try:
                        target_document = self.store.get(normalized)
                    except MemoryBankError:
                        self.add("broken-link", document.path, f"Missing target: {target}")
                        continue
            if anchor:
                anchors = {slugify_heading(heading) for heading in target_document.headings}
                if anchor.casefold() not in anchors:
                    self.add("broken-anchor", document.path, f"Missing anchor: {target}")
