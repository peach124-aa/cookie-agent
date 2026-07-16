"""Rollout buffer for collecting RL trajectories."""

from collections.abc import Iterator
from typing import Generic

from cookie_agent.rl.experience import Experience, Trajectory
from cookie_agent.rl.types import ActionType, InfoType, StateType


class RolloutBuffer(Generic[StateType, ActionType, InfoType]):
    """Stores sequential experiences and splits them into distinct trajectories."""

    def __init__(self) -> None:
        """Initialize an empty rollout buffer."""
        self._buffer: list[Experience[StateType, ActionType, InfoType]] = []

    def append(self, experience: Experience[StateType, ActionType, InfoType]) -> None:
        """Append a new experience to the buffer.

        Args:
            experience: The generic transition record.
        """
        self._buffer.append(experience)

    def clear(self) -> None:
        """Empty the buffer."""
        self._buffer.clear()

    def __len__(self) -> int:
        """Get the total number of stored experiences.

        Returns:
            The number of records.
        """
        return len(self._buffer)

    def __iter__(self) -> Iterator[Experience[StateType, ActionType, InfoType]]:
        """Iterate over the experiences in insertion order.

        Returns:
            An iterator over the buffer.
        """
        return iter(self._buffer)

    def episodes(self) -> Iterator[Trajectory[StateType, ActionType, InfoType]]:
        """Yield full trajectories based on termination flags.

        If the buffer doesn't end on a termination flag, the remaining
        experiences form the final trajectory.

        Yields:
            Contiguous Trajectory instances.
        """
        current_episode: list[Experience[StateType, ActionType, InfoType]] = []
        for exp in self._buffer:
            current_episode.append(exp)
            if exp.terminated:
                yield Trajectory(current_episode)
                current_episode = []

        if current_episode:
            yield Trajectory(current_episode)
