# Changelog - Cookie Agent

All reviewed and approved milestone commits for this repository are logged here.

---

## Commit 0019
- **Title**: Configuration System
- **Status**: Ready
- **Description**: Reconstructed the system architecture to a decentralized, domain-driven configuration model using the Python Standard Library.
  - **Structure Improvements**: Abolished the legacy monolithic structures and `yaml` parsers, converting to `JSON` compatibility integrated natively across decoupled modules (`capture.py`, `detector.py`, etc.).
  - **Immutable Serialization**: Programmed an advanced abstraction inside `serializer.py` operating generically with Python types allowing `BaseConfig` to execute dictionary recursive unwrapping universally across the project.
  - **Validation Security**: Hardened class attributes with `__post_init__` using the newly developed `validator.py` suite.

---

## Commit 0018
- **Title**: Action Planner
- **Status**: Ready
- **Description**: Implemented the `ActionPlanner` protocol to securely translate abstract intents into low-level `ADBCommand` sequences without side effects.
  - **Core Modifications**: Expanded `IntentType` enum in `actions.py` to support `IDLE`, `DOUBLE_JUMP`, and `DASH`.
  - **Planner Engine**: Implemented `CookieActionPlanner` which sequentially routes deterministic `ActionIntent` to exact coordinates defined in pure Python.
  - **Mapping & Builder**: Configured pure-python `mapping.py` static coordinates, coupled with atomic atomic command sequence constructors (`tap`, `swipe`, `hold`, `release`) in `builder.py`.
  - **Isolation Verification**: Strictly respects isolation boundaries. Executes no subprocesses, doesn't construct `ADBClient`, handles no networking, imports zero environmental or ML libraries.
  - **Test Suite**: Developed rigorous matrix tests mapping all `IntentType` enumerations to exact output list boundaries, including exception bridging for invalid routing payloads.

---

## Commit 0017
- **Title**: Policy Module
- **Status**: Ready
- **Description**: Implemented the decision-making Policy boundary layer.
  - **RulePolicy**: Designed a deterministic, stateless heuristic baseline policy that evaluates `GameState` properties.
  - **PPOPolicy**: Created an adapter implementing the `Policy` protocol while delegating inferences to an injected generic `PPOAgentProtocol`, guaranteeing complete decoupling from ML environments (Torch/NumPy).
  - **PolicySelector**: Constructed a dependency-injection based dynamic router to seamlessly swap active policies without singletons.
  - **Dependencies**: Fully adheres to architectural isolation. Consumes `GameState` to produce `ActionIntent` without any reverse dependencies on Execution (Device, Capture, Planner).
  - **Tests**: Verified protocol conformance, heuristic logic trees, exception handling wrapper behavior, and DI stability.

---

## Commit 0016
- **Title**: PPO Trainer
- **Status**: Ready
- **Description**: Implemented the pure Python Orchestration loop for the PPO agent:
  - **Protocols**: Declared strict dependency inversion abstractions for `AgentProtocol`, `OptimizerProtocol`, `SchedulerProtocol`, `CheckpointProtocol`, and `CallbackProtocol`.
  - **PPOTrainer**: Synchronizes the sequential process of buffer collection, GAE calculation via `PPOAlgorithm`, and minibatch gradient backpropagation.
  - **Metrics**: Standardized strongly-typed `EpochMetrics` and `TrainMetrics` dataclasses instead of primitive tuples or dictionaries.
  - **Dependencies**: Retains zero external coupling to Gym environments, deep learning engines, or Cookie Run logic, acting only as the mathematical sequencer.
  - **Tests**: Validated loop choreography, exact callback lifecycle sequences, and metric reporting structures.

---

## Commit 0015
- **Title**: PPO Algorithm
- **Status**: Ready
- **Description**: Implemented the core mathematical routines for Proximal Policy Optimization:
  - **Returns & GAE**: `compute_discounted_returns` and `compute_gae` for robust baseline variance reduction.
  - **Surrogate Objectives**: Clipped policy loss, Mean Squared Error value loss, and entropy bonus regularization.
  - **Orchestration**: Created a strict `PPOAlgorithm` coordinator that routes sequential generic math without coupling to a trainer, optimizer, or deep learning backend.
  - **Dependencies**: No PPO frameworks, PyTorch, NumPy, or neural network logic. Strict Pure Python operations applied over `list[float]`.
  - **Tests**: Comprehensive unit tests covering GAE bounds, surrogate loss clipping bounds, and scalar sequence validation.

---

## Commit 0014
- **Title**: RL Experience Buffer
- **Status**: Ready
- **Description**: Implemented the generic Reinforcement Learning experience module:
  - **Generics-driven Architecture**: Pure Python `Experience`, `Trajectory`, and `RolloutBuffer` containers typed cleanly via `TypeVar` to fully decouple RL logic from Cookie Run abstractions.
  - **Determinism**: Introduced deterministic, chronological `MiniBatchSampler`.
  - **Memory Safety**: `Experience` arrays are strict slot-based, frozen dataclasses optimizing buffer scale overhead natively in Python.
  - **Dependencies**: No PPO, PyTorch, NumPy, or serialization coupling. Strict Pure Python implementation.
  - **Tests**: Comprehensive unit tests covering generic typing immutability, batch slicing, episode splitting, and reward aggregation.

---

## Commit 0013
- **Title**: Environment
- **Status**: Ready
- **Description**: Implemented the Environment Module for core orchestration:
  - **CookieEnvironment**: Ties Capture, Detector, Tracker, State Builder, Reward Strategy, Device Controller, and Action Planner pipelines together into `reset()` and `step()` methods.
  - **Dependencies**: No PPO, RL Environment framework, or Cookie Run game logic introduced. Strict Pure Python implementation.
  - **Cleanup**: Implements robust `close()` mechanism spanning all submodules via safe protocol probing.
  - **Tests**: Comprehensive mock testing across orchestration flows ensuring pipeline sequence is respected.

---

## Commit 0012
- **Title**: Reward Engine
- **Status**: Ready
- **Description**: Implemented the Reward Engine Module in pure Python:
  - **RewardEngine**: Conforms to the `RewardStrategy` Protocol.
  - **RewardRule**: Extensible rule protocol allowing decoupled injection of domain-specific logic.
  - **Event Aggregation**: Evaluates state transitions across all registered rules and deterministically combines emitted `RewardEvent` objects.
  - **Dependencies**: No game logic, no RL environment logic, and zero external numerical dependencies.
  - **Tests**: Exhaustive test coverage (over 92% project-wide) for positive, negative, and aggregation reward logic.

---

## Commit 0011
- **Title**: State Builder
- **Status**: Ready
- **Description**: Implemented the State Builder Module in pure Python:
  - **DefaultStateBuilder**: Conforms to the `StateBuilder` Protocol.
  - **Unified GameState**: Combines tracked objects, OCR results, and character status into a single `GameState`.
  - **Heuristics**: Derives `JumpPhase`, `airborne`, `grounded`, `scroll_speed`, and `scroll_distance` organically from velocity outputs and previous states if missing from metadata.
  - **Tests**: Comprehensive unit testing ensuring transition state logic handles temporal features cleanly.

---

## Commit 0010
- **Title**: Tracker Module
- **Status**: Ready
- **Description**: Implemented the Tracker Module in pure Python:
  - **ObjectTracker**: Conforms to the `Tracker` Protocol.
  - **Assignment Strategy**: Greedy assignment algorithm using Euclidean distance.
  - **LifecycleManager**: Filters and transitions `TrackedObject` states through `ACTIVE`, `OCCLUDED`, `CONSUMED`, and `LOST`.
  - **Velocity Calculation**: Derived velocity vectors natively based on timestamp deltas between consecutive frames.
  - **Tests**: Comprehensive unit tests covering state transitions and protocols without introducing dependencies like `scipy`.

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

---

## Commit 0006
- **Title**: Capture Module
- **Status**: Approved
- **Description**: Implemented the low-latency graphical frame buffer capture module:
  - **Base Capture Source Interface**: Created an abstract class conforming to the runtime checkable `CaptureSource` protocol.
  - **WindowsCapture**: Implemented GDI-based screen capture retrieving raw emulator graphics buffers in BGRA format directly without color conversion or external package dependencies (such as numpy, OpenCV, or torch).
  - **Bounded FrameBuffer**: Implemented a thread-safe FIFO queue dropping the oldest frame on capacity overflow.
  - **Unit Testing**: 100% test coverage using platform-independent mock layers for Windows GDI and handle APIs.

---

## Commit 0007
- **Title**: ADB Device Controller
- **Status**: Approved
- **Description**: Implemented the Android Device Controller:
  - **ADBClient**: Subprocess-based thin wrapper around `adb` CLI supporting push, pull, shell, connect, and health check.
  - **Commands Builders**: Declared immutable builders returning tuple argument parameters mapping taps, swipes, and key events.
  - **Output Parsers**: Parsers extracting resolution bounds (`wm size`), device lists, and window focus configurations without code duplicate regex.
  - **ADBDeviceController**: High-level execution client implementing `DeviceController` protocol.
  - **Unit Testing**: Complete unit test mapping client retries, error validations, parser flows, and execution commands.

---

## Commit 0008
- **Title**: Replay Recorder
- **Status**: Approved
- **Description**: Implemented a replay recording subsystem:
  - **Custom Binary Format**: Designed a lightweight, chunked binary file layout utilizing magic bytes and version verification checks.
  - **ReplayWriter**: Losslessly serializes session headers, frames, and command lists.
  - **ReplayReader**: Lazily deserializes files back into immutable Frame structures.
  - **ReplayRecorder**: Concrete implementation conforming to the `ReplayObserver` protocol.
  - **Unit Testing**: Asserts write/read cycles, corrupt streams handling, formatting errors, and conformance validation.

---

## Commit 0009
- **Title**: Detector Module
- **Status**: Approved
- **Description**: Implemented the object detection predictor subsystem:
  - **Mock YOLO Inference Backend**: Inference protocol and mock loaders running predictions without PyTorch/GPU.
  - **Pure NumPy Preprocessor**: Converts raw image frames, normalizes color coordinates, and scales resolutions.
  - **NMS Postprocessor**: Computes box overlaps (IoU), suppresses overlaps, scales boxes back to original bounds, and filters scores.
  - **Predictor**: Integrates loops conforming to the `Detector` contract.
  - **Unit Testing**: Asserts nearest-neighbor scaling, mock prediction loads, and protocol checks.
