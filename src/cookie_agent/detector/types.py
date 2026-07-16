"""Local detection models representing raw model outputs."""

from dataclasses import dataclass

from cookie_agent.core.detection import BBox


@dataclass(frozen=True, slots=True)
class Detection:
    """Local object detection prediction.

    Attributes:
        class_id: Numerical category classification ID.
        class_name: Classified label category name.
        confidence: Object prediction confidence score.
        bbox: Bounding box target on screen coordinate plane.
        track_id: Optional persistent identifier tracking index.
    """

    class_id: int
    class_name: str
    confidence: float
    bbox: BBox
    track_id: int | None = None
