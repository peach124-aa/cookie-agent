"""PPO adapter policy."""

from typing import Protocol, runtime_checkable

from cookie_agent.core.actions import ActionIntent
from cookie_agent.core.state import GameState
from cookie_agent.policy.exceptions import PolicyError


@runtime_checkable
class PPOAgentProtocol(Protocol):
    """Abstract contract for an underlying ML agent inferencer.

    This keeps the policy layer completely independent of concrete
    implementations like PyTorch, NumPy, or ONNX.
    """

    def predict(self, state: GameState) -> ActionIntent:
        """Infer the optimal action from the current state.

        Args:
            state: The current GameState.

        Returns:
            The selected ActionIntent.

        Raises:
            Exception: Implementations may raise errors if inference fails.
        """
        ...


class PPOPolicy:
    """An adapter that wraps an ML agent to conform to the Policy protocol.

    Delegates action selection strictly to the injected agent.
    """

    def __init__(self, agent: PPOAgentProtocol) -> None:
        """Initialize the PPOPolicy with an abstract ML agent.

        Args:
            agent: An object conforming to PPOAgentProtocol.
        """
        self._agent = agent

    def select_action(self, state: GameState) -> ActionIntent:
        """Select an action using the injected ML agent.

        Args:
            state: The unified GameState.

        Returns:
            The action intent chosen by the PPO agent.

        Raises:
            PolicyError: If the underlying agent fails to predict an action.
        """
        try:
            return self._agent.predict(state)
        except Exception as e:
            raise PolicyError(f"PPO Agent inference failed: {e}") from e
