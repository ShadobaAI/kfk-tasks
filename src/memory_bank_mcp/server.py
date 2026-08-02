from __future__ import annotations

import argparse
import asyncio
import contextvars
import json
import logging
import os
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial
from importlib.metadata import version
from typing import Any

import anyio
import uvicorn
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .api import MemoryBankAPI, tool_definitions
from .store import MemoryBankError, MemoryBankStore


LOGGER = logging.getLogger("memory_bank_mcp")
REQUEST_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    "memory_bank_request_id", default="-"
)
SERVER_NAME = "kafka-adapter-memory-bank"
SERVER_VERSION = "0.2.0"


def _integer_environment(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _float_environment(
    name: str, default: float, minimum: float, maximum: float
) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be a number") from error
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _list_environment(name: str) -> tuple[str, ...]:
    raw = os.environ.get(name, "")
    return tuple(
        item.strip()
        for item in raw.replace(";", ",").split(",")
        if item.strip()
    )


@dataclass(frozen=True)
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8767
    endpoint: str = "/mcp"
    allowed_origins: tuple[str, ...] = ()
    request_timeout_seconds: float = 30.0
    max_request_bytes: int = 1_048_576
    max_concurrent_requests: int = 32

    @classmethod
    def from_environment(cls) -> "ServerConfig":
        return cls(
            host=os.environ.get("MEMORY_BANK_HOST", "127.0.0.1"),
            port=_integer_environment("MEMORY_BANK_PORT", 8767, 1, 65535),
            endpoint=os.environ.get("MEMORY_BANK_ENDPOINT", "/mcp"),
            allowed_origins=_list_environment("MEMORY_BANK_ALLOWED_ORIGINS"),
            request_timeout_seconds=_float_environment(
                "MEMORY_BANK_REQUEST_TIMEOUT_SECONDS", 30.0, 0.1, 3600.0
            ),
            max_request_bytes=_integer_environment(
                "MEMORY_BANK_MAX_REQUEST_BYTES", 1_048_576, 1024, 100_000_000
            ),
            max_concurrent_requests=_integer_environment(
                "MEMORY_BANK_MAX_CONCURRENT_REQUESTS", 32, 1, 10_000
            ),
        ).validated()

    def validated(self) -> "ServerConfig":
        if not self.host.strip():
            raise ValueError("host must not be empty")
        if not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if not self.endpoint.startswith("/") or self.endpoint.endswith("/"):
            raise ValueError("endpoint must start with '/' and must not end with '/'")
        if self.endpoint in {"/health/live", "/health/ready"}:
            raise ValueError("MCP endpoint must be separate from health endpoints")
        if self.request_timeout_seconds <= 0:
            raise ValueError("request timeout must be positive")
        if self.max_request_bytes < 1024:
            raise ValueError("max request bytes must be at least 1024")
        if self.max_concurrent_requests < 1:
            raise ValueError("max concurrent requests must be positive")
        return self


def emit_event(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    LOGGER.info(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


class StructuredLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        try:
            parsed = json.loads(message)
            if isinstance(parsed, dict):
                return json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError):
            pass
        payload: dict[str, Any] = {
            "event": "dependency_log",
            "logger": record.name,
            "level": record.levelname.casefold(),
            "message": message,
        }
        if record.exc_info and record.exc_info[0]:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(StructuredLogFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers[:] = [handler]
    root_logger.setLevel(logging.INFO)
    LOGGER.handlers.clear()
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = True


def create_mcp_server(
    store: MemoryBankStore,
    executor: ThreadPoolExecutor,
    executor_capacity: asyncio.Semaphore,
    api: MemoryBankAPI | None = None,
) -> Server[Any]:
    selected_api = api or MemoryBankAPI(store)
    server: Server[Any] = Server(
        SERVER_NAME,
        version=SERVER_VERSION,
        instructions="Read, search, validate, and safely update the Markdown Memory Bank.",
    )

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=definition["name"],
                description=definition["description"],
                inputSchema=definition["inputSchema"],
            )
            for definition in tool_definitions()
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any]
    ) -> Any:
        started = time.perf_counter()
        status = "ok"
        error_category: str | None = None
        operation_path: str | None = None
        try:
            loop = asyncio.get_running_loop()
            context = contextvars.copy_context()
            await executor_capacity.acquire()
            future = loop.run_in_executor(
                executor,
                partial(context.run, selected_api.call, name, arguments),
            )
            future.add_done_callback(
                lambda _: loop.call_soon_threadsafe(executor_capacity.release)
            )
            value = await asyncio.shield(future)
            if isinstance(value, dict):
                operation_path = next(
                    (
                        str(value[key])
                        for key in ("created", "updated")
                        if value.get(key)
                    ),
                    None,
                )
                return value
            text = (
                value
                if isinstance(value, str)
                else json.dumps(value, ensure_ascii=False, indent=2)
            )
            return (
                [types.TextContent(type="text", text=text)],
                {"result": value},
            )
        except MemoryBankError:
            status = "error"
            error_category = "client_error"
            raise
        except Exception:
            status = "error"
            error_category = "internal_error"
            raise
        finally:
            fields: dict[str, Any] = {
                "request_id": REQUEST_ID.get(),
                "method": "tools/call",
                "tool": name,
                "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                "status": status,
            }
            if error_category:
                fields["error_category"] = error_category
            if name.startswith(("create_", "update_")):
                path = operation_path or arguments.get("path")
                if path:
                    fields["path"] = str(path)
            emit_event("tool_call", **fields)

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        resources = [
            types.Resource(
                uri=f"memory-bank:///{document.path}",
                name=document.title,
                description=document.summary[:300],
                mimeType="text/markdown",
            )
            for document in store.documents()
        ]
        resources.insert(
            0,
            types.Resource(
                uri="memory-bank:///tree",
                name="Memory Bank tree",
                mimeType="text/plain",
            ),
        )
        return resources

    @server.read_resource()
    async def read_resource(uri: Any) -> list[ReadResourceContents]:
        text_uri = str(uri)
        prefix = "memory-bank:///"
        if not text_uri.startswith(prefix):
            raise MemoryBankError("Unsupported resource URI")
        path = text_uri[len(prefix) :]
        if path == "tree":
            return [ReadResourceContents(store.tree(), "text/plain")]
        return [
            ReadResourceContents(
                store.read_document(path, 1_000_000), "text/markdown"
            )
        ]

    return server


class RequestPolicyMiddleware:
    """Bound and observe MCP HTTP requests without inspecting document content."""

    def __init__(self, app: ASGIApp, config: ServerConfig):
        self.app = app
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = self._request_id(scope)
        token = REQUEST_ID.set(request_id)
        started = time.perf_counter()
        status_code = 500
        error_category: str | None = None
        method_name = scope.get("method", "")
        tool_name: str | None = None
        response_started = False

        async def observed_send(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii", "ignore")))
                message = {**message, "headers": headers}
            await send(message)

        try:
            if scope.get("path") in {"/health/live", "/health/ready"}:
                await self.app(scope, receive, observed_send)
                return
            if scope.get("path") == self.config.endpoint and method_name == "POST":
                content_length = self._content_length(scope)
                if content_length is not None and content_length > self.config.max_request_bytes:
                    status_code = 413
                    error_category = "request_too_large"
                    await self._error(observed_send, 413, "Request body is too large")
                    return

            if self.semaphore.locked():
                status_code = 429
                error_category = "concurrency_limit"
                await self._error(observed_send, 429, "Too many concurrent requests")
                return
            await self.semaphore.acquire()
            try:
                with anyio.fail_after(self.config.request_timeout_seconds):
                    replay = receive
                    if (
                        scope.get("path") == self.config.endpoint
                        and method_name == "POST"
                    ):
                        messages, body = await self._read_body(receive)
                        if len(body) > self.config.max_request_bytes:
                            status_code = 413
                            error_category = "request_too_large"
                            await self._error(
                                observed_send, 413, "Request body is too large"
                            )
                            return
                        method_name, tool_name = self._operation(body, method_name)
                        replay = self._replay(messages)
                    await self.app(scope, replay, observed_send)
            finally:
                self.semaphore.release()
        except TimeoutError:
            error_category = "timeout"
            status_code = 504
            if not response_started:
                await self._error(observed_send, 504, "Request timed out")
        except Exception as error:
            error_category = "internal_error"
            status_code = 500
            if not response_started:
                await self._error(observed_send, 500, "Internal server error")
            emit_event(
                "request_failed",
                request_id=request_id,
                status=status_code,
                error_category=error_category,
                exception_type=type(error).__name__,
            )
        finally:
            fields: dict[str, Any] = {
                "request_id": request_id,
                "method": method_name,
                "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                "status": status_code,
            }
            if tool_name:
                fields["tool"] = tool_name
            if error_category:
                fields["error_category"] = error_category
            emit_event("http_request", **fields)
            REQUEST_ID.reset(token)

    @staticmethod
    def _request_id(scope: Scope) -> str:
        headers = dict(scope.get("headers", []))
        supplied = headers.get(b"x-request-id", b"").decode("ascii", "ignore")
        if supplied and len(supplied) <= 128 and all(
            character.isalnum() or character in "-_." for character in supplied
        ):
            return supplied
        return uuid.uuid4().hex

    @staticmethod
    def _content_length(scope: Scope) -> int | None:
        try:
            headers = dict(scope.get("headers", []))
            raw = headers.get(b"content-length")
            return int(raw) if raw else None
        except ValueError:
            return None

    async def _read_body(self, receive: Receive) -> tuple[list[Message], bytes]:
        messages: list[Message] = []
        chunks: list[bytes] = []
        while True:
            message = await receive()
            messages.append(message)
            if message["type"] != "http.request":
                break
            chunks.append(message.get("body", b""))
            if sum(map(len, chunks)) > self.config.max_request_bytes:
                break
            if not message.get("more_body", False):
                break
        return messages, b"".join(chunks)

    @staticmethod
    def _replay(messages: list[Message]) -> Receive:
        queue = list(messages)

        async def receive() -> Message:
            if queue:
                return queue.pop(0)
            return {"type": "http.disconnect"}

        return receive

    @staticmethod
    def _operation(body: bytes, fallback: str) -> tuple[str, str | None]:
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict):
                return fallback, None
            method = str(payload.get("method") or fallback)
            params = payload.get("params")
            tool = (
                str(params.get("name"))
                if method == "tools/call"
                and isinstance(params, dict)
                and params.get("name")
                else None
            )
            return method, tool
        except (UnicodeDecodeError, ValueError):
            return fallback, None

    @staticmethod
    async def _error(send: Send, status: int, message: str) -> None:
        body = json.dumps({"error": message}, separators=(",", ":")).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


class StreamableHTTPApp:
    def __init__(self, manager: StreamableHTTPSessionManager):
        self.manager = manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.manager.handle_request(scope, receive, send)


def create_app(
    store: MemoryBankStore | None = None,
    config: ServerConfig | None = None,
    api: MemoryBankAPI | None = None,
) -> ASGIApp:
    selected_store = store or MemoryBankStore.from_environment()
    selected_config = (config or ServerConfig.from_environment()).validated()
    executor = ThreadPoolExecutor(
        max_workers=selected_config.max_concurrent_requests,
        thread_name_prefix="memory-bank-tool",
    )
    executor_capacity = asyncio.Semaphore(
        selected_config.max_concurrent_requests
    )
    mcp_server = create_mcp_server(
        selected_store,
        executor,
        executor_capacity,
        api,
    )
    state = {"ready": False}
    allowed_hosts = [
        selected_config.host,
        f"{selected_config.host}:*",
        "127.0.0.1",
        "127.0.0.1:*",
        "localhost",
        "localhost:*",
        "[::1]",
        "[::1]:*",
    ]
    manager = StreamableHTTPSessionManager(
        app=mcp_server,
        json_response=True,
        stateless=True,
        security_settings=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=allowed_hosts,
            allowed_origins=list(selected_config.allowed_origins),
        ),
    )

    async def live(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def ready(_: Request) -> JSONResponse:
        ready_state = state["ready"] and selected_store.is_ready()
        return JSONResponse(
            {"status": "ready" if ready_state else "not-ready"},
            status_code=200 if ready_state else 503,
        )

    @asynccontextmanager
    async def lifespan(_: Starlette):
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(executor, selected_store.prepare)
            state["ready"] = True
            emit_event(
                "server_started",
                transport="streamable-http",
                mode="stateless",
                mcp_sdk_version=version("mcp"),
                host=selected_config.host,
                port=selected_config.port,
                endpoint=selected_config.endpoint,
            )
            async with manager.run():
                yield
        finally:
            state["ready"] = False
            emit_event("server_stopped", status="ok")
            executor.shutdown(wait=True, cancel_futures=True)

    app = Starlette(
        routes=[
            Route("/health/live", endpoint=live, methods=["GET"]),
            Route("/health/ready", endpoint=ready, methods=["GET"]),
            Route(
                selected_config.endpoint,
                endpoint=StreamableHTTPApp(manager),
                methods=["GET", "POST"],
            ),
        ],
        lifespan=lifespan,
    )
    protected_app: ASGIApp = RequestPolicyMiddleware(app, selected_config)
    if selected_config.allowed_origins:
        return CORSMiddleware(
            protected_app,
            allow_origins=list(selected_config.allowed_origins),
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=[
                "Accept",
                "Content-Type",
                "Last-Event-ID",
                "Mcp-Protocol-Version",
                "Mcp-Session-Id",
                "X-Request-ID",
            ],
            expose_headers=["Mcp-Session-Id", "X-Request-ID"],
        )
    return protected_app


def add_server_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", help="bind host; default MEMORY_BANK_HOST or 127.0.0.1")
    parser.add_argument("--port", type=int, help="TCP port; default MEMORY_BANK_PORT or 8767")
    parser.add_argument("--endpoint", help="MCP path; default MEMORY_BANK_ENDPOINT or /mcp")


def config_from_arguments(arguments: argparse.Namespace) -> ServerConfig:
    environment = ServerConfig.from_environment()
    return ServerConfig(
        host=arguments.host or environment.host,
        port=arguments.port or environment.port,
        endpoint=arguments.endpoint or environment.endpoint,
        allowed_origins=environment.allowed_origins,
        request_timeout_seconds=environment.request_timeout_seconds,
        max_request_bytes=environment.max_request_bytes,
        max_concurrent_requests=environment.max_concurrent_requests,
    ).validated()


def main(argv: list[str] | None = None) -> None:
    configure_logging()
    parser = argparse.ArgumentParser(prog="memory-bank-mcp")
    add_server_arguments(parser)
    config = config_from_arguments(parser.parse_args(argv))
    app = create_app(config=config)
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        access_log=False,
        log_config=None,
    )


if __name__ == "__main__":
    main()
