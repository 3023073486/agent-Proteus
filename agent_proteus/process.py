from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def which(command: str) -> str | None:
    return shutil.which(command)


def command_invocation(command: str) -> list[str]:
    resolved = shutil.which(command) or command
    suffix = Path(resolved).suffix.lower()
    if suffix in {".bat", ".cmd"}:
        return ["cmd.exe", "/d", "/c", resolved]
    return [resolved]


def run_json_command(command: list[str], timeout: int = 120) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    parsed: Any = stdout
    if stdout:
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = stdout
    result: dict[str, Any] = {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "command": command,
        "stdout": parsed,
    }
    if stderr:
        result["stderr"] = stderr
    return result
