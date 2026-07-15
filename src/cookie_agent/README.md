# Cookie Agent Core Package

This directory contains the main Python source code for the `cookie_agent` library.

---

## Package Overview

The core codebase follows the **Single Responsibility Principle**, separating capture logic, neural vision pipelines, game tracking, and action policies.

*   `version.py`: Single source of truth for package versioning.
*   `__init__.py`: Package entry point exposing metadata.

---

## Future Package Modules

In subsequent development phases, this folder will house the following submodules:

1.  **`capture/`**: Screenshot grabbers and low-latency frame buffer collectors.
2.  **`vision/`**: Deep learning object detectors, image preprocessing, and classification pipelines.
3.  **`state/`**: Continuous state tracking engine computing cookie trajectories and speed parameters.
4.  **`policy/`**: Policy algorithms (heuristics and RL models) predicting action bounds.
5.  **`controller/`**: Input interfaces generating tap, double-tap, or slide commands to target Android emulation.
6.  **`utils/`**: Shared helpers, logging, and configuration parsers.
