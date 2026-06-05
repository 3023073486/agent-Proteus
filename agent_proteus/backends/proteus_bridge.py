from __future__ import annotations

import base64
import os
import tempfile
from pathlib import Path
from typing import Any

from agent_proteus.process import command_invocation, run_json_command, which


class ProteusBridgeBackend:
    name = "proteus-bridge"

    def __init__(self, command: str | None = None) -> None:
        self.command = command or os.environ.get("PROTEUS_BRIDGE", "proteus-bridge")

    def available(self) -> bool:
        return bool(which(self.command) or Path(self.command).exists())

    def _run(self, args: list[str], timeout: int = 180) -> dict[str, Any]:
        return run_json_command([*command_invocation(self.command), *args, "--json"], timeout=timeout)

    def doctor(self) -> dict[str, Any]:
        return self._run(["doctor"])

    def windows(self) -> dict[str, Any]:
        return self._run(["windows"])

    def launch(self, project: str | None = None, wait: bool = True) -> dict[str, Any]:
        args = ["launch"]
        if project:
            args.extend(["--project", project])
        if wait:
            args.append("--wait")
        return self._run(args)

    def focus(self, title_match: str | None = None, handle: int | None = None) -> dict[str, Any]:
        args = ["focus"]
        if title_match:
            args.extend(["--title-match", title_match])
        if handle is not None:
            args.extend(["--handle", str(handle)])
        return self._run(args)

    def keys(self, value: str, title_match: str | None = None, handle: int | None = None) -> dict[str, Any]:
        args = ["keys", "--value", value]
        self._append_target(args, title_match, handle)
        return self._run(args)

    def click(
        self,
        x: int,
        y: int,
        button: str = "Left",
        relative: bool = False,
        double: bool = False,
        title_match: str | None = None,
        handle: int | None = None,
    ) -> dict[str, Any]:
        args = ["click", "--x", str(x), "--y", str(y), "--button", button]
        if relative:
            args.append("--relative")
        if double:
            args.append("--double")
        self._append_target(args, title_match, handle)
        return self._run(args)

    def drag(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        duration_ms: int = 450,
        relative: bool = False,
        title_match: str | None = None,
        handle: int | None = None,
    ) -> dict[str, Any]:
        args = [
            "drag",
            "--from-x",
            str(from_x),
            "--from-y",
            str(from_y),
            "--to-x",
            str(to_x),
            "--to-y",
            str(to_y),
            "--duration-ms",
            str(duration_ms),
        ]
        if relative:
            args.append("--relative")
        self._append_target(args, title_match, handle)
        return self._run(args)

    def screenshot(self, out: str | None = None, include_image: bool = False) -> dict[str, Any]:
        out_path = out or str(Path(tempfile.gettempdir()) / "agent-proteus-screenshot.png")
        result = self._run(["screenshot", "--out", out_path])
        result["path"] = out_path
        if include_image and Path(out_path).exists():
            result["image_base64"] = base64.b64encode(Path(out_path).read_bytes()).decode("ascii")
        return result

    def run_script(self, file: str) -> dict[str, Any]:
        return self._run(["run-script", "--file", file])

    @staticmethod
    def _append_target(args: list[str], title_match: str | None, handle: int | None) -> None:
        if title_match:
            args.extend(["--title-match", title_match])
        if handle is not None:
            args.extend(["--handle", str(handle)])
