"""Replay recorder custom exceptions."""


class ReplayError(Exception):
    """Base exception for all replay operations."""


class ReplayWriteError(ReplayError):
    """Raised when serializing replay details fails."""


class ReplayReadError(ReplayError):
    """Raised when parsing or retrieving files fails."""


class ReplayFormatError(ReplayError):
    """Raised when magic header bytes or version compatibility checks fail."""
