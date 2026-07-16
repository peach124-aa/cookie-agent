"""Unified GameState representation model."""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum, auto

from cookie_agent.core.tracking import TrackedObject
from cookie_agent.core.types import StepId


class JumpPhase(StrEnum):
    """Locomotion jumps state markers."""

    GROUNDED = auto()
    FIRST_JUMP = auto()
    SECOND_JUMP = auto()
    FALLING = auto()


@dataclass(frozen=True, slots=True)
class PlayerState:
    """Cookie status properties.

    Attributes:
        velocity_x: X-axis speed delta.
        velocity_y: Y-axis speed delta.
        jump_phase: Current jump status indicator.
        airborne: True if character is not grounded.
        grounded: True if character is touching a platform.
        time_since_last_jump: Jitter check clock.
        time_since_last_damage: Invincibility check clock.
        relay_available: Backup runner indicator.
        buffs: Optional custom metadata settings.
    """

    velocity_x: float
    velocity_y: float
    jump_phase: JumpPhase
    airborne: bool
    grounded: bool
    time_since_last_jump: float
    time_since_last_damage: float
    relay_available: bool
    buffs: dict[str, bool | float | str] | None = None


@dataclass(frozen=True, slots=True)
class MapHint:
    """Advisory metadata outlining target platforms."""

    target_coordinates: Sequence[tuple[int, int]]


@dataclass(frozen=True, slots=True)
class GameState:
    """Unified environment snapshot.

    Attributes:
        schema_version: Format compatibility key.
        player: Player state variables.
        objects: List of active TrackedObjects.
        scroll_speed: Estimated background scroll speed.
        scroll_distance: Distance traversed.
        step_id: Optional step counter index.
    """

    schema_version: int
    player: PlayerState
    objects: Sequence[TrackedObject]
    scroll_speed: float
    scroll_distance: float
    step_id: StepId | None = None
