"""Trainer dependency protocols for PPO RL loops."""

from typing import Any, Protocol, runtime_checkable

from cookie_agent.rl.experience import Experience
from cookie_agent.rl.ppo import PPOLossResult
from cookie_agent.rl.types import ActionType, InfoType, StateType


@runtime_checkable
class AgentProtocol(Protocol[StateType, ActionType, InfoType]):
    """Contract for the neural network actor-critic."""

    def evaluate_actions(
        self,
        batch: list[Experience[StateType, ActionType, InfoType]],
    ) -> tuple[list[float], list[float], list[float]]:
        """Evaluate the current policy and value function on a batch of experiences.

        Args:
            batch: A sequence of experiences.

        Returns:
            A tuple containing three equal-length lists:
            - values: The estimated state values.
            - log_probs: The log probabilities of the actions taken.
            - entropies: The entropies of the action distributions.
        """
        ...

    def backward(self, loss_result: PPOLossResult) -> None:
        """Execute the backward pass and gradient computation based on loss scalars.

        Args:
            loss_result: The pure Python loss scalars computed by PPOAlgorithm.
        """
        ...


@runtime_checkable
class OptimizerProtocol(Protocol):
    """Contract for the network optimizer."""

    def zero_grad(self) -> None:
        """Clear existing gradients before backward pass."""
        ...

    def step(self) -> None:
        """Apply the computed gradients to the network parameters."""
        ...


@runtime_checkable
class SchedulerProtocol(Protocol):
    """Contract for learning rate schedulers."""

    def step(self) -> None:
        """Update the learning rate based on epoch progression."""
        ...

    def get_last_lr(self) -> list[float]:
        """Return the last computed learning rate(s).

        Returns:
            A list of learning rates for the parameter groups.
        """
        ...


@runtime_checkable
class CheckpointProtocol(Protocol):
    """Contract for saving and loading training state."""

    def save(self, filepath: str) -> None:
        """Serialize the agent and optimizer state to disk.

        Args:
            filepath: Destination path for the checkpoint.
        """
        ...


@runtime_checkable
class CallbackProtocol(Protocol):
    """Contract for training lifecycle hooks."""

    def on_train_start(self, trainer: Any) -> None:
        """Called once before training begins."""
        ...

    def on_epoch_start(self, epoch: int) -> None:
        """Called at the beginning of each epoch."""
        ...

    def on_batch_start(self, batch_idx: int) -> None:
        """Called before processing a minibatch."""
        ...

    def on_batch_end(self, batch_idx: int, metrics: PPOLossResult) -> None:
        """Called after a minibatch has been processed and optimized."""
        ...

    def on_epoch_end(self, epoch: int, metrics: Any) -> None:
        """Called at the end of an epoch."""
        ...

    def on_train_end(self) -> None:
        """Called once after all epochs have completed."""
        ...
