from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memory_bank_mcp.store import MemoryBankError, MemoryBankStore


def document(title: str = "Sample", status: str = "draft", extra: str = "") -> str:
    return f"""---
title: {title}
type: note
status: {status}
updated: 2026-07-29
{extra}---

# {title}

## Summary

- Compact summary for {title}.

## Details

Kafka and кфкИнтеграция details.
"""


class StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "memory-bank"
        self.root.mkdir()
        (self.root / "README.md").write_text(document("Index"), encoding="utf-8")
        (self.root / "кириллица.md").write_text(document("Кириллица"), encoding="utf-8")
        self.store = MemoryBankStore(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_bounded_reads_search_and_lines(self) -> None:
        self.assertIn("[truncated]", self.store.read_document("README.md", 60))
        summary = self.store.read_summary("README.md", 1000)
        self.assertIn("Compact summary", summary["summary"])
        self.assertIn("Kafka", self.store.read_section("README.md", "Details"))
        lines = self.store.read_lines("README.md", 1, 3)
        self.assertEqual(1, lines["start_line"])
        result = self.store.search("кфкИнтеграция", limit=2)
        self.assertEqual(2, result["count"])
        exact = self.store.search("Compact summary for Index.", exact=True)
        self.assertEqual(1, exact["count"])

    def test_filters_and_context(self) -> None:
        (self.root / "repo.md").write_text(
            document("Repo", extra="repository: kafka-adapter\ncomponents:\n  - queues\n"),
            encoding="utf-8",
        )
        cards = self.store.list_documents(repository="kafka-adapter")
        self.assertEqual(["repo.md"], [card["path"] for card in cards])
        context = self.store.task_context(
            repositories=["kafka-adapter"], components=["queues"], max_chars=5000
        )
        self.assertIn("repo.md", [item["path"] for item in context["documents"]])

    def test_alias_filters_and_normalized_related_paths(self) -> None:
        (self.root / "architecture").mkdir()
        (self.root / "repositories").mkdir()
        (self.root / "architecture" / "overview.md").write_text(
            document(
                "Architecture",
                extra=(
                    "affected_repositories:\n"
                    "  - kafka-adapter\n"
                    "affected_components:\n"
                    "  - queues\n"
                ),
            ),
            encoding="utf-8",
        )
        (self.root / "repositories" / "adapter.md").write_text(
            document(
                "Adapter",
                extra="related:\n  - ../architecture/overview.md\n",
            ),
            encoding="utf-8",
        )
        filtered = self.store.list_documents(
            repository="kafka-adapter", component="queues"
        )
        self.assertEqual(
            ["architecture/overview.md"], [item["path"] for item in filtered]
        )
        related = self.store.related("repositories/adapter.md")
        self.assertEqual("architecture/overview.md", related[0]["path"])

    def test_create_update_section_and_overwrite_protection(self) -> None:
        self.store.create("notes/новый.md", document("Новый"))
        with self.assertRaises(MemoryBankError):
            self.store.create("notes/новый.md", document("Overwrite"))
        self.store.update_section("notes/новый.md", "Details", "Replacement")
        self.assertEqual("Replacement", self.store.read_section("notes/новый.md", "Details"))
        self.store.update_section("notes/новый.md", "Details", "Appended", append=True)
        self.assertIn("Appended", self.store.read_section("notes/новый.md", "Details"))

    def test_rejects_escape_and_non_markdown_paths(self) -> None:
        rejected = [
            "../outside.md",
            "..\\outside.md",
            "C:\\temp\\outside.md",
            "\\\\server\\share\\outside.md",
            "//server/share/outside.md",
            "/absolute.md",
            "notes/file.txt",
        ]
        for value in rejected:
            with self.subTest(value=value):
                with self.assertRaises(MemoryBankError):
                    self.store.resolve(value, for_write=True)

    def test_atomic_failure_preserves_existing_content(self) -> None:
        original = (self.root / "README.md").read_text(encoding="utf-8")
        with patch("memory_bank_mcp.store.os.replace", side_effect=OSError("simulated")):
            with self.assertRaises(OSError):
                self.store.update("README.md", document("Changed"))
        self.assertEqual(original, (self.root / "README.md").read_text(encoding="utf-8"))
        self.assertEqual([], list(self.root.glob("*.tmp")))

    @unittest.skipIf(not hasattr(os, "symlink"), "symlinks unsupported")
    def test_symlink_escape_is_rejected_when_creation_is_permitted(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        link = self.root / "link"
        try:
            os.symlink(outside, link, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation not permitted")
        with self.assertRaises(MemoryBankError):
            self.store.resolve("link/escape.md", for_write=True)


if __name__ == "__main__":
    unittest.main()
