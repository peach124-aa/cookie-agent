# ADR-0006: Configuration-First Architecture

## Status
- **Date**: 2026-07-16
- **Status**: Approved
- **Reviewer**: Tech Lead

---

## Context
In complex agent architectures (including computer vision pipelines, state tracking engines, and reinforcement learning controllers), developers and AI agents frequently introduce hardcoded magic numbers, local file system paths, and runtime constants. This creates severe coupling:
- Changing target capture resolutions, model paths, or input delays requires modifying logic files.
- Offline training scripts and online game loops cannot share settings reliably.
- Automation tools and continuous integration pipelines cannot dynamically override parameters (e.g. changing log levels or GPU device selections on the fly).

---

## Decision
We establish a strict **Configuration-First (Config-First)** architecture for the entire Cookie Agent system:
1.  **Zero Runtime Constants**: Hardcoding device paths, bounding box confidence thresholds, action delay ms, reward weights, or emulator serial numbers is strictly prohibited.
2.  **Unified Configuration Directory**: All configurations are stored under `configs/`, separated into version-controlled baseline files under `configs/defaults/` and git-ignored overrides under `configs/local/`.
3.  **Environment Variables Priority**: System environment variables prefixed with `COOKIE_AGENT_` override both default and local files at runtime.
4.  **Serialization Schema Validation**: All configs must declare a top-level `schema_version` tag to ensure structure migrations can occur programmatically.
5.  **List Merge Substitution (List Overwrite)**:
    When merging local configuration overrides or environment parameters with baseline configurations, lists are treated as atomic units. Lists do NOT merge item-by-item or concatenate; instead, the override list completely replaces the default list. This guarantees deterministic behavior and simplifies debugging.

---

## Rejected Alternatives
We evaluated several existing Python configuration libraries but rejected them in favor of a custom YAML-based loader:

- **Hydra & OmegaConf**:
  - *Why Rejected*: Hydra brings significant complexity, CLI pollution, and slow imports. It generates automatic build caches and directory artifacts that complicate replay reproducibility. We need simple, lightweight configurations that do not hijack terminal command-line arguments.
- **Dynaconf**:
  - *Why Rejected*: Dynaconf has a large footprint, automates massive amounts of magic loading behavior (which makes tracking where values came from difficult), and can behave non-deterministically based on environment settings.
- **Pydantic Settings**:
  - *Why Rejected*: Pydantic brings large dependencies and slow runtime overheads. Writing a pure python configuration loader using frozen dataclasses and native `ruamel.yaml` parser keeps our dependency tree clean, minimizes package bloat, guarantees fast startup times, and makes long-term maintenance straightforward.

---

## Consequences
- **Pros**:
  - **Environment Agnostic**: The exact same codebase runs seamlessly on local developer machines, headless CI runners, and high-performance training nodes.
  - **Fast Tuning**: Adjusting linter thresholds, reward weights, or planner variances requires zero code changes.
  - **Type Safety**: Enables parsing configurations into strict validated formats before execution loops initialize.
- **Cons**:
  - **Initialization Overhead**: Code must initialize a config manager and load values at startup.
  - **Complexity**: Requires documenting and updating templates for configuration schema definitions as features expand.
- **Next Steps**:
  - Developers must write parser loaders conforming to this ADR.
  - Verify that local files are ignored in `.gitignore`.
