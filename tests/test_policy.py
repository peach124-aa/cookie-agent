"""Unit tests for the Policy module."""

import pytest

from cookie_agent.core.actions import ActionIntent, IntentType
from cookie_agent.core.detection import BBox, DetectionClass
from cookie_agent.core.state import GameState, JumpPhase, PlayerState
from cookie_agent.core.tracking import TrackedObject, TrackStatus
from cookie_agent.core.types import TrackId
from cookie_agent.policy.exceptions import PolicyError
from cookie_agent.policy.ppo_policy import PPOPolicy
from cookie_agent.policy.rule_policy import RulePolicy
from cookie_agent.policy.selector import PolicySelector


def create_mock_state(grounded: bool, obj_xmin: int) -> GameState:
    """Create a minimal mocked GameState for testing."""
    player = PlayerState(
        velocity_x=10.0,
        velocity_y=0.0,
        jump_phase=JumpPhase.GROUNDED if grounded else JumpPhase.FALLING,
        airborne=not grounded,
        grounded=grounded,
        time_since_last_jump=0.0,
        time_since_last_damage=0.0,
        relay_available=True,
    )
    
    bbox = BBox(xmin=obj_xmin, ymin=0, xmax=obj_xmin + 10, ymax=10)
    obj = TrackedObject(
        object_id=TrackId(1),
        class_name=DetectionClass.OBSTACLE_GROUND,
        bbox=bbox,
        velocity_x=0.0,
        velocity_y=0.0,
        status=TrackStatus.ACTIVE,
    )
    
    return GameState(
        schema_version=1,
        player=player,
        objects=[obj],
        scroll_speed=10.0,
        scroll_distance=100.0,
    )


def test_rule_policy_determinstic() -> None:
    """Verify RulePolicy yields JUMP when obstacles are close."""
    policy = RulePolicy(jump_threshold_x=20.0)
    
    # Grounded with close obstacle (xmin = 10 < 20) -> JUMP
    state1 = create_mock_state(grounded=True, obj_xmin=10)
    assert policy.select_action(state1) == ActionIntent(IntentType.JUMP)
    
    # Grounded with far obstacle (xmin = 30 > 20) -> NONE
    state2 = create_mock_state(grounded=True, obj_xmin=30)
    assert policy.select_action(state2) == ActionIntent(IntentType.NONE)
    
    # Not grounded with close obstacle -> NONE (wait to land)
    state3 = create_mock_state(grounded=False, obj_xmin=10)
    assert policy.select_action(state3) == ActionIntent(IntentType.NONE)


class MockPPOAgent:
    def __init__(self, action: ActionIntent, fail: bool = False) -> None:
        self._action = action
        self._fail = fail

    def predict(self, state: GameState) -> ActionIntent:
        if self._fail:
            raise ValueError("Network error")
        return self._action


def test_ppo_policy_adapter() -> None:
    """Verify PPOPolicy correctly delegates to the agent protocol."""
    agent = MockPPOAgent(ActionIntent(IntentType.SLIDE))
    policy = PPOPolicy(agent)
    
    state = create_mock_state(grounded=True, obj_xmin=50)
    assert policy.select_action(state) == ActionIntent(IntentType.SLIDE)


def test_ppo_policy_exception() -> None:
    """Verify PPOPolicy catches and wraps agent errors."""
    agent = MockPPOAgent(ActionIntent(IntentType.NONE), fail=True)
    policy = PPOPolicy(agent)
    
    state = create_mock_state(grounded=True, obj_xmin=50)
    with pytest.raises(PolicyError, match="PPO Agent inference failed"):
        policy.select_action(state)


def test_policy_selector() -> None:
    """Verify PolicySelector dynamic routing and DI."""
    rule_pol = RulePolicy()
    ppo_pol = PPOPolicy(MockPPOAgent(ActionIntent(IntentType.JUMP)))
    
    registry = {
        "rule": rule_pol,
        "ppo": ppo_pol,
    }
    
    selector = PolicySelector(policies=registry, default_policy="rule")  # type: ignore[arg-type]
    # ignoring type check on dict instantiation because PolicySelector takes Mapping/dict of PolicyProtocol
    
    state = create_mock_state(grounded=True, obj_xmin=50) # Far obstacle -> Rule returns NONE
    
    # Default is rule
    assert selector.select_action(state) == ActionIntent(IntentType.NONE)
    
    # Switch to PPO
    selector.set_active_policy("ppo")
    assert selector.select_action(state) == ActionIntent(IntentType.JUMP)


def test_policy_selector_invalid_config() -> None:
    """Verify PolicySelector rejects bad configurations."""
    registry = {"rule": RulePolicy()}
    
    with pytest.raises(PolicyError, match="Default policy 'missing' not registered"):
        PolicySelector(policies=registry, default_policy="missing")  # type: ignore[arg-type]
        
    selector = PolicySelector(policies=registry, default_policy="rule")  # type: ignore[arg-type]
    
    with pytest.raises(PolicyError, match="Cannot select unregistered policy: fake"):
        selector.set_active_policy("fake")
