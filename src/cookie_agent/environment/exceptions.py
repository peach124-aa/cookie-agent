"""Environment specific exceptions."""


class AgentEnvironmentError(Exception):
    """Base exception for all environment-related errors."""


class CaptureTimeoutError(AgentEnvironmentError):
    """Raised when the environment fails to capture a frame in time."""
