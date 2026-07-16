"""Public tracker package exports."""

from cookie_agent.tracker.exceptions import TrackerError
from cookie_agent.tracker.tracker import ObjectTracker

__all__: list[str] = [
    "ObjectTracker",
    "TrackerError",
]
