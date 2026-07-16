"""Unit tests for the Cookie Agent core interface models and protocols."""

from collections.abc import Sequence
from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest
from cookie_agent.core import (
    ActionIntent,
    ActionPlanner,
    ADBCommand,
    BBox,
    CaptureSource,
    Confidence,
    Detection,
    DetectionClass,
    Detector,
    DeviceController,
    Frame,
    FrameId,
    GameState,
    InputKind,
    IntentType,
    JumpPhase,
    LaneIndex,
    MapHint,
    PlayerState,
    Policy,
    ReplayObserver,
    RewardEvent,
    RewardStrategy,
    StateBuilder,
    StepId,
    Timestamp,
    TrackedObject,
    Tracker,
    TrackId,
    TrackStatus,
)


def test_newtypes() -> None:
    """Verify construction of custom NewTypes."""
    assert FrameId(1) == 1
    assert TrackId(2) == 2
    assert StepId(3) == 3
    assert Timestamp(1.5) == 1.5
    assert LaneIndex(4) == 4
    assert Confidence(0.99) == 0.99


def test_frame_properties() -> None:
    """Verify Frame construction, immutability, and resolution property."""
    frame = Frame(
        frame_id=FrameId(42),
        timestamp=Timestamp(123.45),
        width=1280,
        height=720,
        data=b"\x00\xff",
    )
    assert frame.frame_id == 42
    assert frame.timestamp == 123.45
    assert frame.resolution == (1280, 720)

    with pytest.raises(FrozenInstanceError):
        cast(Any, frame).width = 1920


def test_bbox_and_detection_properties() -> None:
    """Verify BBox properties and Detection delegation."""
    bbox = BBox(xmin=10, ymin=20, xmax=30, ymax=60)
    assert bbox.width == 20
    assert bbox.height == 40
    assert bbox.area == 800
    assert bbox.center == (20.0, 40.0)

    detection = Detection(
        frame_id=FrameId(1),
        timestamp=Timestamp(1.0),
        class_name=DetectionClass.JELLY,
        bbox=bbox,
        confidence=Confidence(0.95),
        lane=LaneIndex(2),
        detector_name="yolo",
    )
    assert detection.center == (20.0, 40.0)

    with pytest.raises(FrozenInstanceError):
        cast(Any, detection).confidence = Confidence(0.99)


def test_tracked_object_mutability() -> None:
    """Verify that TrackedObject is mutable and supports changes."""
    bbox = BBox(xmin=15, ymin=25, xmax=35, ymax=45)
    obj = TrackedObject(
        object_id=TrackId(99),
        class_name=DetectionClass.OBSTACLE_GROUND,
        bbox=bbox,
        velocity_x=-5.0,
        velocity_y=0.0,
        status=TrackStatus.ACTIVE,
    )
    assert obj.object_id == 99
    assert obj.status == TrackStatus.ACTIVE

    # Validate mutability (no FrozenInstanceError raised)
    obj.status = TrackStatus.LOST
    assert obj.status == TrackStatus.LOST

    obj.velocity_x = -10.0
    assert obj.velocity_x == -10.0


def test_game_state_construction() -> None:
    """Verify PlayerState and GameState construction and immutability."""
    player = PlayerState(
        velocity_x=10.0,
        velocity_y=0.0,
        jump_phase=JumpPhase.GROUNDED,
        airborne=False,
        grounded=True,
        time_since_last_jump=0.5,
        time_since_last_damage=1.2,
        relay_available=True,
        buffs={"giant": True},
    )
    state = GameState(
        schema_version=1,
        player=player,
        objects=[],
        scroll_speed=5.0,
        scroll_distance=100.0,
        step_id=StepId(10),
    )
    assert state.schema_version == 1
    assert state.step_id == 10

    with pytest.raises(FrozenInstanceError):
        cast(Any, state).scroll_speed = 6.0


def test_action_and_command_construction() -> None:
    """Verify ActionIntent and ADBCommand properties."""
    intent = ActionIntent(intent=IntentType.JUMP)
    assert intent.intent == IntentType.JUMP

    command = ADBCommand(
        kind=InputKind.TOUCH_DOWN,
        x=200,
        y=400,
        hold_ms=50,
        delay_ms=10,
    )
    assert command.kind == InputKind.TOUCH_DOWN

    with pytest.raises(FrozenInstanceError):
        cast(Any, command).x = 250


def test_reward_event_construction() -> None:
    """Verify RewardEvent properties and immutability."""
    event = RewardEvent(value=100.0, event_type="jelly_collected")
    assert event.value == 100.0

    with pytest.raises(FrozenInstanceError):
        cast(Any, event).value = 50.0


def test_enums_values() -> None:
    """Verify that enums match spec categories."""
    assert DetectionClass.COOKIE.value == "cookie"
    assert TrackStatus.OCCLUDED.value == "occluded"
    assert JumpPhase.SECOND_JUMP.value == "second_jump"
    assert IntentType.SLIDE.value == "slide"
    assert InputKind.TOUCH_UP.value == "touch_up"


class DummyCaptureSource:
    """Stub conforming to CaptureSource protocol."""

    def capture(self) -> Frame | None:
        """Capture dummy frame."""
        return Frame(FrameId(1), Timestamp(1.0), 10, 10, b"")


class DummyDetector:
    """Stub conforming to Detector protocol."""

    def detect(self, frame: Frame) -> list[Detection]:
        """Detect dummy elements."""
        _ = frame
        return []


class DummyTracker:
    """Stub conforming to Tracker protocol."""

    def track(self, detections: Sequence[Detection]) -> list[TrackedObject]:
        """Track dummy objects."""
        _ = detections
        return []


class DummyStateBuilder:
    """Stub conforming to StateBuilder protocol."""

    def build(
        self,
        tracked_objects: Sequence[TrackedObject],
        ocr_results: dict[str, float | str],
        character_status: dict[str, bool | float | str],
        map_hint: MapHint | None = None,
        previous_state: GameState | None = None,
    ) -> GameState:
        """Compose GameState."""
        _ = tracked_objects
        _ = ocr_results
        _ = character_status
        _ = map_hint
        _ = previous_state
        player = PlayerState(0.0, 0.0, JumpPhase.GROUNDED, False, True, 0.0, 0.0, True)
        return GameState(1, player, [], 0.0, 0.0)


class DummyRewardStrategy:
    """Stub conforming to RewardStrategy protocol."""

    def calculate(
        self,
        previous_state: GameState,
        current_state: GameState,
    ) -> RewardEvent:
        """Calculate step score."""
        _ = previous_state
        _ = current_state
        return RewardEvent(0.0, "none")


class DummyPolicy:
    """Stub conforming to Policy protocol."""

    def select_action(self, state: GameState) -> ActionIntent:
        """Select action intent."""
        _ = state
        return ActionIntent(IntentType.NONE)


class DummyActionPlanner:
    """Stub conforming to ActionPlanner protocol."""

    def plan(self, intent: ActionIntent, state: GameState) -> list[ADBCommand]:
        """Plan click events."""
        _ = intent
        _ = state
        return []


class DummyDeviceController:
    """Stub conforming to DeviceController protocol."""

    def execute(self, commands: Sequence[ADBCommand]) -> bool:
        """Execute tap actions."""
        _ = commands
        return True


class DummyReplayObserver:
    """Stub conforming to ReplayObserver protocol."""

    def observe(
        self,
        frame: Frame,
        commands: Sequence[ADBCommand],
        metadata: dict[str, bool | float | str],
    ) -> None:
        """Observe timeline step."""
        _ = frame
        _ = commands
        _ = metadata


def test_protocol_conformance_and_runtime_checks() -> None:
    """Verify runtime checkability and conformance of protocols."""
    capture_source = DummyCaptureSource()
    assert isinstance(capture_source, CaptureSource)
    assert capture_source.capture() is not None

    detector = DummyDetector()
    assert isinstance(detector, Detector)
    assert len(detector.detect(capture_source.capture())) == 0  # type: ignore[arg-type]

    tracker = DummyTracker()
    assert isinstance(tracker, Tracker)
    assert len(tracker.track([])) == 0

    state_builder = DummyStateBuilder()
    assert isinstance(state_builder, StateBuilder)
    ocr_res: dict[str, float | str] = {}
    char_status: dict[str, bool | float | str] = {}
    state = state_builder.build([], ocr_res, char_status)
    assert state.schema_version == 1

    reward_strategy = DummyRewardStrategy()
    assert isinstance(reward_strategy, RewardStrategy)
    assert reward_strategy.calculate(state, state).value == 0.0

    policy = DummyPolicy()
    assert isinstance(policy, Policy)
    assert policy.select_action(state).intent == IntentType.NONE

    action_planner = DummyActionPlanner()
    assert isinstance(action_planner, ActionPlanner)
    assert len(action_planner.plan(policy.select_action(state), state)) == 0

    device_controller = DummyDeviceController()
    assert isinstance(device_controller, DeviceController)
    assert device_controller.execute([]) is True

    replay_observer = DummyReplayObserver()
    assert isinstance(replay_observer, ReplayObserver)
    # Validate method executes
    replay_observer.observe(state_builder.build([], {}, {}), [], {})  # type: ignore[arg-type]
