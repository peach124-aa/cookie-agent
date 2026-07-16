"""Capture system configuration."""

from dataclasses import dataclass

from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_non_empty, validate_positive


@dataclass(frozen=True, slots=True)
class CaptureConfig(BaseConfig):
    """Configuration for device capture streams."""

    backend: str
    target_fps: int
    queue_size: int

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_non_empty("backend", self.backend)
        validate_positive("target_fps", self.target_fps)
        validate_positive("queue_size", self.queue_size)

    @classmethod
    def default(cls) -> "CaptureConfig":
        """Return default configuration."""
        return cls(backend="windows", target_fps=60, queue_size=5)
