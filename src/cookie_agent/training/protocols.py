"""Formal communication contracts for the Training orchestration layer."""

from typing import Any, Protocol, runtime_checkable

from cookie_agent.core.actions import ActionIntent
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState
from cookie_agent.environment.info import StepInfo
from cookie_agent.rl.experience import Experience


@runtime_checkable
class EnvironmentProtocol(Protocol):
    """Contract for the environment wrapper."""

    def reset(self) -> GameState:
        """Reset the environment to its initial state."""
        ...

    def step(
        self, action: ActionIntent
    ) -> tuple[GameState, RewardEvent, bool, StepInfo]:
        """Execute a single time step in the environment."""
        ...


@runtime_checkable
class BufferProtocol(Protocol):
    """Contract for the experience rollout buffer."""

    def append(self, experience: Experience[GameState, ActionIntent, StepInfo]) -> None:
        """Add a transition experience to the buffer."""
        ...

    def clear(self) -> None:
        """Clear all stored experiences."""
        ...

    def __len__(self) -> int:
        """Return the number of stored experiences."""
        ...


@runtime_checkable
class TrainerProtocol(Protocol):
    """Contract for the model trainer."""

    def train(self, epochs: int, buffer: Any, batch_size: int) -> Any:
        """Train the model using the collected experiences."""
        ...
