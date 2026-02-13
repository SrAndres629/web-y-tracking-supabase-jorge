from __future__ import annotations

import json
import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    command: str
    args: list[str]
    env: dict[str, str]


class NeuroMCPClient:
    """Minimal stdio JSON-RPC client for the NeuroVision MCP server."""

    def __init__(self, config_path: str | None = None, timeout_sec: float = 10.0) -> None:
        self.timeout_sec = timeout_sec
        self._request_id = 0
        self._proc: subprocess.Popen[str] | None = None
        self._lock = threading.Lock()
        self.server = self._resolve_server(config_path)

    @staticmethod
    def _resolve_server(config_path: str | None) -> MCPServerConfig:
        config_file = Path(config_path) if config_path else Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
        if config_file.exists():
            try:
                content = json.loads(config_file.read_text(encoding="utf-8"))
                neuro = content.get("mcpServers", {}).get("neurovision")
                if isinstance(neuro, dict):
                    return MCPServerConfig(
                        command=str(neuro.get("command", "python")),
                        args=[str(v) for v in neuro.get("args", [])],
                        env={str(k): str(v) for k, v in neuro.get("env", {}).items()},
                    )
            except Exception as exc:
                LOGGER.exception("Failed loading external mcp_config.json: %s", exc)

        local_path = Path("neurovision/mcp_server.py")
        if local_path.exists():
            return MCPServerConfig(command="python", args=[str(local_path)], env={})
        raise FileNotFoundError("NeuroVision MCP server not found in external config or local path.")

    def start(self) -> None:
        if self._proc and self._proc.poll() is None:
            return
        try:
            self._proc = subprocess.Popen(
                [self.server.command, *self.server.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env={**os.environ, **self.server.env},
            )
        except Exception as exc:
            raise RuntimeError(f"Could not start NeuroVision MCP server: {exc}") from exc
        self._safe_request("initialize", {"clientInfo": {"name": "project-ego-v2", "version": "2.0"}})

    def stop(self) -> None:
        if not self._proc:
            return
        try:
            self._safe_request("shutdown", {})
        except Exception:
            LOGGER.debug("MCP shutdown request failed.", exc_info=True)
        finally:
            self._proc.terminate()
            self._proc = None

    def list_files(self, pattern: str = ".") -> Any:
        return self._tool_call("list_files", {"pattern": pattern})

    def read_file(self, path: str) -> Any:
        return self._tool_call("read_file", {"path": path})

    def _tool_call(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        return self._safe_request("tools/call", {"name": tool_name, "arguments": arguments})

    def _safe_request(self, method: str, params: dict[str, Any]) -> Any:
        with self._lock:
            return self._request(method, params)

    def _request(self, method: str, params: dict[str, Any]) -> Any:
        if not self._proc or self._proc.poll() is not None:
            self.start()
        assert self._proc and self._proc.stdin and self._proc.stdout
        self._request_id += 1
        message = {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
        self._proc.stdin.write(json.dumps(message) + "\n")
        self._proc.stdin.flush()

        start = time.time()
        while time.time() - start < self.timeout_sec:
            line = self._proc.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
            try:
                payload = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            if payload.get("id") != self._request_id:
                continue
            if "error" in payload:
                raise RuntimeError(f"MCP error: {payload['error']}")
            return payload.get("result")
        raise TimeoutError(f"MCP request timeout for method '{method}'.")
