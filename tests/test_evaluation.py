"""Unit tests for the Evaluation System."""

from unittest.mock import MagicMock

import pytest
from cookie_agent.core.actions import ActionIntent
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState
from cookie_agent.environment.info import StepInfo
from cookie_agent.evaluation.metrics import EvaluationMetrics
from cookie_agent.evaluation.protocols import EnvironmentProtocol, PolicyProtocol
from cookie_agent.evaluation.runner import EvaluationRunner


@pytest.fixture()
def dummy_state() -> MagicMock:
    """Fixture to provide a mocked state."""
    return MagicMock(spec=GameState)


@pytest.fixture()
def dummy_action() -> MagicMock:
    """Fixture to provide a mocked action."""
    return MagicMock(spec=ActionIntent)


@pytest.fixture()
def reward_event() -> MagicMock:
    """Fixture to provide a mocked reward event."""
    reward = MagicMock(spec=RewardEvent)
    reward.value = 1.0
    return reward


@pytest.fixture()
def step_info() -> MagicMock:
    """Fixture to provide mocked step info."""
    return MagicMock(spec=StepInfo)


@pytest.fixture()
def mock_environment(
    dummy_state: MagicMock, reward_event: MagicMock, step_info: MagicMock
) -> MagicMock:
    """Mock EnvironmentProtocol."""
    env = MagicMock(spec=EnvironmentProtocol)
    env.reset.return_value = dummy_state

    # 2 steps per episode, reward 1.0 each step
    # First step: not terminated, Second step: terminated
    env.step.side_effect = [
        (dummy_state, reward_event, False, step_info),
        (dummy_state, reward_event, True, step_info),
        (dummy_state, reward_event, False, step_info),
        (dummy_state, reward_event, True, step_info),
    ]
    return env


@pytest.fixture()
def mock_policy(dummy_action: MagicMock) -> MagicMock:
    """Mock PolicyProtocol."""
    policy = MagicMock(spec=PolicyProtocol)
    policy.select_action.return_value = dummy_action
    return policy


def test_evaluation_runner_success(
    mock_environment: MagicMock, mock_policy: MagicMock
) -> None:
    """Test standard evaluation run with multiple episodes."""
    runner = EvaluationRunner(
        environment=mock_environment,
        policy=mock_policy,
        num_episodes=2,
    )

    metrics = runner.evaluate()

    # Assert orchestrator calls
    assert mock_environment.reset.call_count == 2
    assert mock_environment.step.call_count == 4
    assert mock_policy.select_action.call_count == 4

    # Assert metrics
    assert isinstance(metrics, EvaluationMetrics)
    assert metrics.num_episodes == 2
    assert metrics.mean_reward == 2.0  # 2 steps * 1.0 reward per episode
    assert metrics.std_reward == 0.0  # both episodes have exactly 2.0 reward
    assert metrics.mean_length == 2.0  # 2 steps per episode
    assert metrics.total_duration_seconds >= 0.0


def test_evaluation_runner_zero_episodes(
    mock_environment: MagicMock, mock_policy: MagicMock
) -> None:
    """Test evaluation run with zero episodes."""
    runner = EvaluationRunner(
        environment=mock_environment,
        policy=mock_policy,
        num_episodes=0,
    )

    metrics = runner.evaluate()

    # Assert no steps executed
    mock_environment.reset.assert_not_called()
    mock_policy.select_action.assert_not_called()

    # Assert zero metrics
    assert metrics.num_episodes == 0
    assert metrics.mean_reward == 0.0
    assert metrics.std_reward == 0.0
    assert metrics.mean_length == 0.0


def test_evaluation_runner_single_episode(
    mock_environment: MagicMock, mock_policy: MagicMock
) -> None:
    """Test evaluation run with a single episode to verify std_reward computation."""
    runner = EvaluationRunner(
        environment=mock_environment,
        policy=mock_policy,
        num_episodes=1,
    )

    metrics = runner.evaluate()

    assert metrics.num_episodes == 1
    assert metrics.std_reward == 0.0  # standard deviation of 1 element is 0.0


def test_evaluation_runner_bubbles_exceptions(
    mock_environment: MagicMock, mock_policy: MagicMock
) -> None:
    """Test Fail Fast behavior when environment raises an exception."""
    mock_environment.step.side_effect = ValueError("Environment failed")

    runner = EvaluationRunner(
        environment=mock_environment,
        policy=mock_policy,
        num_episodes=1,
    )

    with pytest.raises(ValueError, match="Environment failed"):
        runner.evaluate()


def test_multiple_episode_statistics() -> None:
    """Test mean and standard deviation from multiple episode rewards."""
    rewards = [1.0, 3.0, 5.0]
    lengths = [10, 20, 30]
    duration = 1.5

    metrics = EvaluationMetrics.from_results(rewards, lengths, duration)

    assert metrics.num_episodes == 3
    assert metrics.mean_reward == 3.0
    assert metrics.std_reward == 2.0  # std dev of [1, 3, 5] is 2.0
    assert metrics.mean_length == 20.0
    assert metrics.total_duration_seconds == 1.5


def test_environment_reset_called_every_episode(
    mock_environment: MagicMock, mock_policy: MagicMock
) -> None:
    """Test that environment.reset() is called exactly once per episode."""
    # Run for 5 episodes
    runner = EvaluationRunner(
        environment=mock_environment,
        policy=mock_policy,
        num_episodes=5,
    )

    # We need to provide enough side effects for 5 episodes.
    # Let's say 1 step per episode.
    reward_event = MagicMock(spec=RewardEvent)
    reward_event.value = 1.0
    step_info = MagicMock(spec=StepInfo)
    dummy_state = MagicMock(spec=GameState)

    mock_environment.step.side_effect = [
        (dummy_state, reward_event, True, step_info) for _ in range(5)
    ]

    runner.evaluate()

    assert mock_environment.reset.call_count == 5
