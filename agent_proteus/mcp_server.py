from __future__ import annotations

import json
import sys
from typing import Any

from agent_proteus import __version__
from agent_proteus.orchestrator import AgentProteus


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


TOOLS: list[dict[str, Any]] = [
    {"name": "agent_proteus_doctor", "description": "Check UI Automata, DesktopCtl, and proteus-bridge backend health.", "inputSchema": schema({})},
    {"name": "agent_proteus_windows", "description": "List Proteus-related windows through proteus-bridge.", "inputSchema": schema({})},
    {
        "name": "agent_proteus_observe",
        "description": "Observe Proteus through UI Automata, DesktopCtl, then proteus-bridge fallback.",
        "inputSchema": schema(
            {
                "target": {"type": "string", "default": "Proteus"},
                "mode": {"type": "string", "default": "auto", "enum": ["auto", "uia", "ocr", "vision", "windows"]},
            }
        ),
    },
    {
        "name": "agent_proteus_launch",
        "description": "Launch Proteus, optionally opening a project.",
        "inputSchema": schema({"project": {"type": "string"}, "wait": {"type": "boolean", "default": True}}),
    },
    {
        "name": "agent_proteus_focus",
        "description": "Focus Proteus by title regex or handle.",
        "inputSchema": schema({"title_match": {"type": "string"}, "handle": {"type": "integer"}}),
    },
    {
        "name": "agent_proteus_keys",
        "description": "Send keys to Proteus.",
        "inputSchema": schema({"value": {"type": "string"}, "title_match": {"type": "string"}, "handle": {"type": "integer"}}, ["value"]),
    },
    {
        "name": "agent_proteus_click",
        "description": "Click at Proteus coordinates.",
        "inputSchema": schema(
            {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "button": {"type": "string", "default": "Left", "enum": ["Left", "Right"]},
                "relative": {"type": "boolean", "default": False},
                "double": {"type": "boolean", "default": False},
                "title_match": {"type": "string"},
                "handle": {"type": "integer"},
            },
            ["x", "y"],
        ),
    },
    {
        "name": "agent_proteus_drag",
        "description": "Drag between Proteus coordinates.",
        "inputSchema": schema(
            {
                "from_x": {"type": "integer"},
                "from_y": {"type": "integer"},
                "to_x": {"type": "integer"},
                "to_y": {"type": "integer"},
                "duration_ms": {"type": "integer", "default": 450},
                "relative": {"type": "boolean", "default": False},
                "title_match": {"type": "string"},
                "handle": {"type": "integer"},
            },
            ["from_x", "from_y", "to_x", "to_y"],
        ),
    },
    {
        "name": "agent_proteus_screenshot",
        "description": "Capture a screenshot through proteus-bridge.",
        "inputSchema": schema({"out": {"type": "string"}, "include_image": {"type": "boolean", "default": False}}),
    },
    {
        "name": "agent_proteus_run_script",
        "description": "Run a proteus-bridge JSON action script.",
        "inputSchema": schema({"file": {"type": "string"}}, ["file"]),
    },
    {
        "name": "agent_proteus_layout_audit",
        "description": "Audit a Proteus .pdsprj for component spacing, overlap risk, and missing reference designators.",
        "inputSchema": schema(
            {
                "project": {"type": "string"},
                "required_refs": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            ["project"],
        ),
    },
]


def write_response(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def text_result(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}]}


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    arguments = arguments or {}
    agent = AgentProteus()
    if name == "agent_proteus_doctor":
        return text_result(agent.doctor())
    if name == "agent_proteus_windows":
        return text_result(agent.windows())
    if name == "agent_proteus_observe":
        return text_result(agent.observe(target=arguments.get("target", "Proteus"), mode=arguments.get("mode", "auto")))
    if name == "agent_proteus_launch":
        return text_result(agent.launch(project=arguments.get("project"), wait=arguments.get("wait", True)))
    if name == "agent_proteus_focus":
        return text_result(agent.focus(title_match=arguments.get("title_match"), handle=arguments.get("handle")))
    if name == "agent_proteus_keys":
        return text_result(agent.keys(value=arguments["value"], title_match=arguments.get("title_match"), handle=arguments.get("handle")))
    if name == "agent_proteus_click":
        return text_result(agent.click(**arguments))
    if name == "agent_proteus_drag":
        return text_result(agent.drag(**arguments))
    if name == "agent_proteus_screenshot":
        return text_result(agent.screenshot(out=arguments.get("out"), include_image=arguments.get("include_image", False)))
    if name == "agent_proteus_run_script":
        return text_result(agent.run_script(file=arguments["file"]))
    if name == "agent_proteus_layout_audit":
        return text_result(agent.layout_audit(project=arguments["project"], required_refs=arguments.get("required_refs") or []))
    raise ValueError(f"Unknown tool: {name}")


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "agent-Proteus", "version": __version__},
                "instructions": "Use UI Automata and DesktopCtl for observation when configured; use proteus-bridge for deterministic Proteus actions.",
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        try:
            return {"jsonrpc": "2.0", "id": request_id, "result": call_tool(str(params.get("name")), params.get("arguments") or {})}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}}
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


def serve_stdio() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            response = handle_request(json.loads(line))
        except Exception as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if response is not None:
            write_response(response)
    return 0
