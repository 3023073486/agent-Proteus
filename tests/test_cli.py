from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys


def _resolve_cli() -> list[str]:
    force = os.environ.get("AGENT_PROTEUS_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which("agent-proteus")
    if path:
        return [path]
    if force:
        raise RuntimeError("agent-proteus not found in PATH. Install with: python -m pip install -e .")
    return [sys.executable, "-m", "agent_proteus"]


def _run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*_resolve_cli(), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def _json(args: list[str]) -> dict:
    result = _run(["--json", *args])
    return json.loads(result.stdout)


def test_help_lists_core_commands() -> None:
    result = _run(["--help"])
    assert "doctor" in result.stdout
    assert "observe" in result.stdout
    assert "mcp" in result.stdout


def test_doctor_json_has_backend_sections() -> None:
    data = _json(["doctor"])
    assert data["ok"] is True
    assert "backends" in data
    assert "ui_automata" in data["backends"]
    assert "desktopctl" in data["backends"]
    assert "proteus_bridge" in data["backends"]


def test_windows_json_is_machine_readable() -> None:
    data = _json(["windows"])
    assert isinstance(data, dict)
    assert "ok" in data
