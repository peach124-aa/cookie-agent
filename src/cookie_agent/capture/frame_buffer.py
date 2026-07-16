"""Thread-safe bounded frame queue."""

import collections
import threading

from cookie_agent.capture.exceptions import CaptureTimeoutError
from cookie_agent.core.frame import Frame


class FrameBuffer:
    """Bounded thread-safe FIFO queue that drops the oldest frames on overflow."""

    def __init__(self, max_size: int):
        """Initialize frame buffer.

        Args:
            max_size: Maximum capacity of the buffer.

        Raises:
            ValueError: If max_size is <= 0.
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive.")
        self.max_size = max_size
        self._queue: collections.deque[Frame] = collections.deque(maxlen=max_size)
        self._condition = threading.Condition()

    def push(self, frame: Frame) -> None:
        """Push a frame to the buffer. If full, drops the oldest frame.

        Args:
            frame: The Frame object to buffer.
        """
        with self._condition:
            self._queue.append(frame)
            self._condition.notify_all()

    def pop(self, timeout: float | None = None) -> Frame:
        """Pop the oldest frame from the buffer, blocking if empty.

        Args:
            timeout: Optional wait timeout in seconds.

        Returns:
            Frame: The popped Frame.

        Raises:
            CaptureTimeoutError: If the timeout expires before a frame is available.
        """
        with self._condition:
            if not self._queue:
                if not self._condition.wait(timeout=timeout):
                    raise CaptureTimeoutError("Timed out waiting for frame in buffer.")
                if not self._queue:
                    raise CaptureTimeoutError("Timed out waiting for frame in buffer.")
            return self._queue.popleft()

    def clear(self) -> None:
        """Clear all frames in the buffer."""
        with self._condition:
            self._queue.clear()

    def qsize(self) -> int:
        """Get the current size of the buffer.

        Returns:
            int: The number of frames in the queue.
        """
        with self._condition:
            return len(self._queue)
