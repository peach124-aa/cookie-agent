"""Unit tests for the Reward Engine module in pure Python."""

from typing import cast

from cookie_agent.core.protocols import RewardStrategy
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState, JumpPhase, PlayerState
from cookie_agent.core.types import StepId
from cookie_agent.reward import RewardEngine
from cookie_agent.reward.rule import RewardRule


class DistanceRule:
    """Mock rule giving positive reward for distance scrolled."""

    def evaluate(
        self, previous_state: GameState, current_state: GameState
    ) -> RewardEvent | None:
        """Mock evaluate."""
        delta = current_state.scroll_distance - previous_state.scroll_distance
        if delta > 0:
            return RewardEvent(value=delta * 0.1, event_type="DISTANCE")
        return None


class DamageRule:
    """Mock rule giving negative reward for taking damage."""

    def evaluate(
        self, previous_state: GameState, current_state: GameState
    ) -> RewardEvent | None:
        """Mock evaluate."""
        if (
            current_state.player.time_since_last_damage == 0.0
            and previous_state.player.time_since_last_damage > 0
        ):
            return RewardEvent(value=-10.0, event_type="DAMAGE")
        return None


def _create_mock_state(
    scroll_distance: float = 0.0, time_since_last_damage: float = 5.0
) -> GameState:
    player = PlayerState(
        velocity_x=0.0,
        velocity_y=0.0,
        jump_phase=JumpPhase.GROUNDED,
        airborne=False,
        grounded=True,
        time_since_last_jump=1.0,
        time_since_last_damage=time_since_last_damage,
        relay_available=True,
    )
    return GameState(
        schema_version=1,
        player=player,
        objects=[],
        scroll_speed=100.0,
        scroll_distance=scroll_distance,
        step_id=cast(StepId, 1),
    )


def test_engine_protocol_conformance() -> None:
    """Verify RewardEngine conforms to RewardStrategy protocol."""
    engine = RewardEngine()
    assert isinstance(engine, RewardStrategy)


def test_rule_protocol_conformance() -> None:
    """Verify mock rules conform to RewardRule protocol."""
    rule = DistanceRule()
    assert isinstance(rule, RewardRule)


def test_empty_transitions() -> None:
    """Verify neutral reward when no rules trigger."""
    engine = RewardEngine([DistanceRule(), DamageRule()])

    state1 = _create_mock_state(scroll_distance=100.0, time_since_last_damage=1.0)
    state2 = _create_mock_state(scroll_distance=100.0, time_since_last_damage=1.1)

    event = engine.calculate(state1, state2)

    assert event.value == 0.0
    assert event.event_type == "NONE"


def test_positive_rewards() -> None:
    """Verify positive rewards are emitted when triggered."""
    engine = RewardEngine([DistanceRule(), DamageRule()])

    state1 = _create_mock_state(scroll_distance=100.0, time_since_last_damage=1.0)
    state2 = _create_mock_state(scroll_distance=200.0, time_since_last_damage=1.1)

    event = engine.calculate(state1, state2)

    assert event.value == 10.0  # (200 - 100) * 0.1
    assert event.event_type == "DISTANCE"


def test_negative_rewards() -> None:
    """Verify negative rewards are emitted when triggered."""
    engine = RewardEngine([DistanceRule(), DamageRule()])

    state1 = _create_mock_state(scroll_distance=100.0, time_since_last_damage=1.0)
    state2 = _create_mock_state(scroll_distance=100.0, time_since_last_damage=0.0)

    event = engine.calculate(state1, state2)

    assert event.value == -10.0
    assert event.event_type == "DAMAGE"


def test_multiple_reward_aggregation() -> None:
    """Verify multiple events are aggregated correctly."""
    engine = RewardEngine()
    engine.add_rule(DistanceRule())
    engine.add_rule(DamageRule())

    state1 = _create_mock_state(scroll_distance=100.0, time_since_last_damage=1.0)
    state2 = _create_mock_state(scroll_distance=200.0, time_since_last_damage=0.0)

    event = engine.calculate(state1, state2)

    # Distance (+10.0) + Damage (-10.0) = 0.0
    assert event.value == 0.0
    assert event.event_type == "DISTANCE|DAMAGE"
