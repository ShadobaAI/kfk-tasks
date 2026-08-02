from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from memory_bank_mcp.api import MemoryBankAPI, tool_definitions
from memory_bank_mcp.store import MemoryBankStore


TASK_ROOT = Path(__file__).resolve().parents[1]


class APIServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryBankStore(TASK_ROOT / "memory-bank")

    def test_tool_list_and_summary_call(self) -> None:
        names = {item["name"] for item in tool_definitions()}
        self.assertIn("get_task_context", names)
        self.assertIn("create_specification", names)
        response = MemoryBankAPI(self.store).call(
            "get_summary", {"path": "README.md"}
        )
        self.assertIn("compact project knowledge index", response["summary"])
        self.assertEqual(64, len(response["revision"]))

    def test_resources_include_tree_and_cyrillic_content(self) -> None:
        self.assertIn(
            "кфкИнтеграция",
            self.store.read_document(
                "repositories/kafka-adapter.md", max_chars=1_000_000
            ),
        )

    def test_adr_and_specification_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "memory-bank"
            (root / "decisions").mkdir(parents=True)
            (root / "specifications").mkdir()
            shutil.copy(
                TASK_ROOT / "memory-bank" / "decisions" / "template.md",
                root / "decisions" / "template.md",
            )
            shutil.copy(
                TASK_ROOT / "memory-bank" / "specifications" / "template.md",
                root / "specifications" / "template.md",
            )
            api = MemoryBankAPI(MemoryBankStore(root))

            api.call(
                "create_adr",
                {
                    "id": "ADR-0042",
                    "short_name": "queue-policy",
                    "title": "Queue policy",
                },
            )
            api.call(
                "create_specification",
                {
                    "id": "SPEC-0042",
                    "short_name": "queue-policy",
                    "title": "Queue policy",
                },
            )
            specification_path = "specifications/spec-0042-queue-policy.md"
            api.store.update_front_matter(
                specification_path,
                {
                    "affected_repositories": ["kafka-adapter"],
                    "affected_components": ["queues"],
                    "related_adrs": ["ADR-0042"],
                },
                expected_revision=api.store.get(specification_path).revision,
            )
            result = api.call(
                "update_specification_status",
                {
                    "id": "SPEC-0042",
                    "status": "in-progress",
                    "expected_revision": api.store.get(specification_path).revision,
                },
            )
            result = api.call(
                "update_implementation_result",
                {
                    "id": "SPEC-0042",
                    "content": "Implemented in a temporary test store.",
                    "expected_revision": result["revision"],
                },
            )
            api.call(
                "update_deviations",
                {
                    "id": "SPEC-0042",
                    "content": "No deviations.",
                    "expected_revision": result["revision"],
                },
            )

            cards = api.call(
                "list_specifications",
                {"repository": "kafka-adapter", "component": "queues"},
            )
            self.assertEqual([specification_path], [item["path"] for item in cards])
            context = api.call(
                "get_task_context",
                {"specification_id": "SPEC-0042", "max_chars": 10_000},
            )
            self.assertEqual(
                {specification_path, "decisions/adr-0042-queue-policy.md"},
                {item["path"] for item in context["documents"]},
            )
            self.assertIn(
                "Implemented in a temporary test store.",
                api.call("get_specification", {"id": "SPEC-0042"}),
            )


if __name__ == "__main__":
    unittest.main()
