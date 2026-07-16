"""Reward Rule protocol."""

from typing import Protocol, runtime_checkable

from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState


@runtime_checkable
class RewardRule(Protocol):
    """Contract for individual reward evaluation rules."""

    def evaluate(self, previous_state: GameState, current_state: GameState) -> RewardEvent | None:
        """Evaluate a state transition and emit a reward event if applicable.

        Args:
            previous_state: The game state before the transition.
            current_state: The game state after the transition.

        Returns:
            A RewardEvent if the rule triggers, else None.
        """
        ...
