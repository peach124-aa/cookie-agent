# Lessons Learned - Cookie Agent

This document is a living log for recording lessons learned, performance discoveries, and troubleshooting tips during the development of Cookie Agent.

---

## 1. How to Use this Log
Agents and developers should update this file whenever:
- A significant bug or performance bottleneck is solved.
- An assumption about the game physics, emulator latency, or ML model behavior is corrected.
- A workflow process is streamlined.

---

## 2. Phase 0 - Project Bootstrap Findings
- **Layout selection**: Using the `src/` layout prevents common namespace collisions where tests accidentally import from local workspace paths instead of the installed editable package.
- **Ruff integration**: Consolidating isort, black, and flake8 configurations into Ruff simplifies linter configuration setup.
