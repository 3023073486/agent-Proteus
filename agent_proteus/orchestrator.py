from __future__ import annotations

from typing import Any

from agent_proteus.backends import DesktopCtlBackend, ProteusBridgeBackend, UiAutomataBackend
from agent_proteus.layout_audit import audit_project


class AgentProteus:
    def __init__(self) -> None:
        self.ui_automata = UiAutomataBackend()
        self.desktopctl = DesktopCtlBackend()
        self.proteus = ProteusBridgeBackend()

    def doctor(self) -> dict[str, Any]:
        return {
            "ok": True,
            "backends": {
                "ui_automata": {
                    "available": self.ui_automata.available(),
                    "doctor": self.ui_automata.doctor(),
                },
                "desktopctl": {
                    "available": self.desktopctl.available(),
                    "doctor": self.desktopctl.doctor() if self.desktopctl.available() else {"ok": False, "error": "not found"},
                },
                "proteus_bridge": {
                    "available": self.proteus.available(),
                    "doctor": self.proteus.doctor() if self.proteus.available() else {"ok": False, "error": "not found"},
                },
            },
        }

    def windows(self) -> dict[str, Any]:
        return self.proteus.windows()

    def observe(self, target: str = "Proteus", mode: str = "auto") -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        if self.ui_automata.available():
            result = self.ui_automata.observe(target=target, mode=mode)
            attempts.append({"backend": self.ui_automata.name, "result": result})
            if result.get("ok"):
                return {"ok": True, "backend": self.ui_automata.name, "result": result, "attempts": attempts}

        if self.desktopctl.available():
            result = self.desktopctl.observe(target=target, mode=mode)
            attempts.append({"backend": self.desktopctl.name, "result": result})
            if result.get("ok"):
                return {"ok": True, "backend": self.desktopctl.name, "result": result, "attempts": attempts}

        result = self.proteus.windows()
        attempts.append({"backend": self.proteus.name, "result": result})
        return {"ok": result.get("ok", False), "backend": self.proteus.name, "result": result, "attempts": attempts}

    def focus(self, title_match: str | None = None, handle: int | None = None) -> dict[str, Any]:
        return self.proteus.focus(title_match=title_match, handle=handle)

    def launch(self, project: str | None = None, wait: bool = True) -> dict[str, Any]:
        return self.proteus.launch(project=project, wait=wait)

    def keys(self, value: str, title_match: str | None = None, handle: int | None = None) -> dict[str, Any]:
        return self.proteus.keys(value=value, title_match=title_match, handle=handle)

    def click(self, x: int, y: int, **kwargs: Any) -> dict[str, Any]:
        return self.proteus.click(x=x, y=y, **kwargs)

    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int, **kwargs: Any) -> dict[str, Any]:
        return self.proteus.drag(from_x=from_x, from_y=from_y, to_x=to_x, to_y=to_y, **kwargs)

    def screenshot(self, out: str | None = None, include_image: bool = False) -> dict[str, Any]:
        return self.proteus.screenshot(out=out, include_image=include_image)

    def run_script(self, file: str) -> dict[str, Any]:
        return self.proteus.run_script(file=file)

    def layout_audit(self, project: str, required_refs: list[str] | None = None) -> dict[str, Any]:
        return audit_project(project, required_refs=required_refs)
