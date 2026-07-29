from __future__ import annotations

import json
import sys
import traceback
from typing import Any

from .api import MemoryBankAPI, tool_definitions
from .store import MemoryBankError, MemoryBankStore


PROTOCOL_VERSION = "2024-11-05"


class MCPServer:
    def __init__(self, store: MemoryBankStore | None = None):
        self.store = store or MemoryBankStore.from_environment()
        self.api = MemoryBankAPI(self.store)

    def handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")
        if request_id is None:
            return None
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}, "resources": {}},
                    "serverInfo": {"name": "kafka-adapter-memory-bank", "version": "0.1.0"},
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": tool_definitions()}
            elif method == "tools/call":
                params = request.get("params") or {}
                value = self.api.call(params.get("name", ""), params.get("arguments"))
                text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
                result = {
                    "content": [{"type": "text", "text": text}],
                    "structuredContent": value if isinstance(value, (dict, list)) else {"result": value},
                    "isError": False,
                }
            elif method == "resources/list":
                resources = [
                    {
                        "uri": f"memory-bank:///{document.path}",
                        "name": document.title,
                        "description": document.summary[:300],
                        "mimeType": "text/markdown",
                    }
                    for document in self.store.documents()
                ]
                resources.insert(
                    0,
                    {
                        "uri": "memory-bank:///tree",
                        "name": "Memory Bank tree",
                        "mimeType": "text/plain",
                    },
                )
                result = {"resources": resources}
            elif method == "resources/read":
                uri = str((request.get("params") or {}).get("uri", ""))
                prefix = "memory-bank:///"
                if not uri.startswith(prefix):
                    raise MemoryBankError("Unsupported resource URI")
                path = uri[len(prefix) :]
                if path == "tree":
                    result = {"contents": [{"uri": uri, "mimeType": "text/plain", "text": self.store.tree()}]}
                else:
                    result = {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": self.store.read_document(path, 1_000_000)}]}
            else:
                return self._error(request_id, -32601, f"Method not found: {method}")
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except (MemoryBankError, TypeError, ValueError) as error:
            return self._error(request_id, -32602, str(error))
        except Exception as error:  # pragma: no cover - defensive protocol boundary
            traceback.print_exc(file=sys.stderr)
            return self._error(request_id, -32603, str(error))

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def main() -> None:
    server = MCPServer()
    for raw_line in sys.stdin.buffer:
        if not raw_line.strip():
            continue
        try:
            request = json.loads(raw_line)
            response = server.handle(request)
        except json.JSONDecodeError as error:
            response = MCPServer._error(None, -32700, str(error))
        if response is not None:
            encoded = json.dumps(response, ensure_ascii=False, separators=(",", ":"))
            sys.stdout.buffer.write(encoded.encode("utf-8") + b"\n")
            sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()

