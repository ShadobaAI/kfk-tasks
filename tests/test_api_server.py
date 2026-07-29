from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from memory_bank_mcp.api import MemoryBankAPI, tool_definitions
from memory_bank_mcp.server import MCPServer
from memory_bank_mcp.store import MemoryBankStore


TASK_ROOT = Path(__file__).resolve().parents[1]


class APIServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryBankStore(TASK_ROOT / "memory-bank")
        self.server = MCPServer(self.store)

    def test_tool_list_and_summary_call(self) -> None:
        names = {item["name"] for item in tool_definitions()}
        self.assertIn("get_task_context", names)
        self.assertIn("create_specification", names)
        response = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "get_summary", "arguments": {"path": "README.md"}},
            }
        )
        self.assertFalse(response["result"]["isError"])
        self.assertIn("Kafka Adapter Memory Bank", response["result"]["content"][0]["text"])

    def test_resources_include_tree_and_cyrillic_content(self) -> None:
        response = self.server.handle({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
        uris = {item["uri"] for item in response["result"]["resources"]}
        self.assertIn("memory-bank:///tree", uris)
        read = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/read",
                "params": {"uri": "memory-bank:///repositories/kafka-adapter.md"},
            }
        )
        self.assertIn("кфкИнтеграция", read["result"]["contents"][0]["text"])

    def test_stdio_startup(self) -> None:
        environment = os.environ.copy()
        environment["KAFKA_PROJECTS_ROOT"] = str(TASK_ROOT.parent)
        environment["PYTHONPATH"] = str(TASK_ROOT / "src")
        process = subprocess.Popen(
            [sys.executable, "-m", "memory_bank_mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=environment,
        )
        request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}},
        }
        stdout, stderr = process.communicate(json.dumps(request, ensure_ascii=False) + "\n", timeout=10)
        self.assertEqual("", stderr)
        response = json.loads(stdout.strip())
        self.assertEqual("kafka-adapter-memory-bank", response["result"]["serverInfo"]["name"])

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
            )
            api.call(
                "update_specification_status",
                {"id": "SPEC-0042", "status": "in-progress"},
            )
            api.call(
                "update_implementation_result",
                {
                    "id": "SPEC-0042",
                    "content": "Implemented in a temporary test store.",
                },
            )
            api.call(
                "update_deviations",
                {"id": "SPEC-0042", "content": "No deviations."},
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
