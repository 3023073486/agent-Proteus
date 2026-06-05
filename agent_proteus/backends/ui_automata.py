from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class UiAutomataBackend:
    """Optional UI Automata adapter.

    UI Automata can be exposed as an MCP server or local HTTP service. This
    adapter supports the HTTP shape first because it is easy to compose with a
    Python CLI; MCP hosts can also connect to UI Automata directly.
    """

    name = "ui-automata"

    def __init__(self, url: str | None = None) -> None:
        self.url = (url or os.environ.get("UI_AUTOMATA_URL") or "").rstrip("/")

    def available(self) -> bool:
        return bool(self.url)

    def doctor(self) -> dict[str, Any]:
        if not self.url:
            return {"ok": False, "error": "UI_AUTOMATA_URL is not set"}
        return self._request("GET", "/health")

    def observe(self, target: str = "Proteus", mode: str = "auto") -> dict[str, Any]:
        if not self.url:
            return {"ok": False, "error": "UI_AUTOMATA_URL is not set"}
        return self._request("POST", "/observe", {"target": target, "mode": mode})

    def click(self, x: int, y: int, target: str = "Proteus") -> dict[str, Any]:
        if not self.url:
            return {"ok": False, "error": "UI_AUTOMATA_URL is not set"}
        return self._request("POST", "/click", {"target": target, "x": x, "y": y})

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(f"{self.url}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                text = response.read().decode("utf-8", errors="replace")
                try:
                    parsed: Any = json.loads(text)
                except json.JSONDecodeError:
                    parsed = text
                return {"ok": 200 <= response.status < 300, "status": response.status, "stdout": parsed}
        except urllib.error.URLError as exc:
            return {"ok": False, "error": str(exc), "url": self.url}
