"""Tracker configuration."""

from dataclasses import dataclass

from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_positive


@dataclass(frozen=True, slots=True)
class TrackerConfig(BaseConfig):
    """Configuration for continuous object tracking."""

    max_age: int
    min_hits: int
    distance_threshold: float

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_positive("max_age", self.max_age)
        validate_positive("min_hits", self.min_hits)
        validate_positive("distance_threshold", self.distance_threshold)

    @classmethod
    def default(cls) -> "TrackerConfig":
        """Return default configuration."""
        return cls(max_age=15, min_hits=3, distance_threshold=50.0)
