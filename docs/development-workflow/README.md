# Development Workflow (`docs/development-workflow/`)

This document describes the structured development lifecycle and quality pipeline required for extending the Cookie Agent project.

---

## 1. Development Lifecycle Flow

```
Design
  ↓
Prompt
  ↓
Implementation
  ↓
Technical Review
  ↓
QA
  ↓
Merge
```

---

## 2. Phase Explanations

### Step 1: Design
- **Action**: Before modifying code, draft an implementation plan outlining file changes, testing steps, and architectural impacts.
- **Artifacts**: Save design specs under `docs/rfc/` or `docs/adr/`.
- **Sign-off**: Requires approval from the Technical Lead.

### Step 2: Prompt
- **Action**: Use the prompt templates located in `.ai/PROMPTS/` to initialize feature tasks for AI developer agents, ensuring rules and boundaries are injected at execution time.

### Step 3: Implementation
- **Action**: Develop the code inside `src/cookie_agent/` according to standard coding rules (PEP 8, type hints, Google docstrings, config-first, logging).
- **Constraints**: No placeholder code or TODO blocks are allowed to remain.

### Step 4: Technical Review
- **Action**: Audit changes using the Code Reviewer persona guidelines to catch scope creep, magic numbers, or code styling mismatches.
- **Command Gate**: Ruff linter checks must pass cleanly.

### Step 5: QA
- **Action**: QA Engineer audits tests, mocks, and runs the test suite.
- **Command Gate**: All unit tests must pass successfully, and CI checks must be green.

### Step 6: Merge
- **Action**: Merge the approved feature branch onto `main` and tag the commit milestone.
