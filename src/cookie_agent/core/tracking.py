"""Object tracking representations."""

from dataclasses import dataclass
from enum import StrEnum, auto

from cookie_agent.core.detection import BBox, DetectionClass
from cookie_agent.core.types import TrackId


class TrackStatus(StrEnum):
    """Lifecycle tracking states of an entity."""

    ACTIVE = auto()
    OCCLUDED = auto()
    CONSUMED = auto()
    LOST = auto()


@dataclass(slots=True)
class TrackedObject:
    """Entity followed continuously over consecutive frames.

    Attributes:
        object_id: Unique identification tag.
        class_name: Classified class category.
        bbox: Last known spatial boundaries.
        velocity_x: Estimated velocity on X-axis (pixels/sec).
        velocity_y: Estimated velocity on Y-axis (pixels/sec).
        status: Current tracking lifecycle state.
    """

    object_id: TrackId
    class_name: DetectionClass
    bbox: BBox
    velocity_x: float
    velocity_y: float
    status: TrackStatus
