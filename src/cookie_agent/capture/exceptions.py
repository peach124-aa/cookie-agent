"""Capture-specific exceptions."""


class CaptureError(Exception):
    """Base exception for capture errors."""


class WindowNotFoundError(CaptureError):
    """Raised when target window is not found."""


class CaptureTimeoutError(CaptureError):
    """Raised when frame capture or buffer read times out."""
