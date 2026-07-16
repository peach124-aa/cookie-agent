"""Exceptions for the configuration module."""


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class ValidationError(ConfigError):
    """Raised when configuration values fail validation constraints."""

    pass


class SerializationError(ConfigError):
    """Raised when configuration fails to serialize or deserialize."""

    pass


class MergeError(ConfigError):
    """Raised when configuration dictionaries fail to merge."""

    pass
