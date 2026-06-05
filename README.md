# agent-Proteus

Agent-friendly Proteus automation for Hermes, Codex, and other MCP hosts.

`agent-Proteus` combines three layers:

- **UI Automata** for structured Windows UI observation when available.
- **DesktopCtl** for local visual/OCR-style desktop observation and actions when available.
- **proteus-bridge** for deterministic Proteus 8 launch, focus, key, click, drag, screenshot, and JSON-script execution.

The project intentionally does not vendor UI Automata or DesktopCtl. It treats them as optional external backends so the integration stays small, legal, and easy to upgrade.

## Install

```powershell
cd D:\克里斯蒂娜\repos\agent-Proteus
python -m pip install -e .
agent-proteus --json doctor
```

## Hermes MCP Config

Add this to Hermes `config.yaml`:

```yaml
mcp_servers:
  agent_proteus:
    command: "python"
    args:
      - "-m"
      - "agent_proteus"
      - "mcp"
    env:
      PROTEUS_BRIDGE: "D:/nodejs/proteus-bridge.cmd"
      # Optional if running a UI Automata HTTP service:
      # UI_AUTOMATA_URL: "http://127.0.0.1:7860"
      # Optional if desktopctl is not on PATH:
      # DESKTOPCTL: "C:/path/to/desktopctl.exe"
    timeout: 180
    connect_timeout: 60
```

After Hermes starts, it should discover tools named like:

- `agent_proteus_doctor`
- `agent_proteus_observe`
- `agent_proteus_windows`
- `agent_proteus_focus`
- `agent_proteus_click`
- `agent_proteus_drag`
- `agent_proteus_run_script`

## CLI

```powershell
agent-proteus --json doctor
agent-proteus --json windows
agent-proteus --json observe --target Proteus
agent-proteus --json focus --title-match "Proteus|ISIS"
agent-proteus --json keys "{ESC}"
agent-proteus --json click 500 420 --relative --title-match "Proteus"
agent-proteus --json drag 400 300 700 300 --relative --duration-ms 450
```

## Observation Strategy

`agent-proteus observe` tries backends in this order:

1. `UI_AUTOMATA_URL`, if configured.
2. `desktopctl`, if available on PATH or via `DESKTOPCTL`.
3. `proteus-bridge windows` fallback.

This makes Proteus work today with `proteus-bridge`, while allowing richer live-ish observation when UI Automata or DesktopCtl are installed.

## Safety Notes

- Prefer `agent-proteus run-script` for repeatable coordinate batches.
- Do not save Proteus projects until the layout is visually verified.
- Prefer labels/terminals and deterministic placement over long guessed wires.
- Use observation after UI-changing actions, not after every single click.

## Related Projects

- UI Automata: https://automata.visioncortex.org/
- DesktopCtl: https://desktopctl.com/
- Hermes Agent: https://github.com/NousResearch/hermes-agent

## License

MIT
