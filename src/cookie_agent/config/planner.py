"""Action planner configuration."""

from dataclasses import dataclass
from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_non_negative

@dataclass(frozen=True, slots=True)
class PlannerConfig(BaseConfig):
    """Configuration for mapping intents to device inputs."""

    tap_hold_ms: int
    delay_between_commands_ms: int

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_non_negative("tap_hold_ms", self.tap_hold_ms)
        validate_non_negative("delay_between_commands_ms", self.delay_between_commands_ms)

    @classmethod
    def default(cls) -> "PlannerConfig":
        return cls(
            tap_hold_ms=50,
            delay_between_commands_ms=0
        )
