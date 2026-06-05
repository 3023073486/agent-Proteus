from __future__ import annotations

import argparse
import sys
from typing import Any

from agent_proteus import __version__
from agent_proteus.jsonio import print_json
from agent_proteus.orchestrator import AgentProteus


def add_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--title-match", help="Proteus window title regex.")
    parser.add_argument("--handle", type=int, help="Proteus window handle as integer.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-proteus",
        description="Agent-friendly Proteus automation CLI and MCP server.",
    )
    parser.add_argument("--version", action="version", version=f"agent-proteus {__version__}")
    parser.add_argument("--json", action="store_true", help="Emit stable JSON output. Human output is currently JSON too.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Check optional backends and Proteus bridge health.")
    subparsers.add_parser("windows", help="List Proteus-related windows.")

    observe = subparsers.add_parser("observe", help="Observe Proteus through UI Automata, DesktopCtl, then proteus-bridge.")
    observe.add_argument("--target", default="Proteus", help="Target app/window name.")
    observe.add_argument("--mode", default="auto", choices=["auto", "uia", "ocr", "vision", "windows"], help="Observation mode hint.")

    launch = subparsers.add_parser("launch", help="Launch Proteus, optionally with a project.")
    launch.add_argument("--project", help="Optional .pdsprj path.")
    launch.add_argument("--no-wait", action="store_true", help="Do not wait for a Proteus window.")

    focus = subparsers.add_parser("focus", help="Focus a Proteus window.")
    add_target_args(focus)

    keys = subparsers.add_parser("keys", help="Send keys to Proteus.")
    keys.add_argument("value", help="SendKeys-compatible value, for example '{ESC}'.")
    add_target_args(keys)

    click = subparsers.add_parser("click", help="Click Proteus coordinates.")
    click.add_argument("x", type=int)
    click.add_argument("y", type=int)
    click.add_argument("--button", default="Left", choices=["Left", "Right"])
    click.add_argument("--relative", action="store_true")
    click.add_argument("--double", action="store_true")
    add_target_args(click)

    drag = subparsers.add_parser("drag", help="Drag between Proteus coordinates.")
    drag.add_argument("from_x", type=int)
    drag.add_argument("from_y", type=int)
    drag.add_argument("to_x", type=int)
    drag.add_argument("to_y", type=int)
    drag.add_argument("--duration-ms", type=int, default=450)
    drag.add_argument("--relative", action="store_true")
    add_target_args(drag)

    screenshot = subparsers.add_parser("screenshot", help="Capture a Proteus/desktop screenshot through proteus-bridge.")
    screenshot.add_argument("--out", help="Output PNG path.")
    screenshot.add_argument("--include-image", action="store_true", help="Include base64 PNG in JSON output.")

    run_script = subparsers.add_parser("run-script", help="Run a proteus-bridge JSON action script.")
    run_script.add_argument("file", help="Script JSON path.")

    layout_audit = subparsers.add_parser("layout-audit", help="Audit a Proteus .pdsprj for component spacing and missing refs.")
    layout_audit.add_argument("--project", required=True, help="Proteus .pdsprj path.")
    layout_audit.add_argument("--require", action="append", default=[], help="Required reference designator, repeatable.")

    subparsers.add_parser("mcp", help="Run the stdio MCP server.")
    return parser


def run_command(args: argparse.Namespace) -> dict[str, Any]:
    agent = AgentProteus()
    if args.command == "doctor":
        return agent.doctor()
    if args.command == "windows":
        return agent.windows()
    if args.command == "observe":
        return agent.observe(target=args.target, mode=args.mode)
    if args.command == "launch":
        return agent.launch(project=args.project, wait=not args.no_wait)
    if args.command == "focus":
        return agent.focus(title_match=args.title_match, handle=args.handle)
    if args.command == "keys":
        return agent.keys(value=args.value, title_match=args.title_match, handle=args.handle)
    if args.command == "click":
        return agent.click(
            x=args.x,
            y=args.y,
            button=args.button,
            relative=args.relative,
            double=args.double,
            title_match=args.title_match,
            handle=args.handle,
        )
    if args.command == "drag":
        return agent.drag(
            from_x=args.from_x,
            from_y=args.from_y,
            to_x=args.to_x,
            to_y=args.to_y,
            duration_ms=args.duration_ms,
            relative=args.relative,
            title_match=args.title_match,
            handle=args.handle,
        )
    if args.command == "screenshot":
        return agent.screenshot(out=args.out, include_image=args.include_image)
    if args.command == "run-script":
        return agent.run_script(file=args.file)
    if args.command == "layout-audit":
        return agent.layout_audit(project=args.project, required_refs=args.require)
    raise ValueError(f"Unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "mcp":
        from agent_proteus.mcp_server import serve_stdio

        return serve_stdio()
    try:
        print_json(run_command(args))
        return 0
    except Exception as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
