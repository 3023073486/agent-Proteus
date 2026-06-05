---
name: agent-proteus
description: Use the local agent-Proteus CLI/MCP harness to operate Proteus 8 through stable JSON commands, optional UI Automata/DesktopCtl observation, and proteus-bridge fallback.
---

# agent-Proteus

Use this skill when a task involves Proteus 8 automation, Hermes/Codex MCP
integration for Proteus, schematic layout cleanup, component placement, wiring,
HEX loading, or deciding between observation backends and screenshots.

## First Checks

Verify the CLI is installed and inspect available backends:

```powershell
agent-proteus --json doctor
agent-proteus --json windows
```

If `proteus_bridge.available` is false, install or expose `proteus-bridge` first.
`UI_AUTOMATA_URL` and `DESKTOPCTL` are optional observation upgrades, not required
for basic Proteus control.

## Launch And Observe

Open or focus a project:

```powershell
agent-proteus --json launch --project "C:\ProteusLCD1602_8CH\LCD1602_8CH_TEMP.pdsprj" --no-wait
agent-proteus --json focus --title-match "Proteus|ISIS"
agent-proteus --json observe --target Proteus
```

Observation order is UI Automata, DesktopCtl, then proteus-bridge window
metadata. Read the returned `backend` and `attempts` fields before choosing the
next action.

## Safe Action Pattern

Prefer deterministic project-file or scripted changes before manual GUI
coordinates:

```powershell
agent-proteus --json run-script "C:\tmp\proteus-actions.json"
agent-proteus --json keys "{ESC}"
agent-proteus --json screenshot --out "C:\tmp\proteus-check.png"
```

Use screenshots sparingly: capture at checkpoints, after suspicious dialogs, or
when a human needs to verify layout. Do not screenshot after every click.

## Hermes MCP

Expose the MCP server with:

```yaml
mcp_servers:
  agent_proteus:
    command: "python"
    args: ["-m", "agent_proteus", "mcp"]
    timeout: 180
    connect_timeout: 60
```

Expected tools include `agent_proteus_doctor`, `agent_proteus_observe`,
`agent_proteus_windows`, `agent_proteus_focus`, `agent_proteus_launch`,
`agent_proteus_keys`, `agent_proteus_click`, `agent_proteus_drag`,
`agent_proteus_screenshot`, and `agent_proteus_run_script`.

## Proteus Layout Guidance

For messy schematics, first make the layout clean, then wire:

- Prefer coordinate-aware file/script placement when the project format is known.
- Avoid repeated GUI dragging unless current observation proves the selected part.
- Keep backups before project-file patching.
- Verify firmware pin expectations against schematic intent before wiring.
- Use ASCII paths for HEX files loaded into MCU properties.

## Do Not

- Do not save after broad GUI movement without visual confirmation.
- Do not treat generated diagrams as real Proteus schematic previews.
- Do not rely on stale dialog handles; Proteus recreates controls often.
- Do not use Chinese/non-ASCII paths for MCU `Program File` values.
