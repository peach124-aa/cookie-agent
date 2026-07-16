"""Base capture source interface."""

from abc import ABC, abstractmethod

from cookie_agent.core.frame import Frame


class BaseCaptureSource(ABC):
    """Abstract base class for capture source implementations."""

    @abstractmethod
    def capture(self) -> Frame | None:
        """Capture a single frame from the target source.

        Returns:
            Frame | None: The captured Frame, or None if unsuccessful.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the capture source and release underlying system resources."""
        pass
