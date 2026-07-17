"""Protocols for the Evaluation subsystem."""

from typing import Protocol, runtime_checkable

from cookie_agent.core.actions import ActionIntent
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState
from cookie_agent.environment.info import StepInfo


@runtime_checkable
class EnvironmentProtocol(Protocol):
    """Contract for the environment in the evaluation layer."""

    def reset(self) -> GameState:
        """Reset the environment to its initial state."""
        ...

    def step(
        self, action: ActionIntent
    ) -> tuple[GameState, RewardEvent, bool, StepInfo]:
        """Execute the next state transition."""
        ...


@runtime_checkable
class PolicyProtocol(Protocol):
    """Contract for the policy in the evaluation layer."""

    def select_action(self, state: GameState) -> ActionIntent:
        """Select an action based on the current state."""
        ...
