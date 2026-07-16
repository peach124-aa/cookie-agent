"""Object tracker implementing core Tracker protocol."""

from collections.abc import Sequence
from typing import cast

from cookie_agent.core.detection import Detection
from cookie_agent.core.protocols import Tracker
from cookie_agent.core.tracking import TrackedObject, TrackStatus
from cookie_agent.core.types import Timestamp, TrackId
from cookie_agent.tracker.assignment import greedy_assignment
from cookie_agent.tracker.filtering import LifecycleManager


class ObjectTracker(Tracker):
    """Links object identifiers across consecutive frame instances."""

    def __init__(self, max_distance: float = 100.0, max_occluded_frames: int = 15):
        """Initialize the ObjectTracker.

        Args:
            max_distance: Maximum distance for greedy assignment matching.
            max_occluded_frames: Frames before dropping an occluded track.
        """
        self.max_distance = max_distance
        self.lifecycle = LifecycleManager(max_occluded_frames=max_occluded_frames)
        self.tracks: list[TrackedObject] = []
        self.next_object_id: int = 1
        self.last_timestamp: Timestamp | None = None

    def track(self, detections: Sequence[Detection]) -> Sequence[TrackedObject]:
        """Link object coordinates across times steps.

        Args:
            detections: List of raw predictions from the current frame.

        Returns:
            List of tracked entities.
        """
        if not detections:
            # Update all active tracks to occluded
            for track in self.tracks:
                self.lifecycle.update_unmatched(track)
            self.tracks = self.lifecycle.filter_active_tracks(self.tracks)
            return self.tracks

        current_timestamp = detections[0].timestamp
        time_delta = 0.0
        if self.last_timestamp is not None:
            time_delta = current_timestamp - self.last_timestamp
            if time_delta <= 0:
                time_delta = 1 / 30.0  # Fallback to 30fps if timestamps are identical
        else:
            time_delta = 1 / 30.0

        self.last_timestamp = current_timestamp

        # Perform assignment
        det_list = list(detections)
        matched_indices, unmatched_detections, unmatched_tracks = greedy_assignment(
            det_list, self.tracks, max_distance=self.max_distance
        )

        # Update matched tracks
        for d_idx, t_idx in matched_indices:
            det = det_list[d_idx]
            track = self.tracks[t_idx]

            # Calculate velocity
            dx = det.center[0] - track.bbox.center[0]
            dy = det.center[1] - track.bbox.center[1]
            track.velocity_x = dx / time_delta
            track.velocity_y = dy / time_delta

            # Update state
            track.bbox = det.bbox
            self.lifecycle.update_matched(track)

        # Update unmatched tracks
        for t_idx in unmatched_tracks:
            track = self.tracks[t_idx]
            self.lifecycle.update_unmatched(track)
            # Retain old velocity, or decay it? We'll retain it for estimation.

        # Create new tracks for unmatched detections
        for d_idx in unmatched_detections:
            det = det_list[d_idx]
            new_track = TrackedObject(
                object_id=cast(TrackId, self.next_object_id),
                class_name=det.class_name,
                bbox=det.bbox,
                velocity_x=0.0,
                velocity_y=0.0,
                status=TrackStatus.ACTIVE,
            )
            self.tracks.append(new_track)
            self.next_object_id += 1

        # Filter out lost/consumed tracks
        self.tracks = self.lifecycle.filter_active_tracks(self.tracks)

        return self.tracks
