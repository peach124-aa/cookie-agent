"""Generic configuration file loader."""

from pathlib import Path
from typing import Any, TypeVar

from cookie_agent.config.base import BaseConfig
from cookie_agent.config.exceptions import ConfigError

T = TypeVar("T", bound=BaseConfig)


def load_from_dict(cls: type[T], data: dict[str, Any]) -> T:
    """Load configuration from a raw dictionary."""
    try:
        return cls.from_dict(data)
    except Exception as e:
        raise ConfigError(f"Failed to load {cls.__name__} from dictionary: {e}") from e


def load_from_json(cls: type[T], json_str: str) -> T:
    """Load configuration from a raw JSON string."""
    try:
        return cls.from_json(json_str)
    except Exception as e:
        raise ConfigError(f"Failed to load {cls.__name__} from JSON string: {e}") from e


def load_from_file(cls: type[T], file_path: str | Path) -> T:
    """Load configuration from a JSON file."""
    path = Path(file_path)
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            content = f.read()
        return load_from_json(cls, content)
    except Exception as e:
        raise ConfigError(f"Failed to read configuration file {path}: {e}") from e
