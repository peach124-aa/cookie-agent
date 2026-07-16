"""Reward configuration."""

from dataclasses import dataclass

from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_non_empty


@dataclass(frozen=True, slots=True)
class RewardConfig(BaseConfig):
    """Scoring rules and engine parameters."""

    strategy: str
    survival_points_per_frame: float
    jelly_points: float
    obstacle_penalty: float

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_non_empty("strategy", self.strategy)

    @classmethod
    def default(cls) -> "RewardConfig":
        """Return default configuration."""
        return cls(
            strategy="survival",
            survival_points_per_frame=0.1,
            jelly_points=1.0,
            obstacle_penalty=-10.0,
        )
