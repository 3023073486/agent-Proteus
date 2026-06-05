# Agent Harness: Proteus GUI-to-CLI

## Purpose

`agent-Proteus` is a small harness that lets coding agents operate Proteus 8
through stable CLI and MCP calls instead of fragile repeated mouse work.

It follows the CLI-Anything harness philosophy:

- Use the real software as the backend.
- Prefer native project files, deterministic scripts, and structured
  observation over ad-hoc GUI dragging.
- Emit stable JSON so agents can recover from errors.
- Verify real outputs and real windows, not only command exit codes.

## Backend Strategy

Proteus is the source of truth. This project does not reimplement schematic
simulation or rendering.

The current backend order is:

1. UI Automata HTTP service, when `UI_AUTOMATA_URL` is configured.
2. DesktopCtl, when `DESKTOPCTL` or `desktopctl` is available.
3. `proteus-bridge`, the required local fallback for launch, focus, keys,
   clicks, drags, screenshots, and JSON action scripts.

`agent-proteus observe` walks that order and returns every attempted backend in
JSON. This lets an agent understand whether it is seeing a rich UI tree,
vision/OCR-style state, or only window metadata.

## Command Contract

Every command should be safe for agents to call from any working directory:

```powershell
agent-proteus --json doctor
agent-proteus --json windows
agent-proteus --json observe --target Proteus
agent-proteus --json launch --project "C:\path\project.pdsprj" --no-wait
agent-proteus --json focus --title-match "Proteus|ISIS"
agent-proteus --json keys "{ESC}"
agent-proteus --json screenshot --out "C:\tmp\proteus.png"
agent-proteus --json run-script "C:\tmp\actions.json"
```

JSON policy:

- Success payloads include `ok: true` from the underlying backend when possible.
- Failures return `ok: false` and a plain `error` string.
- Backend subprocess results include `returncode`, `command`, and parsed
  `stdout` when JSON is available.
- Output must avoid credentials and must remain printable on Windows consoles
  that cannot encode all Unicode.

## Proteus Workflow

Use this order for schematic work:

1. `doctor` to check installed backends.
2. `windows` or `launch` to find/focus Proteus.
3. `observe` before high-risk UI actions.
4. File-level inspection or project-script changes for deterministic placement
   where possible.
5. `run-script` for repeatable coordinate batches.
6. `screenshot` only at decision points or for human review.

Avoid GUI drag loops for layout cleanup unless a current visual observation proves
the exact object and coordinate system. Prior Proteus dragging moved focus and
opened property dialogs unpredictably.

## Preview Direction

Proteus does not currently expose a cheap headless schematic renderer through
this harness. Until that exists, screenshots are honest but expensive visual
checkpoints.

A future `preview` command group should follow CLI-Anything preview norms:

- `preview capture` publishes an immutable bundle derived from real Proteus
  project state or a real Proteus export.
- `preview latest` is read-only and never renders.
- `preview live status --json` is a cheap state probe for agents.
- Generated preview artifacts must be truthful Proteus outputs, not synthetic
  diagrams pretending to be the schematic.

## Testing Policy

Tests should cover three layers:

- Unit tests for command construction and JSON-safe output.
- Subprocess tests for installed `agent-proteus` invocations.
- Real-backend checks on Windows where Proteus and `proteus-bridge` are
  installed.

Do not fake Proteus in tests that claim to verify Proteus behavior. If the real
backend is required and missing, the test or `doctor` output should say that
clearly.

## Safety Rules

- Do not save a Proteus project after broad GUI actions without visual
  verification.
- Do not rely on Chinese or non-ASCII paths for Proteus Program File properties.
- Do not silently fall back to fake rendering or fake schematic state.
- Do not run destructive filesystem operations as part of layout repair.
