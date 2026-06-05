from __future__ import annotations

import json
import sys
from typing import Any


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def print_json(data: Any) -> None:
    sys.stdout.write(dumps(data) + "\n")


def ok(data: Any = None, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True}
    if data is not None:
        payload["data"] = data
    payload.update(extra)
    return payload


def error(message: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": False, "error": message}
    payload.update(extra)
    return payload
