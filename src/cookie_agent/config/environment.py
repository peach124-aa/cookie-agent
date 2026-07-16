"""Environment orchestration configuration."""

from dataclasses import dataclass

from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_positive


@dataclass(frozen=True, slots=True)
class EnvironmentConfig(BaseConfig):
    """Orchestration boundaries for environment mapping."""

    max_steps_per_episode: int
    fps_sync: int

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_positive("max_steps_per_episode", self.max_steps_per_episode)
        validate_positive("fps_sync", self.fps_sync)

    @classmethod
    def default(cls) -> "EnvironmentConfig":
        """Return default configuration."""
        return cls(max_steps_per_episode=10000, fps_sync=60)
