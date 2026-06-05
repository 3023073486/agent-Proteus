# Workflow

## Preferred Loop

1. `agent_proteus_observe` to collect window or UI state.
2. Batch deterministic actions with `agent_proteus_run_script`, `agent_proteus_click`, `agent_proteus_drag`, or `agent_proteus_keys`.
3. Observe again only when the UI may have changed meaningfully.
4. Save the Proteus project only after the layout is verified.

## Backend Roles

- UI Automata: structured Windows UI state and element-centric operations.
- DesktopCtl: OCR/vision/token-based observation and generic desktop actions.
- proteus-bridge: Proteus-specific process, window, key, click, drag, screenshot, and script calls.

## Proteus Notes

- Proteus canvas work should prefer stable coordinates and scripts.
- Use terminals/labels for repeated net names such as `DQ1..DQ8`, `LCD_D4..LCD_D7`, `+5V`, and `GND`.
- Avoid direct binary editing of Proteus project internals unless the file format is fully understood.
