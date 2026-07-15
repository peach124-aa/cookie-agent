# Coding Standards (`docs/coding-standard/`)

This document outlines the strict coding guidelines, syntax rules, and style policies required for all developers and AI agents working on the Cookie Agent codebase.

---

## 1. Python Style & PEP 8
- **Python Version**: Strictly standardizes on **Python 3.12** features (pattern matching, union typing `A | B`, parenthesized context managers).
- **PEP 8 Compliance**: Enforced via `ruff`. 
- **Line Length**: Limited to a maximum of **88 characters** (matching the default Black/Ruff formatter config).

---

## 2. Type Hints
- **Rule**: Explicit type hints are **mandatory** for all function arguments, return values, variables, and class attributes.
- **Dynamic Types**: Avoid using `Any` wherever possible. If dynamic buffers require it, document the rationale in a docstring.
- **Static Analysis**: Mypy must pass with strict checks on all source directories.

---

## 3. Google Docstrings
All public modules, classes, methods, and functions must be documented using the **Google style guide**. 

Example:
```python
def compute_distance(origin: float, target: float) -> float:
    """Calculates the absolute distance between the cookie and an obstacle.

    Args:
        origin: The current X coordinate of the cookie.
        target: The front edge X coordinate of the obstacle.

    Returns:
        The absolute difference in X-axis coordinates.

    Raises:
        ValueError: If origin or target is negative.
    """
```

---

## 4. Logging
- **Rule**: Under no circumstances should `print()` statements be committed.
- **Usage**: Emits all output logs via the standard library's `logging` module.
- **Log Levels**: Use appropriate levels:
  - `DEBUG`: Fine-grained diagnostic events (e.g. frame grab durations, local variables).
  - `INFO`: Significant high-level events (e.g. ADB session started, model loaded).
  - `WARNING`: Recoverable anomalies (e.g. slow frame grab, socket timeout).
  - `ERROR`: Unrecoverable errors (e.g. emulator process died).

---

## 5. Naming Conventions
Follow standard PEP 8 naming structures:
- **Modules / Packages**: Lowercase snake_case (e.g., `cookie_agent`, `config_loader.py`).
- **Classes**: PascalCase (e.g., `DisplayCapture`, `ActionPlanner`).
- **Functions / Methods**: Lowercase snake_case (e.g., `start_capture()`, `send_input()`).
- **Variables**: Lowercase snake_case (e.g., `frame_count`, `last_touch_time`).
- **Constants**: UPPERCASE snake_case (e.g., `DEFAULT_PORT`, `MAX_RETRIES`).

---

## 6. Folder Rules & Separation of Concerns
- **Production Code**: Must reside strictly under `src/cookie_agent/`. Do not put logic code files directly in the root or directories like `docs/` or `tools/`.
- **Developer Scripts**: Standalone utilities go to `scripts/`.
- **Developer Tools**: UI visualizers or manual tools go to `tools/`.
- **Configurations**: Dynamic variables, thresholds, and coordinate setups must live in `configs/` JSON/YAML formats. No code configuration classes or hardcoded tables.
