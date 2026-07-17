"""Base capture source interface."""

from abc import ABC, abstractmethod

from cookie_agent.core.frame import Frame


class BaseCaptureSource(ABC):
    """Abstract base class for capture source implementations."""

    @abstractmethod
    def capture(self) -> Frame:
        """Capture a single frame from the target source.

        Returns:
            Frame: The captured Frame.
            Raises exception on failure.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the capture source and release underlying system resources."""
        pass
