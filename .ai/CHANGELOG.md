# Changelog - Cookie Agent

All reviewed and approved milestone commits for this repository are logged here.

---

## Commit 0001
- **Title**: Bootstrap Pack v1.0
- **Status**: Approved with Minor Changes
- **Description**: Initial project skeleton, packages metadata configurations, AI rules, and directory documentation skeletons.

---

## Commit 0002
- **Title**: Development Foundation
- **Status**: Approved
- **Description**: Configured pre-commit linter checks, set up pytest-cov with an 80% coverage check threshold, implemented strict typing with mypy, and added Pull Request, Issue, and design RFC/ADR templates.

---

## Commit 0003
- **Title**: Core Interfaces Specification
- **Status**: Approved (Design Only)
- **Description**: Wrote the Software Design Specification (SDS) for all core models (Frame, BBox, TrackedObject, GameState, ActionIntent, etc.) and component protocols (CaptureSource, Detector, Policy, ActionPlanner, etc.).

---

## Commit 0003.5
- **Title**: Configuration Schema & ADR
- **Status**: Approved (Design Only)
- **Description**: Wrote the Configuration Schema Specification detailing YAML parameter schemas and created ADR-0006 establishing the Configuration-First architecture policy.

---

## Commit 0004
- **Title**: Core Interfaces Package
- **Status**: Approved
- **Description**: Created the `cookie_agent.core` Python package containing all frozen, slot-allocated dataclass models (Frame, BBox, Detection, GameState, PlayerState, etc.), string enums (JumpPhase, IntentType, etc.), and PEP 544 protocols (CaptureSource, Detector, Policy, etc.). Wrote full unit test coverage.

---

## Commit 0005
- **Title**: Configuration Loader
- **Status**: Approved with Improvements
- **Description**: Implemented the modular configuration loader with the following features:
  - **ConfigName Enumeration**: StrEnum detailing config target identifiers (`APP`, `DEVICE`, etc.).
  - **Centralized Path Resolution**: Integrated `get_config_file()` and `config_exists()` checking file locations.
  - **Immutable Merges**: Replaced merge routines with deep copied structures to protect underlying inputs, establishing atomic list overwriting.
  - **Decoupled Schema Versioning**: Introduced the `CONFIG_SCHEMA_VERSION` constant, separating version checks to occur before deep merging.
  - **Environment Variables Overrides**: Supports missing intermediate path constructions (nested dictionaries), casting case-insensitive boolean states (`true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off`), and raising validation failures on malformed fields.
  - **Unknown Key Validation**: Added recursive check raising errors on foreign fields in loaded YAML sources.
  - **Lightweight Dry Loading**: Cleaned up duplicated file parse checks and removed caching to remain stateless.
