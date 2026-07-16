"""Base configuration module."""

import json
from dataclasses import dataclass
from typing import Any, TypeVar

from cookie_agent.config.serializer import deserialize_from_dict, serialize_to_dict

T = TypeVar("T", bound="BaseConfig")


@dataclass(frozen=True)
class BaseConfig:
    """Immutable base configuration class.

    Provides standard library JSON serialization boundaries.
    """

    @classmethod
    def default(cls: type[T]) -> T:
        """Create a default instance of the configuration.

        Must be implemented by all subclasses.
        """
        raise NotImplementedError("Subclasses must implement default()")

    def to_dict(self) -> dict[str, Any]:
        """Serialize configuration to a primitive dictionary."""
        return serialize_to_dict(self)

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Instantiate configuration from a nested dictionary."""
        return deserialize_from_dict(cls, data)

    def to_json(self) -> str:
        """Serialize configuration to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls: type[T], json_str: str) -> T:
        """Instantiate configuration from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
