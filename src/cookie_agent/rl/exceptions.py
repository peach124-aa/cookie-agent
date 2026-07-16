"""Reinforcement Learning module exceptions."""


class RLError(Exception):
    """Base exception for RL-related errors."""


class ReplayBufferError(RLError):
    """Raised when an operation on the RolloutBuffer or Sampler is invalid."""
