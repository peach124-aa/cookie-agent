"""Public capture classes, buffer, and exceptions."""

from cookie_agent.capture.base import BaseCaptureSource
from cookie_agent.capture.exceptions import (
    CaptureError,
    CaptureTimeoutError,
    WindowNotFoundError,
)
from cookie_agent.capture.frame_buffer import FrameBuffer
from cookie_agent.capture.windows_capture import WindowsCapture

__all__: list[str] = [
    "BaseCaptureSource",
    "WindowsCapture",
    "FrameBuffer",
    "CaptureError",
    "WindowNotFoundError",
    "CaptureTimeoutError",
]
