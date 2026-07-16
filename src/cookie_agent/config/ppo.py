"""PPO algorithm configuration."""

from dataclasses import dataclass

from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_positive, validate_range


@dataclass(frozen=True, slots=True)
class PPOConfig(BaseConfig):
    """Mathematical limits and clipping factors for PPO."""

    gamma: float
    lambda_gae: float
    clip_ratio: float
    value_coeff: float
    entropy_coeff: float

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_range("gamma", self.gamma, 0.0, 1.0)
        validate_range("lambda_gae", self.lambda_gae, 0.0, 1.0)
        validate_positive("clip_ratio", self.clip_ratio)
        validate_positive("value_coeff", self.value_coeff)
        validate_positive("entropy_coeff", self.entropy_coeff)

    @classmethod
    def default(cls) -> "PPOConfig":
        """Return default configuration."""
        return cls(
            gamma=0.99,
            lambda_gae=0.95,
            clip_ratio=0.2,
            value_coeff=0.5,
            entropy_coeff=0.01,
        )
