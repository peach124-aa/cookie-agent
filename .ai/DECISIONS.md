# Decisions Log - Cookie Agent

This document records the architectural and design decisions made for the **Cookie Agent** project, tracking rationale, contexts, and statuses.

---

## ADR-0001: Python 3.12 Workspace & Layout Standard

### Status
**Approved**

### Context
We need to establish a robust, maintainable, and modern development ecosystem for the Python project.

### Decision
- **Python Version**: Standardize strictly on Python 3.12 to utilize advanced typing syntax, logging enhancements, and library stability.
- **Layout**: Use the standard `src/` layout layout style (`src/cookie_agent/`) to prevent import ambiguities and ensure cleaner unit testing.
- **Tooling**:
  - **Ruff**: For unified linting and formatting. Ruff is extremely fast and combines features of Flake8, Black, and isort.
  - **mypy**: Enforce strict static type checking to eliminate runtime type mismatches.
  - **pytest**: For testing.

### Consequences
- All developers (human and AI) must run tests and static checkers.
- Standard import structures must be used.

---

## ADR-0002: Monolithic Single-Game Focus

### Status
**Approved**

### Context
It is common for game AI projects to over-engineer dynamic adapters, abstraction layers, and plug-in systems to support generic games (e.g. multiple runner games). This adds massive overhead and code bloat.

### Decision
- Reject all plugin structures, generic adapters, and abstract game wrappers.
- All modules, detectors, trackers, and controllers are built with hardcoded assumptions specifically for **CookieRun Classic (쿠키런 for Kakao)**.

### Consequences
- Code remains simple, direct, and readable.
- Development cycle is faster since we don't support speculative generalization.

---

## ADR-0003: Configuration-Driven Design (Config-First)

### Status
**Approved**

### Context
Hardcoded values (coordinates, game speed constants, object thresholds) lead to logic brittleness.

### Decision
- No hardcoded magic values inside code.
- All values must be stored in files inside the `configs/` directory (JSON/YAML formats) and loaded dynamically.

### Consequences
- Tuning the agent's behavior does not require modifying code.
- Ensures distinct isolation of settings from logic.
