"""Unit tests for the Cookie Environment orchestration module."""

from collections.abc import Sequence
from typing import cast

import pytest

from cookie_agent.core.actions import ActionIntent, ADBCommand, IntentType
from cookie_agent.core.detection import BBox, Detection, DetectionClass
from cookie_agent.core.frame import Frame
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState, JumpPhase, PlayerState
from cookie_agent.core.tracking import TrackedObject, TrackStatus
from cookie_agent.core.types import Confidence, FrameId, StepId, Timestamp, TrackId
from cookie_agent.environment import CookieEnvironment, EnvironmentError


class MockCaptureSource:
    def __init__(self, frame: Frame | None = None) -> None:
        self._frame: Frame | None = frame or Frame(
            frame_id=cast(FrameId, 1),
            timestamp=cast(Timestamp, 0.0),
            width=800,
            height=600,
            data=b"",
        )
        self.closed = False

    def capture(self) -> Frame | None:
        return self._frame

    def close(self) -> None:
        self.closed = True


class MockDetector:
    def detect(self, frame: Frame) -> list[Detection]:
        return [
            Detection(
                frame_id=cast(FrameId, 1),
                timestamp=cast(Timestamp, 0.0),
                class_name=DetectionClass.COOKIE,
                confidence=cast(Confidence, 0.99),
                bbox=BBox(0, 0, 10, 10),
            )
        ]

    def close(self) -> None:
        pass


class MockTracker:
    def track(self, detections: Sequence[Detection]) -> list[TrackedObject]:
        return [TrackedObject(cast(TrackId, 1), DetectionClass.COOKIE, BBox(0, 0, 10, 10), 0.0, 0.0, TrackStatus.ACTIVE)]


class MockStateBuilder:
    def build(self, *args, **kwargs) -> GameState:  # type: ignore
        return GameState(
            schema_version=1,
            player=PlayerState(0.0, 0.0, JumpPhase.GROUNDED, False, True, 0.0, 0.0, True, {}),
            objects=[],
            scroll_speed=100.0,
            scroll_distance=0.0,
            step_id=cast(StepId, 1),
        )


class MockRewardStrategy:
    def calculate(self, previous_state: GameState, current_state: GameState) -> RewardEvent:
        return RewardEvent(1.0, "MOCK_REWARD")


class MockDeviceController:
    def __init__(self) -> None:
        self.executed_commands: list[Sequence[ADBCommand]] = []
        self.disconnected = False

    def execute(self, commands: Sequence[ADBCommand]) -> bool:
        self.executed_commands.append(commands)
        return True

    def disconnect(self) -> None:
        self.disconnected = True


class MockActionPlanner:
    def plan(self, intent: ActionIntent, state: GameState) -> list[ADBCommand]:
        return []


@pytest.fixture
def environment() -> CookieEnvironment:
    return CookieEnvironment(
        capture_source=MockCaptureSource(),
        detector=MockDetector(),
        tracker=MockTracker(),
        state_builder=MockStateBuilder(),
        reward_strategy=MockRewardStrategy(),
        device_controller=MockDeviceController(),
        action_planner=MockActionPlanner(),
    )


def test_reset(environment: CookieEnvironment) -> None:
    """Verify reset creates initial state."""
    state = environment.reset()
    assert state.step_id == 1
    assert state.scroll_speed == 100.0


def test_step_without_reset(environment: CookieEnvironment) -> None:
    """Verify stepping before resetting raises EnvironmentError."""
    with pytest.raises(EnvironmentError):
        environment.step(ActionIntent(IntentType.NONE))


def test_step(environment: CookieEnvironment) -> None:
    """Verify stepping returns the proper tuple and pipes correctly."""
    environment.reset()
    
    state, reward, terminated, info = environment.step(ActionIntent(IntentType.JUMP))
    
    assert state.step_id == 1
    assert reward.value == 1.0
    assert reward.event_type == "MOCK_REWARD"
    assert terminated is False
    assert info.intent == ActionIntent(IntentType.JUMP)
    assert len(info.detections) == 1
    assert len(info.tracked_objects) == 1


def test_close(environment: CookieEnvironment) -> None:
    """Verify close cleans up resources properly."""
    environment.close()
    
    # We can inspect the internals for the test
    assert cast(MockCaptureSource, environment._capture_source).closed is True
    assert cast(MockDeviceController, environment._device_controller).disconnected is True


def test_capture_failure(environment: CookieEnvironment) -> None:
    """Verify missing frame returns error."""
    cast(MockCaptureSource, environment._capture_source)._frame = None
    
    with pytest.raises(EnvironmentError, match="Failed to capture initial frame"):
        environment.reset()
