"""Environment specific exceptions."""


class EnvironmentError(Exception):
    """Base exception for all Environment module errors."""


class CaptureTimeoutError(EnvironmentError):
    """Raised when the environment fails to capture a frame in time."""
