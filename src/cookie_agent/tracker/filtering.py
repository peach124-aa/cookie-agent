"""Lifecycle filtering and state management for tracked objects."""

from cookie_agent.core.tracking import TrackedObject, TrackStatus


class LifecycleManager:
    """Manages the status transitions of tracked objects."""

    def __init__(self, max_occluded_frames: int = 15):
        """Initialize the LifecycleManager.

        Args:
            max_occluded_frames: Number of frames an object can remain OCCLUDED before being marked LOST.
        """
        self.max_occluded_frames = max_occluded_frames
        self.occluded_counts: dict[int, int] = {}

    def update_matched(self, track: TrackedObject) -> None:
        """Update a track that was successfully matched to a detection.

        Args:
            track: The TrackedObject to update.
        """
        track.status = TrackStatus.ACTIVE
        if track.object_id in self.occluded_counts:
            del self.occluded_counts[track.object_id]

    def update_unmatched(self, track: TrackedObject) -> None:
        """Update a track that was not matched to any detection.

        Args:
            track: The TrackedObject to update.
        """
        if track.status == TrackStatus.ACTIVE:
            track.status = TrackStatus.OCCLUDED
            self.occluded_counts[track.object_id] = 1
        elif track.status == TrackStatus.OCCLUDED:
            count = self.occluded_counts.get(track.object_id, 0) + 1
            if count > self.max_occluded_frames:
                track.status = TrackStatus.LOST
                del self.occluded_counts[track.object_id]
            else:
                self.occluded_counts[track.object_id] = count

    def mark_consumed(self, track: TrackedObject) -> None:
        """Explicitly mark a track as consumed (e.g. by external policy feedback).

        Args:
            track: The TrackedObject to update.
        """
        track.status = TrackStatus.CONSUMED
        if track.object_id in self.occluded_counts:
            del self.occluded_counts[track.object_id]

    def filter_active_tracks(self, tracks: list[TrackedObject]) -> list[TrackedObject]:
        """Filter out LOST and CONSUMED tracks.

        Args:
            tracks: List of all tracked objects.

        Returns:
            list[TrackedObject]: Only ACTIVE or OCCLUDED tracks.
        """
        return [
            t for t in tracks if t.status in (TrackStatus.ACTIVE, TrackStatus.OCCLUDED)
        ]
