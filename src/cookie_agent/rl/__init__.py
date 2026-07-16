"""Public Reinforcement Learning package exports."""

from cookie_agent.rl.buffer import RolloutBuffer
from cookie_agent.rl.exceptions import BufferError, RLError
from cookie_agent.rl.experience import Experience, Trajectory
from cookie_agent.rl.ppo import PPOAlgorithm, PPOLossResult
from cookie_agent.rl.protocols import (
    AgentProtocol,
    CallbackProtocol,
    CheckpointProtocol,
    OptimizerProtocol,
    SchedulerProtocol,
)
from cookie_agent.rl.sampler import MiniBatchSampler
from cookie_agent.rl.trainer import PPOTrainer
from cookie_agent.rl.trainer_metrics import EpochMetrics, TrainMetrics

__all__: list[str] = [
    "Experience",
    "Trajectory",
    "RolloutBuffer",
    "MiniBatchSampler",
    "RLError",
    "BufferError",
    "PPOAlgorithm",
    "PPOLossResult",
    "PPOTrainer",
    "EpochMetrics",
    "TrainMetrics",
    "AgentProtocol",
    "CallbackProtocol",
    "CheckpointProtocol",
    "OptimizerProtocol",
    "SchedulerProtocol",
]
