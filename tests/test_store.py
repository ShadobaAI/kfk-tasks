from __future__ import annotations

import multiprocessing
import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
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


def competing_process_update(
    root: str,
    revision: str,
    title: str,
    start,
    results,
) -> None:
    store = MemoryBankStore(Path(root))
    start.wait(timeout=5)
    try:
        store.update(
            "README.md",
            document(title),
            expected_revision=revision,
        )
        results.put("updated")
    except MemoryBankError as error:
        results.put(str(error))


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
        revision = self.store.get("notes/новый.md").revision
        result = self.store.update_section(
            "notes/новый.md",
            "Details",
            "Replacement",
            expected_revision=revision,
        )
        self.assertEqual("Replacement", self.store.read_section("notes/новый.md", "Details"))
        self.store.update_section(
            "notes/новый.md",
            "Details",
            "Appended",
            expected_revision=result["revision"],
            append=True,
        )
        self.assertIn("Appended", self.store.read_section("notes/новый.md", "Details"))

    def test_revision_conflict_prevents_lost_update(self) -> None:
        revision = self.store.get("README.md").revision
        self.store.update(
            "README.md", document("First writer"), expected_revision=revision
        )
        with self.assertRaisesRegex(MemoryBankError, "Revision conflict"):
            self.store.update(
                "README.md", document("Stale writer"), expected_revision=revision
            )

    def test_cross_process_lock_serializes_store_instances(self) -> None:
        first_store = MemoryBankStore(self.root)
        second_store = MemoryBankStore(self.root)
        revision = first_store.get("README.md").revision
        barrier = threading.Barrier(2)

        def update(store: MemoryBankStore, title: str) -> str:
            barrier.wait(timeout=2)
            try:
                store.update(
                    "README.md",
                    document(title),
                    expected_revision=revision,
                )
                return "updated"
            except MemoryBankError as error:
                return str(error)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda item: update(*item),
                    [(first_store, "First"), (second_store, "Second")],
                )
            )
        self.assertEqual(1, results.count("updated"))
        self.assertEqual(
            1,
            sum("Revision conflict" in result for result in results),
        )

    def test_cross_process_lock_prevents_create_overwrite(self) -> None:
        first_store = MemoryBankStore(self.root)
        second_store = MemoryBankStore(self.root)
        barrier = threading.Barrier(2)

        def create(store: MemoryBankStore, title: str) -> str:
            barrier.wait(timeout=2)
            try:
                store.create("notes/shared.md", document(title))
                return "created"
            except MemoryBankError as error:
                return str(error)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda item: create(*item),
                    [(first_store, "First"), (second_store, "Second")],
                )
            )
        self.assertEqual(1, results.count("created"))
        self.assertEqual(
            1,
            sum("Create will not overwrite" in result for result in results),
        )

    def test_file_lock_serializes_independent_processes(self) -> None:
        revision = self.store.get("README.md").revision
        context = multiprocessing.get_context("spawn")
        start = context.Event()
        results = context.Queue()
        processes = [
            context.Process(
                target=competing_process_update,
                args=(
                    str(self.root),
                    revision,
                    title,
                    start,
                    results,
                ),
            )
            for title in ("First process", "Second process")
        ]
        for process in processes:
            process.start()
        start.set()
        for process in processes:
            process.join(timeout=10)
            if process.is_alive():
                process.kill()
                process.join(timeout=2)
                self.fail("Competing update process did not stop")
            self.assertEqual(0, process.exitcode)
        outcomes = [results.get(timeout=2) for _ in processes]
        self.assertEqual(1, outcomes.count("updated"))
        self.assertEqual(
            1,
            sum("Revision conflict" in outcome for outcome in outcomes),
        )

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
        revision = self.store.get("README.md").revision
        with patch("memory_bank_mcp.store.os.replace", side_effect=OSError("simulated")):
            with self.assertRaises(OSError):
                self.store.update(
                    "README.md",
                    document("Changed"),
                    expected_revision=revision,
                )
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
