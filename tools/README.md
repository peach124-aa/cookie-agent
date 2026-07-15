# Developer Tools Directory (`tools/`)

This directory contains utility programs, interactive dashboards, and developer-facing command line interfaces (CLIs) used for diagnostic auditing.

---

## Tooling Standards

Unlike `scripts/` (which are short automation procedures), `tools/` contains complete developer utility apps.
- **Standards**: All tools must follow python coding guidelines (PEP 8, strict type hints, Google docstrings).
- **No Production Code Integration**: Core package modules (`src/cookie_agent/`) must never import files from `tools/`. The dependency direction is strictly: `tools` -> `src/cookie_agent`.

---

## Planned Utilities

1.  **`visualizer`**: A diagnostic dashboard tool overlaying detected obstacle bounding boxes onto live emulator streams to evaluate model prediction performance in real time.
2.  **`input_tester`**: A simple keyboard-override CLI tool enabling manual intervention to trigger inputs to check emulator controller response latency.
