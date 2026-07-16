"""Configuration version definition."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfigurationVersion:
    """Semantic versioning schema for configuration objects."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        """Return the string representation of the version."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def current(cls) -> "ConfigurationVersion":
        """Get the current configuration schema version."""
        return cls(major=1, minor=0, patch=0)
