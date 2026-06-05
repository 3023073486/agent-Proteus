# agent-Proteus Test Plan

## Inventory

- `test_cli.py`: subprocess and parser-level CLI smoke tests.
- Future `test_backends.py`: backend command construction and fallback behavior.
- Future `test_real_proteus.py`: Windows-only real Proteus and proteus-bridge E2E.

## Unit And Subprocess Plan

`test_cli.py` covers:

- `agent-proteus --help` exits successfully and lists core commands.
- `agent-proteus --json doctor` returns parseable JSON with backend sections.
- `agent-proteus --json windows` returns parseable JSON or a clear backend error.
- Installed command resolution falls back to `python -m agent_proteus` in dev.

Expected count: 3 tests.

## Real Backend Plan

Future real-backend tests should run only on the Windows Proteus machine and
should verify:

- `proteus-bridge doctor --json` succeeds.
- Launching a known `.pdsprj` creates or focuses a real Proteus window.
- Screenshot output exists, is PNG, and has non-zero size.
- A harmless `keys "{ESC}"` action succeeds against the focused window.

These tests should not fake Proteus. If the backend is missing, the failure
should clearly point to missing Proteus or `proteus-bridge` setup.

## Current Results

Local run on Windows:

```text
platform win32 -- Python 3.14.5, pytest-9.0.3
collected 3 items

tests/test_cli.py::test_help_lists_core_commands PASSED
tests/test_cli.py::test_doctor_json_has_backend_sections PASSED
tests/test_cli.py::test_windows_json_is_machine_readable PASSED

3 passed in 1.65s
```
