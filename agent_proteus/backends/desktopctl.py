from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from agent_proteus.process import command_invocation, run_json_command, which


class DesktopCtlBackend:
    """Optional DesktopCtl adapter.

    DesktopCtl is treated as an external executable because its exact command
    surface can evolve. Users can override subcommands through environment
    variables without changing agent-Proteus code.
    """

    name = "desktopctl"

    def __init__(self, command: str | None = None) -> None:
        self.command = command or os.environ.get("DESKTOPCTL", "desktopctl")

    def available(self) -> bool:
        return bool(which(self.command) or Path(self.command).exists())

    def doctor(self) -> dict[str, Any]:
        if not self.available():
            return {"ok": False, "error": "desktopctl not found", "command": self.command}
        return run_json_command([*command_invocation(self.command), "--help"], timeout=30)

    def observe(self, target: str = "Proteus", mode: str = "auto") -> dict[str, Any]:
        if not self.available():
            return {"ok": False, "error": "desktopctl not found", "command": self.command}
        template = os.environ.get("AGENT_PROTEUS_DESKTOPCTL_OBSERVE", "observe --json --target {target} --mode {mode}")
        args = template.format(target=target, mode=mode).split()
        return run_json_command([*command_invocation(self.command), *args], timeout=120)

    def click(self, x: int, y: int) -> dict[str, Any]:
        template = os.environ.get("AGENT_PROTEUS_DESKTOPCTL_CLICK", "click --json --x {x} --y {y}")
        args = template.format(x=x, y=y).split()
        return run_json_command([*command_invocation(self.command), *args], timeout=60)

    def type_text(self, text: str) -> dict[str, Any]:
        template = os.environ.get("AGENT_PROTEUS_DESKTOPCTL_TYPE", "type --json --text {text}")
        args = template.format(text=text).split()
        return run_json_command([*command_invocation(self.command), *args], timeout=60)
