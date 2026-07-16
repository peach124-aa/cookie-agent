"""Detection representation models."""

from dataclasses import dataclass
from enum import StrEnum, auto

from cookie_agent.core.types import Confidence, FrameId, LaneIndex, Timestamp


class DetectionClass(StrEnum):
    """Categories of detected game objects."""

    COOKIE = auto()
    OBSTACLE_GROUND = auto()
    OBSTACLE_AIR = auto()
    JELLY = auto()
    COIN = auto()
    POTION = auto()


@dataclass(frozen=True, slots=True)
class BBox:
    """Two-dimensional bounding region on the screen coordinate plane.

    Attributes:
        xmin: Minimum X coordinate.
        ymin: Minimum Y coordinate.
        xmax: Maximum X coordinate.
        ymax: Maximum Y coordinate.
    """

    xmin: int
    ymin: int
    xmax: int
    ymax: int

    @property
    def width(self) -> int:
        """Calculates the width of the bounding box."""
        return self.xmax - self.xmin

    @property
    def height(self) -> int:
        """Calculates the height of the bounding box."""
        return self.ymax - self.ymin

    @property
    def area(self) -> int:
        """Calculates the surface area of the bounding box."""
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        """Calculates the center of the bounding box as a (x, y) float tuple."""
        return (self.xmin + self.xmax) / 2.0, (self.ymin + self.ymax) / 2.0


@dataclass(frozen=True, slots=True)
class Detection:
    """Raw prediction representing a single detected object in a frame.

    Attributes:
        frame_id: Identifier of the frame.
        timestamp: Time of detection.
        class_name: Classified class category.
        bbox: Spatial bounding boundaries.
        confidence: Inference probability score.
        lane: Optional lane placement index.
        detector_name: Label of detector instance.
    """

    frame_id: FrameId
    timestamp: Timestamp
    class_name: DetectionClass
    bbox: BBox
    confidence: Confidence
    lane: LaneIndex | None = None
    detector_name: str = "default"

    @property
    def center(self) -> tuple[float, float]:
        """Exposes the spatial center of the detection bbox as a (x, y) tuple."""
        return self.bbox.center
