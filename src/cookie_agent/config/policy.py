"""Policy configuration."""

from dataclasses import dataclass
from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_non_empty

@dataclass(frozen=True, slots=True)
class PolicyConfig(BaseConfig):
    """Configuration for decision-making boundaries."""

    active_policy: str
    rule_jump_threshold_x: float

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_non_empty("active_policy", self.active_policy)

    @classmethod
    def default(cls) -> "PolicyConfig":
        return cls(
            active_policy="rule",
            rule_jump_threshold_x=20.0
        )
