"""Unit tests for the State Builder module in pure Python."""

from typing import cast

from cookie_agent.core.detection import BBox, DetectionClass
from cookie_agent.core.protocols import StateBuilder
from cookie_agent.core.state import GameState, JumpPhase, PlayerState
from cookie_agent.core.tracking import TrackedObject, TrackStatus
from cookie_agent.core.types import StepId, TrackId
from cookie_agent.state_builder import DefaultStateBuilder


def test_builder_protocol_conformance() -> None:
    """Verify DefaultStateBuilder conforms to StateBuilder protocol."""
    builder = DefaultStateBuilder()
    assert isinstance(builder, StateBuilder)


def test_builder_initial_state() -> None:
    """Verify state builder creates correct initial state with no previous state."""
    builder = DefaultStateBuilder(schema_version=1, fixed_dt=0.1)

    cookie = TrackedObject(
        object_id=cast(TrackId, 1),
        class_name=DetectionClass.COOKIE,
        bbox=BBox(0, 0, 10, 10),
        velocity_x=0.0,
        velocity_y=0.0,
        status=TrackStatus.ACTIVE,
    )

    state = builder.build(
        tracked_objects=[cookie],
        ocr_results={"health": 100.0},
        character_status={"relay_available": True},
        map_hint=None,
        previous_state=None,
    )

    assert state.schema_version == 1
    assert state.step_id == 1
    assert state.scroll_speed == 0.0
    assert state.scroll_distance == 0.0

    player = state.player
    assert player.velocity_x == 0.0
    assert player.velocity_y == 0.0
    assert player.grounded is True
    assert player.airborne is False
    assert player.jump_phase == JumpPhase.GROUNDED
    assert player.time_since_last_jump == 0.0
    assert player.time_since_last_damage == 0.0
    assert player.relay_available is True
    assert player.buffs == {}


def test_builder_scroll_speed() -> None:
    """Verify scroll speed is derived correctly from static obstacles."""
    builder = DefaultStateBuilder(fixed_dt=0.1)

    obstacle = TrackedObject(
        object_id=cast(TrackId, 2),
        class_name=DetectionClass.OBSTACLE_GROUND,
        bbox=BBox(100, 0, 110, 10),
        velocity_x=-300.0,
        velocity_y=0.0,
        status=TrackStatus.ACTIVE,
    )

    state = builder.build(
        tracked_objects=[obstacle],
        ocr_results={},
        character_status={},
    )

    assert state.scroll_speed == 300.0
    assert state.scroll_distance == 0.0


def test_builder_jump_transitions() -> None:
    """Verify player jump phase transitions."""
    builder = DefaultStateBuilder(fixed_dt=0.1)

    # State 1: Grounded
    cookie_ground = TrackedObject(
        cast(TrackId, 1),
        DetectionClass.COOKIE,
        BBox(0, 0, 10, 10),
        0.0,
        0.0,
        TrackStatus.ACTIVE,
    )
    state1 = builder.build([cookie_ground], {}, {})
    assert state1.player.jump_phase == JumpPhase.GROUNDED

    # State 2: First Jump (moving up)
    cookie_jump1 = TrackedObject(
        cast(TrackId, 1),
        DetectionClass.COOKIE,
        BBox(0, 0, 10, 10),
        0.0,
        -100.0,
        TrackStatus.ACTIVE,
    )
    state2 = builder.build([cookie_jump1], {}, {}, previous_state=state1)
    assert state2.player.jump_phase == JumpPhase.FIRST_JUMP
    assert state2.player.time_since_last_jump == 0.0  # reset on transition

    # State 3: Still First Jump (moving up, but not a new jump)
    cookie_jump1_cont = TrackedObject(
        cast(TrackId, 1),
        DetectionClass.COOKIE,
        BBox(0, 0, 10, 10),
        0.0,
        -80.0,
        TrackStatus.ACTIVE,
    )
    state3 = builder.build([cookie_jump1_cont], {}, {}, previous_state=state2)
    assert state3.player.jump_phase == JumpPhase.FIRST_JUMP
    assert state3.player.time_since_last_jump == 0.1

    # State 4: Second Jump (sudden large upward velocity)
    cookie_jump2 = TrackedObject(
        cast(TrackId, 1),
        DetectionClass.COOKIE,
        BBox(0, 0, 10, 10),
        0.0,
        -150.0,
        TrackStatus.ACTIVE,
    )
    state4 = builder.build([cookie_jump2], {}, {}, previous_state=state3)
    assert state4.player.jump_phase == JumpPhase.SECOND_JUMP
    assert state4.player.time_since_last_jump == 0.0  # reset on transition

    # State 5: Falling (moving down)
    cookie_fall = TrackedObject(
        cast(TrackId, 1),
        DetectionClass.COOKIE,
        BBox(0, 0, 10, 10),
        0.0,
        50.0,
        TrackStatus.ACTIVE,
    )
    state5 = builder.build([cookie_fall], {}, {}, previous_state=state4)
    assert state5.player.jump_phase == JumpPhase.FALLING
    assert state5.player.time_since_last_jump == 0.1


def test_builder_character_status_override() -> None:
    """Verify character_status dictionary overrides heuristics."""
    builder = DefaultStateBuilder()
    cookie = TrackedObject(
        cast(TrackId, 1),
        DetectionClass.COOKIE,
        BBox(0, 0, 10, 10),
        0.0,
        0.0,
        TrackStatus.ACTIVE,
    )

    # Even though velocity is 0 (normally GROUNDED), we force FALLING via character_status
    state = builder.build(
        [cookie], {}, {"jump_phase": "FALLING", "airborne": True, "grounded": False}
    )

    assert state.player.jump_phase == JumpPhase.FALLING
    assert state.player.airborne is True
    assert state.player.grounded is False


def test_builder_timers_and_scroll() -> None:
    """Verify timers accumulate and scroll distance integrates correctly."""
    builder = DefaultStateBuilder(fixed_dt=0.5)

    prev_player = PlayerState(
        0.0, 0.0, JumpPhase.GROUNDED, False, True, 1.0, 5.0, False
    )
    prev_state = GameState(1, prev_player, [], 200.0, 1000.0, cast(StepId, 5))

    state = builder.build([], {}, {}, previous_state=prev_state)

    # No static objects -> scroll_speed remains 200.0
    assert state.scroll_speed == 200.0
    # distance = 1000 + 200 * 0.5 = 1100
    assert state.scroll_distance == 1100.0
    assert state.step_id == 6

    # Timers should add dt (0.5)
    assert state.player.time_since_last_jump == 1.5
    assert state.player.time_since_last_damage == 5.5

    # Trigger damage reset
    state_dmg = builder.build([], {}, {"damage_taken": True}, previous_state=state)
    assert state_dmg.player.time_since_last_damage == 0.0
