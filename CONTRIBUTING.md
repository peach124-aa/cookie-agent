# Contributing to Cookie Agent

Thank you for contributing to Cookie Agent. To maintain high code quality and architecture alignment, please adhere to the following workflow guidelines.

---

## 1. Project Philosophy
- **Strict Single-Game Focus**: The project is engineered solely for **CookieRun Classic (쿠키런 for Kakao)**. 
- **Direct Monolith**: No generic game adapters or multi-game plugin architectures.
- **Config-First**: Hardcoding logic parameters or thresholds is strictly forbidden. Move constants to `configs/`.

---

## 2. Development Lifecycle Flow

Every addition or change goes through the following pipeline:

```
Issue
  ↓
Design (RFC/ADR Plan)
  ↓
Technical Lead Review
  ↓
Implementation
  ↓
Code Review
  ↓
QA (Tests & Types)
  ↓
Merge
```

1.  **Issue**: Track features, modifications, or bugs as formal issues.
2.  **Design**: Draft an implementation plan (`implementation_plan.md`) describing file changes and test methodologies.
3.  **Technical Lead Review**: The Tech Lead reviews and approves the plan before any coding begins.
4.  **Implementation**: Write clean, PEP 8 and Python 3.12 compliant code inside `src/cookie_agent/`. Ensure strict type hinting, Google docstrings, and no raw `print` or `TODO` statements.
5.  **Code Review**: Peer review checking compliance against the Constitution and style guides using Ruff lint checks.
6.  **QA**: Execute local unit and integration tests using Pytest. Verify type correctness using Mypy.
7.  **Merge**: Once all review approvals are in, squash-merge the branch onto `main`.

---

## 3. Branch Naming Conventions
- **Feature Branches**: `feature/phase-<number>-<description>` (e.g. `feature/phase-1-display-capture`).
- **Bug Fix Branches**: `fix/phase-<number>-<description>` (e.g. `fix/phase-2-box-overlap`).
- **Docs/Maintenance**: `docs/phase-<number>-<description>` or `chore/phase-<number>-<description>`.

---

## 4. Commit Naming Conventions
Follow the phased commit scheme:
- Format: `Commit <XXXX>: <Brief Description>` (where `XXXX` is a sequential 4-digit number).
- Example: `Commit 0001: Bootstrap Pack v1.0`

---

## 5. Pull Request Expectations
Before a Pull Request is approved:
- Ruff formatting and linting checks must pass cleanly with no violations.
- Mypy static analysis must report zero typing issues.
- Pytest must complete successfully, and coverage thresholds must be satisfied.
- The change must contain no runtime logic unless explicitly authorized for that development phase.
