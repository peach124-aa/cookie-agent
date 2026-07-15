# AI Constitution - Cookie Agent

This document defines the core principles, coding rules, and constraints governing all automated AI agents developing, reviewing, or testing the **Cookie Agent** project.

---

## 1. Scope and Domain Focus

### Exclusive Targeting
This project is built for **one game and one game only**:
**CookieRun Classic (쿠키런 for Kakao)**.

### Strict Anti-Patterns
- **NO Plugin Architectures**: Do not build modular plugin layers, dynamic class loaders, or runtime register hooks for external extensions.
- **NO Generic Game Adapters**: Do not create general game state abstractions or interfaces designed to support other run-and-jump games. Keep the code tightly coupled to the exact physics, timings, and UI layouts of CookieRun Classic.
- **NO Future-Proofing for Multi-Game Support**: Design all structures, inputs, and database schemas with the assumption that this agent will never run on another game.

---

## 2. Core Development Rules

### Python 3.12 Standard
- Use modern Python 3.12 syntax.
- Utilize generic types, pattern matching, union operator (`|`), and advanced logging where appropriate.

### Static Typing
- All functions, variables, parameters, and class attributes must contain **explicit type hints**.
- Do not use `Any` unless completely unavoidable (e.g., dynamic external buffers) and documented with reasons.
- Ensure mypy type checks pass with strict flags.

### Google-Style Docstrings
- All modules, classes, and public functions must have standard Google format docstrings.
- Docstrings must specify Argument names, types, description, return types, and exceptions raised.

### Configuration-Driven Architecture
- No hardcoded magic values, offsets, coordinates, timings, threshold weights, or API configurations.
- All dynamic data must be declared in configurations inside the `configs/` directory.

### Single Responsibility Principle
- Write modular, testable files.
- Ensure each class or function has a single reason to change.

### Zero-Tolerance Rules
- **No `print()` statements**: All outputs must be emitted via standard python loggers.
- **No `TODO` comments**: Resolve all tasks, gaps, and structural issues before pushing or completing a step.
- **No placeholder functions or classes**: Never leave mock structures, draft functions, or dummy code blocks.

---

## 3. Collaboration and Quality Assurance

- Always run verification tools (`ruff check`, `ruff format`, `mypy`, `pytest`) before declaring any task complete.
- When performing reviews or audits, prioritize reliability, execution latency, and conformity to these constitution standards.
