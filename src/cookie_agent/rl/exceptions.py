"""Reinforcement Learning module exceptions."""


class RLError(Exception):
    """Base exception for RL-related errors."""


class BufferError(RLError):
    """Raised when an operation on the RolloutBuffer or Sampler is invalid."""
