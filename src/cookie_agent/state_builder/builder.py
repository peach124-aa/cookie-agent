"""Default implementation of the State Builder protocol."""

from collections.abc import Sequence
from typing import cast

from cookie_agent.core.detection import DetectionClass
from cookie_agent.core.protocols import StateBuilder
from cookie_agent.core.state import GameState, JumpPhase, MapHint, PlayerState
from cookie_agent.core.tracking import TrackedObject
from cookie_agent.core.types import StepId


class DefaultStateBuilder(StateBuilder):
    """Constructs a unified GameState from sensor and tracking outputs.

    Implements heuristics to derive temporal features if not provided directly.
    """

    def __init__(self, schema_version: int = 1, fixed_dt: float = 1 / 30.0):
        """Initialize DefaultStateBuilder.

        Args:
            schema_version: Format version for the emitted GameState.
            fixed_dt: Assumed time delta per step for timers.
        """
        self.schema_version = schema_version
        self.fixed_dt = fixed_dt

    def build(
        self,
        tracked_objects: Sequence[TrackedObject],
        ocr_results: dict[str, float | str],
        character_status: dict[str, bool | float | str],
        map_hint: MapHint | None = None,
        previous_state: GameState | None = None,
    ) -> GameState:
        """Compose the unified state representation."""
        # 1. Identify Cookie properties
        cookie = next(
            (obj for obj in tracked_objects if obj.class_name == DetectionClass.COOKIE),
            None,
        )

        cookie_vel_x = cookie.velocity_x if cookie else 0.0
        cookie_vel_y = cookie.velocity_y if cookie else 0.0

        if not cookie and previous_state:
            cookie_vel_x = previous_state.player.velocity_x
            cookie_vel_y = previous_state.player.velocity_y

        # 2. Derive Grounded/Airborne
        # Assume Y-axis points down (positive = down, negative = up)
        # Moving up (vel_y < -10) -> airborne
        # Moving down (vel_y > 10) -> airborne
        # Still (abs(vel_y) <= 10) -> grounded
        grounded = bool(character_status.get("grounded", abs(cookie_vel_y) <= 10.0))
        airborne = bool(character_status.get("airborne", not grounded))

        # 3. Derive Jump Phase
        jump_phase_str = character_status.get("jump_phase")
        if isinstance(jump_phase_str, str):
            jump_phase = JumpPhase(jump_phase_str.lower())
        else:
            if grounded:
                jump_phase = JumpPhase.GROUNDED
            elif cookie_vel_y > 10.0:
                jump_phase = JumpPhase.FALLING
            else:
                jump_phase = JumpPhase.FIRST_JUMP
                if previous_state and previous_state.player.jump_phase in (
                    JumpPhase.FALLING,
                    JumpPhase.FIRST_JUMP,
                ):
                    # If we were falling or already jumping and are now moving up significantly,
                    # we can assume a second jump (or double jump) was triggered.
                    if (
                        cookie_vel_y < -50.0
                        and previous_state.player.time_since_last_jump > 0.0
                    ):
                        jump_phase = JumpPhase.SECOND_JUMP
                    else:
                        # Retain previous phase if velocity hasn't changed drastically
                        jump_phase = previous_state.player.jump_phase

        # 4. Timers
        time_since_last_jump = 0.0
        if previous_state:
            time_since_last_jump = (
                previous_state.player.time_since_last_jump + self.fixed_dt
            )
            # Reset if transitioning from grounded to jump, or first to second
            if (
                previous_state.player.jump_phase == JumpPhase.GROUNDED
                and jump_phase == JumpPhase.FIRST_JUMP
            ) or (
                previous_state.player.jump_phase == JumpPhase.FIRST_JUMP
                and jump_phase == JumpPhase.SECOND_JUMP
            ):
                time_since_last_jump = 0.0

        time_since_last_damage = 0.0
        if previous_state:
            time_since_last_damage = (
                previous_state.player.time_since_last_damage + self.fixed_dt
            )

        # Check for damage from OCR
        health = float(ocr_results.get("health", -1.0))
        if character_status.get("damage_taken", False):
            time_since_last_damage = 0.0
        elif previous_state and health >= 0:
            pass  # Further health logic could go here

        relay_avail = bool(character_status.get("relay_available", False))

        player_state = PlayerState(
            velocity_x=cookie_vel_x,
            velocity_y=cookie_vel_y,
            jump_phase=jump_phase,
            airborne=airborne,
            grounded=grounded,
            time_since_last_jump=time_since_last_jump,
            time_since_last_damage=time_since_last_damage,
            relay_available=relay_avail,
            buffs={
                k[5:]: v for k, v in character_status.items() if k.startswith("buff_")
            },
        )

        # 5. Scroll Speed and Distance
        # Average x-velocity of static objects (Jelly, Obstacles)
        static_classes = {
            DetectionClass.JELLY,
            DetectionClass.OBSTACLE_GROUND,
            DetectionClass.OBSTACLE_AIR,
            DetectionClass.POTION,
            DetectionClass.COIN,
        }
        static_objs = [
            obj for obj in tracked_objects if obj.class_name in static_classes
        ]

        if static_objs:
            # Static objects move left on screen, so velocity_x is negative. Speed is magnitude.
            avg_vx = sum(obj.velocity_x for obj in static_objs) / len(static_objs)
            scroll_speed = float(-avg_vx)
        elif previous_state:
            scroll_speed = previous_state.scroll_speed
        else:
            scroll_speed = 0.0

        # Don't let scroll speed be negative
        scroll_speed = max(0.0, scroll_speed)

        scroll_distance = 0.0
        if previous_state:
            scroll_distance = (
                previous_state.scroll_distance + scroll_speed * self.fixed_dt
            )

        step_id = 1
        if previous_state and previous_state.step_id is not None:
            step_id = previous_state.step_id + 1

        return GameState(
            schema_version=self.schema_version,
            player=player_state,
            objects=list(tracked_objects),
            scroll_speed=scroll_speed,
            scroll_distance=scroll_distance,
            step_id=cast(StepId, step_id),
        )
