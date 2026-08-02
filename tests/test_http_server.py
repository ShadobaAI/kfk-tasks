from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from starlette.testclient import TestClient

from memory_bank_mcp.api import MemoryBankAPI
from memory_bank_mcp.server import (
    LOGGER,
    RequestPolicyMiddleware,
    ServerConfig,
    create_app,
)
from memory_bank_mcp.store import MemoryBankStore


TASK_ROOT = Path(__file__).resolve().parents[1]
MCP_HEADERS = {
    "host": "127.0.0.1:8765",
    "accept": "application/json, text/event-stream",
    "content-type": "application/json",
}
INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "integration-test", "version": "1"},
    },
}
TOOL_CALL_HEADERS = {
    **MCP_HEADERS,
    "mcp-protocol-version": "2025-11-25",
}


class BlockingAPI(MemoryBankAPI):
    def __init__(self, store: MemoryBankStore, started: threading.Event):
        super().__init__(store)
        self.started = started

    def call(self, name: str, arguments: dict | None = None):
        if name == "get_summary":
            self.started.set()
            time.sleep(0.25)
        return super().call(name, arguments)


class HTTPServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryBankStore(TASK_ROOT / "memory-bank")

    def test_health_endpoints_and_graceful_lifespan(self) -> None:
        app = create_app(self.store, ServerConfig())
        with self.assertLogs(LOGGER, level=logging.INFO) as captured:
            with TestClient(app) as client:
                self.assertEqual(200, client.get("/health/live").status_code)
                ready = client.get("/health/ready")
                self.assertEqual(200, ready.status_code)
                self.assertEqual({"status": "ready"}, ready.json())
        output = "\n".join(captured.output)
        self.assertIn('"event":"server_started"', output)
        self.assertIn('"event":"server_stopped"', output)

    def test_invalid_origin_is_rejected(self) -> None:
        app = create_app(self.store, ServerConfig())
        with TestClient(app) as client:
            response = client.post(
                "/mcp",
                headers={**MCP_HEADERS, "origin": "https://evil.example"},
                json=INITIALIZE,
            )
        self.assertEqual(403, response.status_code)

    def test_allowed_origin_supports_cors_preflight(self) -> None:
        origin = "http://localhost:3000"
        app = create_app(
            self.store,
            ServerConfig(allowed_origins=(origin,)),
        )
        with TestClient(app) as client:
            response = client.options(
                "/mcp",
                headers={
                    "origin": origin,
                    "access-control-request-method": "POST",
                    "access-control-request-headers": (
                        "content-type,mcp-protocol-version"
                    ),
                },
            )
            initialize = client.post(
                "/mcp",
                headers={**MCP_HEADERS, "origin": origin},
                json=INITIALIZE,
            )
        self.assertEqual(200, response.status_code)
        self.assertEqual(origin, response.headers["access-control-allow-origin"])
        self.assertIn(
            "mcp-protocol-version",
            response.headers["access-control-allow-headers"].casefold(),
        )
        self.assertEqual(200, initialize.status_code)
        self.assertEqual(
            origin,
            initialize.headers["access-control-allow-origin"],
        )

    def test_oversized_request_is_rejected(self) -> None:
        config = ServerConfig(max_request_bytes=1024)
        app = create_app(self.store, config)
        with TestClient(app) as client:
            response = client.post(
                "/mcp",
                headers=MCP_HEADERS,
                content=b"x" * 1025,
            )
        self.assertEqual(413, response.status_code)
        self.assertIn("too large", response.json()["error"])

    def test_timeout_and_concurrency_limit(self) -> None:
        async def scenario() -> tuple[int, int, int]:
            async def slow_app(scope, receive, send):
                await asyncio.sleep(0.15)
                await send(
                    {
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [],
                    }
                )
                await send({"type": "http.response.body", "body": b"ok"})

            timeout_app = RequestPolicyMiddleware(
                slow_app,
                ServerConfig(
                    request_timeout_seconds=0.02,
                    max_concurrent_requests=1,
                ),
            )
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=timeout_app),
                base_url="http://test",
            ) as client:
                timeout_response = await client.get("/mcp")

            limited_app = RequestPolicyMiddleware(
                slow_app,
                ServerConfig(
                    request_timeout_seconds=1,
                    max_concurrent_requests=1,
                ),
            )
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=limited_app),
                base_url="http://test",
            ) as client:
                first = asyncio.create_task(client.get("/mcp"))
                await asyncio.sleep(0.02)
                second = await client.get("/mcp")
                first_response = await first
            return (
                timeout_response.status_code,
                first_response.status_code,
                second.status_code,
            )

        self.assertEqual((504, 200, 429), asyncio.run(scenario()))

    def test_blocking_tool_times_out_without_blocking_health(self) -> None:
        started = threading.Event()
        config = ServerConfig(
            request_timeout_seconds=0.05,
            max_concurrent_requests=1,
        )
        app = create_app(self.store, config, BlockingAPI(self.store, started))
        tool_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_summary",
                "arguments": {"path": "README.md"},
            },
        }
        with TestClient(app) as client:
            initialize = client.post(
                "/mcp",
                headers=MCP_HEADERS,
                json=INITIALIZE,
            )
            self.assertEqual(200, initialize.status_code)
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    client.post,
                    "/mcp",
                    headers=TOOL_CALL_HEADERS,
                    json=tool_call,
                )
                self.assertTrue(started.wait(timeout=1))
                health_started = time.perf_counter()
                health = client.get("/health/ready")
                health_duration = time.perf_counter() - health_started
                response = future.result(timeout=2)
        self.assertEqual(200, health.status_code)
        self.assertLess(health_duration, 0.1)
        self.assertEqual(504, response.status_code)

    def test_real_streamable_http_initialization_and_tool_call(self) -> None:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        environment = os.environ.copy()
        environment["KAFKA_PROJECTS_ROOT"] = str(TASK_ROOT.parent)
        environment["PYTHONPATH"] = str(TASK_ROOT / "src")
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "memory_bank_mcp.server",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=environment,
            creationflags=(
                getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                if os.name == "nt"
                else 0
            ),
        )
        try:
            health_url = f"http://127.0.0.1:{port}/health/ready"
            deadline = time.monotonic() + 10
            while True:
                try:
                    with urllib.request.urlopen(health_url, timeout=0.5) as response:
                        if response.status == 200:
                            break
                except OSError:
                    if process.poll() is not None:
                        stderr = process.stderr.read() if process.stderr else ""
                        self.fail(f"Server exited before readiness: {stderr}")
                if time.monotonic() >= deadline:
                    self.fail("Server did not become ready")
                time.sleep(0.05)

            async def call() -> tuple[str, str]:
                async with streamable_http_client(
                    f"http://127.0.0.1:{port}/mcp"
                ) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        initialized = await session.initialize()
                        result = await session.call_tool(
                            "get_summary", {"path": "README.md"}
                        )
                        summary = result.structuredContent or {}
                        return initialized.serverInfo.name, str(summary.get("summary"))

            server_name, summary = asyncio.run(call())
            self.assertEqual("kafka-adapter-memory-bank", server_name)
            self.assertIn("compact project knowledge index", summary)
        finally:
            if process.poll() is None:
                if os.name == "nt":
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        stderr = process.stderr.read() if process.stderr else ""
        records = [
            json.loads(line)
            for line in stderr.splitlines()
            if line.strip()
        ]
        self.assertTrue(records)
        self.assertTrue(all(isinstance(record, dict) for record in records))
        self.assertIn("server_stopped", {record.get("event") for record in records})


if __name__ == "__main__":
    unittest.main()
