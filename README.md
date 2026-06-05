# agent-Proteus

Agent-friendly Proteus automation for Hermes, Codex, and other MCP hosts.

`agent-Proteus` combines three layers:

- **UI Automata** for structured Windows UI observation when available.
- **DesktopCtl** for local visual/OCR-style desktop observation and actions when available.
- **proteus-bridge** for deterministic Proteus 8 launch, focus, key, click, drag, screenshot, and JSON-script execution.

The project intentionally does not vendor UI Automata or DesktopCtl. It treats them as optional external backends so the integration stays small, legal, and easy to upgrade.

## Install

```powershell
git clone https://github.com/3023073486/agent-Proteus.git
cd agent-Proteus
python -m pip install -e .
agent-proteus --json doctor
```

The folder name does not matter. The examples use a plain ASCII directory so
new users do not inherit machine-specific Chinese paths.

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
    timeout: 180
    connect_timeout: 60
```

If `proteus-bridge` or `desktopctl` is not on `PATH`, add explicit paths:

```yaml
mcp_servers:
  agent_proteus:
    command: "python"
    args: ["-m", "agent_proteus", "mcp"]
    env:
      PROTEUS_BRIDGE: "C:/path/to/proteus-bridge.cmd"
      DESKTOPCTL: "C:/path/to/desktopctl.exe"
      # Optional if running a UI Automata HTTP service:
      # UI_AUTOMATA_URL: "http://127.0.0.1:7860"
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

## CLI-Anything Harness Notes

This project borrows the useful parts of the
[CLI-Anything](https://github.com/HKUDS/CLI-Anything) harness philosophy:

- Proteus remains the real backend; `agent-Proteus` is an interface to Proteus,
  not a schematic simulator.
- Commands are designed for stable `--json` agent use from any working
  directory.
- Observation is explicit and layered, so an agent knows whether it has UI tree,
  visual/OCR, or window-only state.
- Screenshots are checkpoint evidence, not the default loop.
- Future preview commands should publish truthful artifacts from real Proteus
  state, not fake renders.

See `HARNESS.md`, `SKILL.md`, and `tests/TEST.md` for the agent workflow and test
plan.

## Tests

```powershell
python -m pip install -e .
python -m pytest tests -v
```

Set `AGENT_PROTEUS_FORCE_INSTALLED=1` to require the installed
`agent-proteus` command instead of the development `python -m agent_proteus`
fallback.

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
