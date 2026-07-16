"""Evaluation scoring structures."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RewardEvent:
    """Metric rating outcome transitions.

    Attributes:
        value: Evaluation value score.
        event_type: Outcome classification category name.
    """

    value: float
    event_type: str
