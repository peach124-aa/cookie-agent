"""Tests for the Training Runner layer."""

from unittest.mock import MagicMock

import pytest
from cookie_agent.core.actions import ActionIntent, IntentType
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState, JumpPhase, PlayerState
from cookie_agent.environment.info import StepInfo
from cookie_agent.rl.buffer import RolloutBuffer
from cookie_agent.training.loop import TrainingLoop
from cookie_agent.training.metrics import EpisodeMetrics
from cookie_agent.training.runner import TrainingRunner


@pytest.fixture()
def dummy_state() -> GameState:
    """Provide a dummy initial state."""
    return GameState(
        schema_version=1,
        player=PlayerState(
            velocity_x=0.0,
            velocity_y=0.0,
            jump_phase=JumpPhase.GROUNDED,
            airborne=False,
            grounded=True,
            time_since_last_jump=0.0,
            time_since_last_damage=0.0,
            relay_available=False,
        ),
        objects=[],
        scroll_speed=100.0,
        scroll_distance=0.0,
    )


@pytest.fixture()
def mock_environment(dummy_state: GameState) -> MagicMock:
    """Mock the environment."""
    env = MagicMock()
    env.reset.return_value = dummy_state
    env.step.return_value = (dummy_state, RewardEvent(1.0, "TEST"), True, MagicMock())
    return env


@pytest.fixture()
def mock_policy() -> MagicMock:
    """Mock the policy."""
    policy = MagicMock()
    policy.select_action.return_value = ActionIntent(IntentType.JUMP)
    return policy


@pytest.fixture()
def mock_trainer() -> MagicMock:
    """Mock the PPO trainer."""
    return MagicMock()


@pytest.fixture()
def runner(
    mock_environment: MagicMock,
    mock_policy: MagicMock,
    mock_trainer: MagicMock,
) -> TrainingRunner:
    """Fixture for TrainingRunner."""
    buffer: RolloutBuffer[GameState, ActionIntent, StepInfo] = RolloutBuffer()
    return TrainingRunner(
        environment=mock_environment,
        policy=mock_policy,
        buffer=buffer,
        trainer=mock_trainer,
        target_buffer_size=2,
        ppo_epochs=3,
        ppo_batch_size=32,
    )


def test_successful_episode(
    runner: TrainingRunner, mock_environment: MagicMock, mock_policy: MagicMock
) -> None:
    """Test a successful single episode execution."""
    metrics = runner.run_episode()

    mock_environment.reset.assert_called_once()
    mock_policy.select_action.assert_called_once()
    mock_environment.step.assert_called_once()

    assert metrics.episode == 1
    assert metrics.episode_reward == 1.0
    assert metrics.episode_length == 1
    assert len(runner._buffer) == 1
    assert runner._update_count == 0


def test_update_called_when_buffer_ready(
    runner: TrainingRunner, mock_trainer: MagicMock
) -> None:
    """Test that PPOTrainer is called and buffer is cleared when ready."""
    # First episode: buffer size = 1 (target is 2)
    runner.run_episode()
    mock_trainer.train.assert_not_called()
    assert len(runner._buffer) == 1

    # Second episode: buffer size reaches 2, update should trigger
    runner.run_episode()
    mock_trainer.train.assert_called_once_with(
        epochs=3,
        buffer=runner._buffer,
        batch_size=32,
    )
    # Buffer should be cleared
    assert len(runner._buffer) == 0
    assert runner._update_count == 1


def test_environment_reset_failure(
    runner: TrainingRunner, mock_environment: MagicMock
) -> None:
    """Test fail fast on environment reset exception."""
    mock_environment.reset.side_effect = RuntimeError("Reset failed")
    with pytest.raises(RuntimeError, match="Reset failed"):
        runner.run_episode()


def test_environment_step_failure(
    runner: TrainingRunner, mock_environment: MagicMock
) -> None:
    """Test fail fast on environment step exception."""
    mock_environment.step.side_effect = RuntimeError("Step failed")
    with pytest.raises(RuntimeError, match="Step failed"):
        runner.run_episode()


def test_trainer_update_failure(
    runner: TrainingRunner, mock_trainer: MagicMock
) -> None:
    """Test fail fast on trainer update exception."""
    # Trigger update on first step
    runner._target_buffer_size = 1
    mock_trainer.train.side_effect = RuntimeError("Train failed")
    with pytest.raises(RuntimeError, match="Train failed"):
        runner.run_episode()


def test_loop_multiple_episodes(runner: TrainingRunner) -> None:
    """Test TrainingLoop running multiple episodes and tracking metrics."""
    loop = TrainingLoop(runner)
    metrics = loop.run(total_episodes=3)

    assert metrics.total_episodes == 3
    assert metrics.total_steps == 3
    assert metrics.best_reward == 1.0
    assert metrics.average_reward == 1.0
    # Buffer should have updated once (2 episodes = 1 update, 1 remaining in buffer)
    assert metrics.total_updates == 1


def test_clean_shutdown(runner: TrainingRunner) -> None:
    """Test TrainingLoop clean shutdown on KeyboardInterrupt."""
    loop = TrainingLoop(runner)

    original_run_episode = runner.run_episode

    def mock_run_episode() -> EpisodeMetrics:
        if runner._episode_count >= 1:
            raise KeyboardInterrupt
        return original_run_episode()

    object.__setattr__(runner, "run_episode", mock_run_episode)

    metrics = loop.run(total_episodes=5)

    # Only 1 episode completed before interrupt
    assert metrics.total_episodes == 5  # Requested total
    assert metrics.total_steps == 1
    assert runner._episode_count == 1
