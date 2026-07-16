"""Minibatch samplers for processing rollout buffers."""

from collections.abc import Iterator
from typing import Generic

from cookie_agent.rl.buffer import RolloutBuffer
from cookie_agent.rl.exceptions import BufferError
from cookie_agent.rl.experience import Experience
from cookie_agent.rl.types import ActionType, InfoType, StateType


class MiniBatchSampler(Generic[StateType, ActionType, InfoType]):
    """Iterates through a RolloutBuffer and yields deterministically-sized batches."""

    def __init__(
        self,
        buffer: RolloutBuffer[StateType, ActionType, InfoType],
        batch_size: int,
    ) -> None:
        """Initialize the sampler.

        Args:
            buffer: The RolloutBuffer to sample from.
            batch_size: The number of experiences per batch.

        Raises:
            BufferError: If batch_size is less than 1.
        """
        if batch_size < 1:
            raise BufferError("batch_size must be at least 1.")

        self._buffer = buffer
        self._batch_size = batch_size

    def __iter__(self) -> Iterator[list[Experience[StateType, ActionType, InfoType]]]:
        """Yield deterministic, non-overlapping minibatches.

        Yields:
            A list of generic experiences. The last batch may be smaller than batch_size.
        """
        batch: list[Experience[StateType, ActionType, InfoType]] = []
        for exp in self._buffer:
            batch.append(exp)
            if len(batch) == self._batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch
