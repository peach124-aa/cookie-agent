"""Core inference pipeline orchestrator."""

import time
from collections.abc import Sequence
from dataclasses import dataclass

from cookie_agent.core.actions import ADBCommand
from cookie_agent.core.protocols import (
    ActionPlanner,
    CaptureSource,
    Detector,
    DeviceController,
    Policy,
    StateBuilder,
    Tracker,
)
from cookie_agent.core.state import GameState
from cookie_agent.runner.exceptions import PipelineError
from cookie_agent.runner.metrics import StepMetrics


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """Structured result of a single inference pipeline execution."""

    metrics: StepMetrics
    state: GameState
    commands: Sequence[ADBCommand]


class InferenceRunner:
    """Orchestrates the execution of the agent pipeline."""

    def __init__(
        self,
        capture_source: CaptureSource,
        detector: Detector,
        tracker: Tracker,
        state_builder: StateBuilder,
        policy: Policy,
        planner: ActionPlanner,
        device_controller: DeviceController,
    ) -> None:
        """Initialize the InferenceRunner with its dependencies.

        Args:
            capture_source: Source for capturing frames.
            detector: Model for object detection.
            tracker: Multi-object tracker.
            state_builder: Constructs the unified GameState.
            policy: Action selection strategy.
            planner: Converts abstract actions to concrete device commands.
            device_controller: Interface for executing ADB commands.
        """
        self._capture_source = capture_source
        self._detector = detector
        self._tracker = tracker
        self._state_builder = state_builder
        self._policy = policy
        self._planner = planner
        self._device_controller = device_controller

        self._previous_state: GameState | None = None
        self._step_counter: int = 0

    def run_step(self) -> InferenceResult:
        """Execute a single pass of the inference pipeline.

        Returns:
            InferenceResult containing the execution metrics, the resulting
            GameState, and the executed ADB commands.

        Raises:
            PipelineError: If a critical pipeline component fails.
        """
        self._step_counter += 1
        t_start = time.perf_counter()

        # 1. Capture
        t0 = time.perf_counter()
        frame = self._capture_source.capture()
        capture_ms = (time.perf_counter() - t0) * 1000.0

        # 2. Detect
        t0 = time.perf_counter()
        detections = self._detector.detect(frame)
        detect_ms = (time.perf_counter() - t0) * 1000.0

        # 3. Track
        t0 = time.perf_counter()
        tracked_objects = self._tracker.track(detections)
        track_ms = (time.perf_counter() - t0) * 1000.0

        # 4. State Build
        t0 = time.perf_counter()
        state = self._state_builder.build(
            tracked_objects=tracked_objects,
            previous_state=self._previous_state,
        )
        self._previous_state = state
        state_build_ms = (time.perf_counter() - t0) * 1000.0

        # 5. Policy
        t0 = time.perf_counter()
        intent = self._policy.select_action(state)
        policy_ms = (time.perf_counter() - t0) * 1000.0

        # 6. Planner
        t0 = time.perf_counter()
        commands = self._planner.plan(intent, state)
        planner_ms = (time.perf_counter() - t0) * 1000.0

        # 7. Execute
        t0 = time.perf_counter()
        success = self._device_controller.execute(commands)
        if not success:
            raise PipelineError("Device controller failed to execute commands.")
        device_ms = (time.perf_counter() - t0) * 1000.0

        total_ms = (time.perf_counter() - t_start) * 1000.0

        metrics = StepMetrics(
            step_id=self._step_counter,
            capture_time_ms=capture_ms,
            detection_time_ms=detect_ms,
            tracking_time_ms=track_ms,
            state_builder_time_ms=state_build_ms,
            policy_time_ms=policy_ms,
            planner_time_ms=planner_ms,
            device_execution_time_ms=device_ms,
            total_pipeline_time_ms=total_ms,
        )

        return InferenceResult(
            metrics=metrics,
            state=state,
            commands=commands,
        )
