# Tests Directory (`tests/`)

This directory houses the test suites for the Cookie Agent project, including unit tests, integration validation, and mock fixtures.

---

## Testing Guidelines

- **Framework**: Standardized on `pytest`.
- **Structure Mapping**: Mirror the layout of `src/cookie_agent/` file-for-file (e.g., tests for `src/cookie_agent/utils/config.py` belong in `tests/utils/test_config.py`).
- **No Side-Effects / Offline Only**: All tests must execute quickly and must not require an active Android emulator or physical device. Use mock libraries to stub external captures or inputs.
- **Naming Pattern**: All test files must be named `test_*.py` and test functions must begin with `test_*`.

---

## Run Verification Suite

To run all checks locally, run:

```bash
# Execute unit tests
pytest

# Execute tests with code coverage summary
pytest --cov=src
```
