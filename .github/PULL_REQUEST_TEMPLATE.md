# Pull Request Template

## Summary
Provide a clear description of the proposed changes, the motivation behind them, and what problem they resolve.

---

## Architecture Impact
- **Single-Game Focus**: Confirm that this PR does not introduce general game interfaces or support for games other than CookieRun Classic.
- **Dependency Scope**: List any newly introduced packages or architecture adjustments.

---

## Testing
Describe the verification tests performed:
- [ ] Local tests executed (e.g. `pytest`)
- [ ] Linter checks (`ruff check .`, `ruff format --check .`)
- [ ] Strict type checking (`mypy src`)
- [ ] Coverage percentage achieved: ______% (80% minimum required)

Provide instructions on how reviewers can manually test or reproduce results.

---

## Checklist
- [ ] Code follows Python 3.12 syntax standards.
- [ ] Strict type annotations are present for all signatures and returns.
- [ ] Google docstrings are complete for all public modules, classes, and methods.
- [ ] No `print()` statements are included; logging is used.
- [ ] No `TODO` comments exist in the diff.
- [ ] All configuration parameters are moved out of the code into `configs/`.

---

## Reviewer Notes
Add any context, configuration instructions, or specific areas of the code you want reviewers to pay attention to.
