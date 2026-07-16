"""Expose public core interface models, contracts, and types."""

from cookie_agent.core.actions import ActionIntent, ADBCommand, InputKind, IntentType
from cookie_agent.core.detection import BBox, Detection, DetectionClass
from cookie_agent.core.frame import Frame
from cookie_agent.core.protocols import (
    ActionPlanner,
    CaptureSource,
    Detector,
    DeviceController,
    Policy,
    ReplayObserver,
    RewardStrategy,
    StateBuilder,
    Tracker,
)
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState, JumpPhase, MapHint, PlayerState
from cookie_agent.core.tracking import TrackedObject, TrackStatus
from cookie_agent.core.types import (
    Confidence,
    FrameId,
    LaneIndex,
    StepId,
    Timestamp,
    TrackId,
)

__all__: list[str] = [
    "ADBCommand",
    "ActionIntent",
    "ActionPlanner",
    "BBox",
    "CaptureSource",
    "Confidence",
    "Detection",
    "DetectionClass",
    "Detector",
    "DeviceController",
    "Frame",
    "FrameId",
    "GameState",
    "InputKind",
    "IntentType",
    "JumpPhase",
    "LaneIndex",
    "MapHint",
    "PlayerState",
    "Policy",
    "ReplayObserver",
    "RewardEvent",
    "RewardStrategy",
    "StateBuilder",
    "StepId",
    "Timestamp",
    "TrackId",
    "TrackStatus",
    "TrackedObject",
    "Tracker",
]
