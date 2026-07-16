"""Unit tests for the generic Reinforcement Learning experience buffer."""

import pytest

from cookie_agent.rl.buffer import RolloutBuffer
from cookie_agent.rl.exceptions import BufferError
from cookie_agent.rl.experience import Experience, Trajectory
from cookie_agent.rl.sampler import MiniBatchSampler


def create_exp(reward: float, terminated: bool = False) -> Experience[str, str, str]:
    """Helper to create generic experiences for testing."""
    return Experience(
        state="S1",
        action="A1",
        reward=reward,
        next_state="S2",
        terminated=terminated,
        info="I1"
    )


def test_experience_immutability() -> None:
    """Verify Experience dataclass is frozen."""
    exp = create_exp(1.0)
    with pytest.raises(Exception):  # FrozenInstanceError inherits from AttributeError/Exception
        exp.reward = 2.0  # type: ignore


def test_trajectory_metrics() -> None:
    """Verify trajectory total reward and length calculations."""
    exps = [create_exp(1.0), create_exp(-0.5), create_exp(2.0, terminated=True)]
    traj = Trajectory(exps)
    
    assert traj.length() == 3
    assert traj.total_reward() == 2.5
    assert traj.experiences == exps


def test_buffer_append_and_clear() -> None:
    """Verify buffer storage operations."""
    buffer = RolloutBuffer[str, str, str]()
    
    assert len(buffer) == 0
    buffer.append(create_exp(1.0))
    buffer.append(create_exp(2.0))
    
    assert len(buffer) == 2
    
    # Iterate
    exps = list(buffer)
    assert len(exps) == 2
    assert exps[0].reward == 1.0
    
    buffer.clear()
    assert len(buffer) == 0


def test_buffer_episode_splitting() -> None:
    """Verify buffer splits experiences into trajectories by termination flag."""
    buffer = RolloutBuffer[str, str, str]()
    
    # Episode 1
    buffer.append(create_exp(1.0))
    buffer.append(create_exp(1.0, terminated=True))
    
    # Episode 2
    buffer.append(create_exp(2.0))
    buffer.append(create_exp(2.0, terminated=True))
    
    # Episode 3 (Unterminated)
    buffer.append(create_exp(3.0))
    
    episodes = list(buffer.episodes())
    
    assert len(episodes) == 3
    assert episodes[0].length() == 2
    assert episodes[0].total_reward() == 2.0
    
    assert episodes[1].length() == 2
    assert episodes[1].total_reward() == 4.0
    
    assert episodes[2].length() == 1
    assert episodes[2].total_reward() == 3.0


def test_minibatch_sampler() -> None:
    """Verify deterministic minibatch iteration."""
    buffer = RolloutBuffer[str, str, str]()
    for i in range(5):
        buffer.append(create_exp(float(i)))
        
    sampler = MiniBatchSampler(buffer, batch_size=2)
    batches = list(sampler)
    
    assert len(batches) == 3
    assert len(batches[0]) == 2
    assert len(batches[1]) == 2
    assert len(batches[2]) == 1  # Remainder
    
    assert batches[0][0].reward == 0.0
    assert batches[0][1].reward == 1.0


def test_minibatch_sampler_empty() -> None:
    """Verify sampler handles empty buffer gracefully."""
    buffer = RolloutBuffer[str, str, str]()
    sampler = MiniBatchSampler(buffer, batch_size=10)
    batches = list(sampler)
    assert len(batches) == 0


def test_minibatch_sampler_invalid_batch_size() -> None:
    """Verify sampler raises BufferError for invalid sizes."""
    buffer = RolloutBuffer[str, str, str]()
    with pytest.raises(BufferError):
        MiniBatchSampler(buffer, batch_size=0)
