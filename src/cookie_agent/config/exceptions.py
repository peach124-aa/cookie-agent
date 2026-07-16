"""Custom exceptions for configuration loader."""


class ConfigError(Exception):
    """Base exception for all configuration errors."""


class ConfigNotFoundError(ConfigError):
    """Raised when a required configuration file cannot be found."""


class ConfigValidationError(ConfigError):
    """Raised when configuration values violate validation boundaries."""


class ConfigSchemaError(ConfigValidationError):
    """Raised when schema_version is invalid, missing, or incompatible."""
