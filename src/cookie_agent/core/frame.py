"""Frame representation model."""

from dataclasses import dataclass

from cookie_agent.core.types import FrameId, Timestamp


@dataclass(frozen=True, slots=True)
class Frame:
    """Wraps raw screen capture buffer.

    Attributes:
        frame_id: Monotonically increasing identifier.
        timestamp: Time of frame capture.
        width: Width of the frame in pixels.
        height: Height of the frame in pixels.
        data: Raw pixel matrix/buffer.
    """

    frame_id: FrameId
    timestamp: Timestamp
    width: int
    height: int
    data: bytes

    @property
    def resolution(self) -> tuple[int, int]:
        """Exposes the frame's dimensions as a (width, height) tuple."""
        return self.width, self.height
