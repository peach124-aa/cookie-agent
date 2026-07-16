"""Locomotion intent and command mappings."""

from dataclasses import dataclass
from enum import StrEnum, auto


class IntentType(StrEnum):
    """Locomotion behavior options."""

    NONE = auto()
    IDLE = auto()
    JUMP = auto()
    DOUBLE_JUMP = auto()
    SLIDE = auto()
    DASH = auto()
    RELAY = auto()


@dataclass(frozen=True, slots=True)
class ActionIntent:
    """Decision representing high-level locomotion intent.

    Attributes:
        intent: Classified movement option.
    """

    intent: IntentType


class InputKind(StrEnum):
    """Kinds of touch inputs emulated on device."""

    TOUCH_DOWN = auto()
    TOUCH_UP = auto()
    TOUCH_MOVE = auto()


@dataclass(frozen=True, slots=True)
class ADBCommand:
    """Low-level touchscreen event instruction.

    Attributes:
        kind: Target Touch event action.
        x: X-coordinate target offset.
        y: Y-coordinate target offset.
        hold_ms: Trigger hold duration.
        delay_ms: Trigger pause before next injection.
    """

    kind: InputKind
    x: int
    y: int
    hold_ms: int
    delay_ms: int
