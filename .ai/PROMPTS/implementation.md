# Prompt Template: Code Implementation

This prompt template should be used to guide AI agents during coding and implementation tasks within the Cookie Agent project.

---

## Prompt Template

```markdown
You are an expert Python developer tasked with implementing a feature for the Cookie Agent project.

### Objective
Implement: [Feature Name / Task Description]

### Reference Context
- Constitution: [CONSTITUTION.md](file:///c:/CKR-P1/.ai/CONSTITUTION.md)
- Project Context: [PROJECT_CONTEXT.md](file:///c:/CKR-P1/.ai/PROJECT_CONTEXT.md)
- Roadmap Phase: [ROADMAP.md](file:///c:/CKR-P1/.ai/ROADMAP.md)

### Strict Requirements
1. **Single-Game Focus**: The code must target ONLY CookieRun Classic. Do not create adapters, generic abstraction patterns, or plugin systems. Keep implementation direct and monolithic.
2. **Type Hints**: Ensure 100% of function arguments, class variables, and return types are annotated.
3. **Google Docstrings**: Write comprehensive docstrings in the Google Style guide.
4. **No Magic Numbers**: Move all parameters, thresholds, paths, or offsets into configurations under `configs/`.
5. **No TODOs / print()**: Use logging exclusively. Do not commit TODOs or print statements.
6. **Linting and Testing**: Run `ruff check`, `ruff format`, and `pytest` before finalizing.

### Action Plan
1. Research the existing files to locate relevant structures.
2. Formulate an implementation plan in markdown format.
3. Once the plan is approved, write clean, structured code.
4. Verify the changes using static type checking and unit tests.
```
