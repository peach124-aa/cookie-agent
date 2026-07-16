"""Policy routing selector."""

from typing import Protocol

from cookie_agent.core.actions import ActionIntent
from cookie_agent.core.state import GameState
from cookie_agent.policy.exceptions import PolicyError


class PolicyProtocol(Protocol):
    """Local representation of the Policy protocol to avoid cyclic deps if necessary."""

    def select_action(self, state: GameState) -> ActionIntent:
        ...


class PolicySelector:
    """Routes state evaluation to a dynamically selected policy.

    Allows dynamic swapping between RulePolicy, PPOPolicy, etc.,
    without instantiating singletons.
    """

    def __init__(
        self, policies: dict[str, PolicyProtocol], default_policy: str
    ) -> None:
        """Initialize the selector with a registry of policies.

        Args:
            policies: A mapping of policy names to Policy instances.
            default_policy: The name of the policy to use by default.

        Raises:
            PolicyError: If the default policy is not in the policies dict.
        """
        if default_policy not in policies:
            raise PolicyError(f"Default policy '{default_policy}' not registered.")

        self._policies = policies
        self._active_policy_name = default_policy

    def set_active_policy(self, name: str) -> None:
        """Switch the active policy router.

        Args:
            name: The name of the registered policy.

        Raises:
            PolicyError: If the name is not registered.
        """
        if name not in self._policies:
            raise PolicyError(f"Cannot select unregistered policy: {name}")
        self._active_policy_name = name

    def select_action(self, state: GameState) -> ActionIntent:
        """Delegate action selection to the currently active policy.

        Args:
            state: The unified GameState.

        Returns:
            The chosen ActionIntent.
        """
        active_policy = self._policies[self._active_policy_name]
        return active_policy.select_action(state)
