"""Experience and Trajectory containers for RL pipelines."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Experience[StateType, ActionType, InfoType]:
    """An immutable, generic record of a single step transition.

    Attributes:
        state: The environment state prior to the action.
        action: The action executed by the agent.
        reward: The scalar feedback received.
        next_state: The environment state resulting from the action.
        terminated: Whether the episode finished after this transition.
        info: Additional metadata or debugging information.
    """

    state: StateType
    action: ActionType
    reward: float
    next_state: StateType
    terminated: bool
    info: InfoType


class Trajectory[StateType, ActionType, InfoType]:
    """A contiguous sequence of experiences representing a single episode."""

    def __init__(
        self, experiences: list[Experience[StateType, ActionType, InfoType]]
    ) -> None:
        """Initialize the Trajectory.

        Args:
            experiences: A list of chronologically ordered experiences.
        """
        self._experiences = experiences

    def total_reward(self) -> float:
        """Calculate the undiscounted sum of rewards in this trajectory.

        Returns:
            The total scalar reward.
        """
        return sum(exp.reward for exp in self._experiences)

    def length(self) -> int:
        """Get the number of experiences in this trajectory.

        Returns:
            The length of the trajectory.
        """
        return len(self._experiences)

    @property
    def experiences(self) -> list[Experience[StateType, ActionType, InfoType]]:
        """Access the underlying experiences list.

        Returns:
            The list of experiences.
        """
        return self._experiences
