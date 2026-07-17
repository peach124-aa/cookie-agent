"""Exceptions for the CLI subsystem."""


class CliError(Exception):
    """Base exception for all CLI-related errors."""


class CliConfigError(CliError):
    """Raised when configuration loading fails."""


class CliCommandError(CliError):
    """Raised when a command fails to execute."""
