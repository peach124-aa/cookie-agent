"""Unit tests for the Action Planner module."""

import pytest

from cookie_agent.core.actions import ActionIntent, ADBCommand, InputKind, IntentType
from cookie_agent.core.protocols import ActionPlanner
from cookie_agent.core.state import GameState, JumpPhase, PlayerState
from cookie_agent.planner import builder, mapping
from cookie_agent.planner.exceptions import MappingError
from cookie_agent.planner.planner import CookieActionPlanner


@pytest.fixture
def dummy_state() -> GameState:
    """Fixture to provide a dummy state since planner ignores it mostly."""
    player = PlayerState(
        velocity_x=0.0,
        velocity_y=0.0,
        jump_phase=JumpPhase.GROUNDED,
        airborne=False,
        grounded=True,
        time_since_last_jump=0.0,
        time_since_last_damage=0.0,
        relay_available=False,
    )
    return GameState(
        schema_version=1,
        player=player,
        objects=[],
        scroll_speed=0.0,
        scroll_distance=0.0,
    )


def test_planner_protocol_conformance() -> None:
    """Verify CookieActionPlanner adheres to the ActionPlanner protocol."""
    planner = CookieActionPlanner()
    assert isinstance(planner, ActionPlanner)


def test_builder_helpers() -> None:
    """Verify builder functions yield valid ADB sequences."""
    # Test tap
    t = builder.tap(x=10, y=20, hold_ms=50, delay_ms=10)
    assert len(t) == 2
    assert t[0] == ADBCommand(InputKind.TOUCH_DOWN, 10, 20, 50, 0)
    assert t[1] == ADBCommand(InputKind.TOUCH_UP, 10, 20, 0, 10)
    
    # Test hold
    h = builder.hold(x=15, y=25, hold_ms=500, delay_ms=0)
    assert len(h) == 2
    assert h[0] == ADBCommand(InputKind.TOUCH_DOWN, 15, 25, 500, 0)
    assert h[1] == ADBCommand(InputKind.TOUCH_UP, 15, 25, 0, 0)
    
    # Test release
    r = builder.release(x=5, y=5, delay_ms=10)
    assert isinstance(r, ADBCommand)
    assert r == ADBCommand(InputKind.TOUCH_UP, 5, 5, 0, 10)
    
    # Test swipe
    s = builder.swipe(10, 10, 20, 20, 100)
    assert len(s) == 3
    assert s[0].kind == InputKind.TOUCH_DOWN
    assert s[1].kind == InputKind.TOUCH_MOVE
    assert s[2].kind == InputKind.TOUCH_UP


def test_planner_mapping_idle(dummy_state: GameState) -> None:
    """Verify IDLE yields empty commands."""
    planner = CookieActionPlanner()
    
    cmds = planner.plan(ActionIntent(IntentType.IDLE), dummy_state)
    assert len(cmds) == 0
    
    cmds = planner.plan(ActionIntent(IntentType.NONE), dummy_state)
    assert len(cmds) == 0


def test_planner_mapping_jump(dummy_state: GameState) -> None:
    """Verify JUMP taps correctly."""
    planner = CookieActionPlanner()
    cmds = planner.plan(ActionIntent(IntentType.JUMP), dummy_state)
    
    assert len(cmds) == 2
    assert cmds[0].kind == InputKind.TOUCH_DOWN
    assert cmds[0].x == mapping.JUMP_BUTTON_X
    assert cmds[0].y == mapping.JUMP_BUTTON_Y


def test_planner_mapping_double_jump(dummy_state: GameState) -> None:
    """Verify DOUBLE_JUMP taps twice."""
    planner = CookieActionPlanner()
    cmds = planner.plan(ActionIntent(IntentType.DOUBLE_JUMP), dummy_state)
    
    assert len(cmds) == 4
    # First tap
    assert cmds[0].kind == InputKind.TOUCH_DOWN
    assert cmds[1].kind == InputKind.TOUCH_UP
    assert cmds[1].delay_ms > 0
    # Second tap
    assert cmds[2].kind == InputKind.TOUCH_DOWN
    assert cmds[3].kind == InputKind.TOUCH_UP


def test_planner_mapping_slide(dummy_state: GameState) -> None:
    """Verify SLIDE issues hold."""
    planner = CookieActionPlanner()
    cmds = planner.plan(ActionIntent(IntentType.SLIDE), dummy_state)
    
    assert len(cmds) == 2
    assert cmds[0].kind == InputKind.TOUCH_DOWN
    assert cmds[0].x == mapping.SLIDE_BUTTON_X
    assert cmds[0].hold_ms > 50


def test_planner_mapping_dash(dummy_state: GameState) -> None:
    """Verify DASH issues swipe."""
    planner = CookieActionPlanner()
    cmds = planner.plan(ActionIntent(IntentType.DASH), dummy_state)
    
    assert len(cmds) == 3
    assert cmds[0].kind == InputKind.TOUCH_DOWN
    assert cmds[1].kind == InputKind.TOUCH_MOVE
    assert cmds[2].kind == InputKind.TOUCH_UP


def test_planner_mapping_invalid(dummy_state: GameState) -> None:
    """Verify invalid intents raise MappingError."""
    planner = CookieActionPlanner()
    
    # Cast a bad string to IntentType for testing the exception route
    bad_intent = ActionIntent(intent="INVALID") # type: ignore[arg-type]
    
    with pytest.raises(MappingError, match="Unsupported intent mapping: INVALID"):
        planner.plan(bad_intent, dummy_state)
