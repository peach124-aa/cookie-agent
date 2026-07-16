"""Cookie Run orchestration Environment."""

from typing import Any

from cookie_agent.core.actions import ActionIntent
from cookie_agent.core.protocols import (
    ActionPlanner,
    CaptureSource,
    Detector,
    DeviceController,
    RewardStrategy,
    StateBuilder,
    Tracker,
)
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState
from cookie_agent.environment.exceptions import EnvironmentError
from cookie_agent.environment.info import StepInfo


class CookieEnvironment:
    """Central orchestrator for the Cookie Run agent pipeline.

    Connects capture, detection, tracking, state building, rewarding, and hardware control.
    """

    def __init__(
        self,
        capture_source: CaptureSource,
        detector: Detector,
        tracker: Tracker,
        state_builder: StateBuilder,
        reward_strategy: RewardStrategy,
        device_controller: DeviceController,
        action_planner: ActionPlanner,
    ):
        """Initialize the orchestration environment.

        Args:
            capture_source: Source of video frames.
            detector: Model inference for object detection.
            tracker: Multi-object temporal tracker.
            state_builder: Constructs GameState from observations.
            reward_strategy: Computes evaluation metrics.
            device_controller: Hardware touch executor.
            action_planner: Translates abstract intents to ADB commands.
        """
        self._capture_source = capture_source
        self._detector = detector
        self._tracker = tracker
        self._state_builder = state_builder
        self._reward_strategy = reward_strategy
        self._device_controller = device_controller
        self._action_planner = action_planner

        self._previous_state: GameState | None = None

    def reset(self) -> GameState:
        """Reset the environment to start a new episode.

        Returns:
            The initial GameState.
        """
        frame = self._capture_source.capture()
        if frame is None:
            raise EnvironmentError("Failed to capture initial frame.")

        detections = self._detector.detect(frame)
        tracked_objects = self._tracker.track(detections)

        # Environment does not handle OCR or Character status currently.
        # StateBuilder extracts what it can or relies on defaults.
        state = self._state_builder.build(
            tracked_objects=tracked_objects,
            ocr_results={},
            character_status={},
            map_hint=None,
            previous_state=None,
        )

        self._previous_state = state
        return state

    def step(
        self, action: ActionIntent
    ) -> tuple[GameState, RewardEvent, bool, StepInfo]:
        """Execute a step in the environment.

        Args:
            action: The high-level intent to execute.

        Returns:
            A tuple of (GameState, RewardEvent, terminated, StepInfo).
        """
        if self._previous_state is None:
            raise EnvironmentError("Cannot step before reset is called.")

        # 1. Plan and execute action
        commands = self._action_planner.plan(action, self._previous_state)
        self._device_controller.execute(commands)

        # 2. Capture frame
        frame = self._capture_source.capture()
        if frame is None:
            raise EnvironmentError("Failed to capture frame during step.")

        # 3 & 4. Detect and Track
        detections = self._detector.detect(frame)
        tracked_objects = self._tracker.track(detections)

        # 5. Build State
        current_state = self._state_builder.build(
            tracked_objects=tracked_objects,
            ocr_results={},
            character_status={},
            map_hint=None,
            previous_state=self._previous_state,
        )

        # 6. Compute Reward
        reward = self._reward_strategy.calculate(self._previous_state, current_state)

        # Update tracking reference
        self._previous_state = current_state

        step_info = StepInfo(
            frame=frame,
            intent=action,
            commands=commands,
            detections=detections,
            tracked_objects=tracked_objects,
        )

        return current_state, reward, False, step_info

    def close(self) -> None:
        """Release owned resources by shutting down dependencies if supported."""
        components: list[Any] = [
            self._capture_source,
            self._detector,
            self._tracker,
            self._state_builder,
            self._reward_strategy,
            self._device_controller,
            self._action_planner,
        ]

        for component in components:
            if hasattr(component, "close") and callable(component.close):
                component.close()
            elif hasattr(component, "disconnect") and callable(component.disconnect):
                component.disconnect()
            elif hasattr(component, "stop") and callable(component.stop):
                component.stop()
