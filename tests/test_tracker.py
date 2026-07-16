"""Unit tests for Tracker module in pure Python."""

from typing import cast

import pytest
from cookie_agent.core.detection import BBox, Detection, DetectionClass
from cookie_agent.core.protocols import Tracker
from cookie_agent.core.tracking import TrackedObject, TrackStatus
from cookie_agent.core.types import Confidence, FrameId, Timestamp, TrackId
from cookie_agent.tracker import ObjectTracker
from cookie_agent.tracker.assignment import (
    calculate_centroid_distance,
    compute_iou,
    greedy_assignment,
)
from cookie_agent.tracker.filtering import LifecycleManager


def test_calculate_centroid_distance() -> None:
    """Verify centroid distance is calculated correctly."""
    det = Detection(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, 0.0),
        class_name=DetectionClass.COOKIE,
        bbox=BBox(0, 0, 10, 10),
        confidence=cast(Confidence, 1.0),
    )
    track = TrackedObject(
        object_id=cast(TrackId, 1),
        class_name=DetectionClass.COOKIE,
        bbox=BBox(10, 10, 20, 20),
        velocity_x=0.0,
        velocity_y=0.0,
        status=TrackStatus.ACTIVE,
    )
    
    # det center is (5, 5), track center is (15, 15)
    # distance = sqrt(10^2 + 10^2) = 14.142...
    dist = calculate_centroid_distance(det, track)
    assert abs(dist - 14.1421356) < 1e-5


def test_compute_iou() -> None:
    """Verify IoU is calculated correctly."""
    box1 = (0, 0, 10, 10)
    box2 = (5, 5, 15, 15)
    iou = compute_iou(box1, box2)
    # intersection = 5 * 5 = 25
    # union = 100 + 100 - 25 = 175
    # iou = 25 / 175 = 0.142857...
    assert abs(iou - 0.142857) < 1e-5


def test_greedy_assignment() -> None:
    """Verify greedy assignment logic."""
    det1 = Detection(cast(FrameId, 1), cast(Timestamp, 0.0), DetectionClass.COOKIE, BBox(0, 0, 10, 10), cast(Confidence, 1.0))
    det2 = Detection(cast(FrameId, 1), cast(Timestamp, 0.0), DetectionClass.JELLY, BBox(100, 100, 110, 110), cast(Confidence, 1.0))
    
    track1 = TrackedObject(cast(TrackId, 1), DetectionClass.COOKIE, BBox(2, 2, 12, 12), 0.0, 0.0, TrackStatus.ACTIVE)
    track2 = TrackedObject(cast(TrackId, 2), DetectionClass.JELLY, BBox(90, 90, 100, 100), 0.0, 0.0, TrackStatus.ACTIVE)
    
    detections = [det1, det2]
    tracks = [track1, track2]
    
    matched, unmatched_d, unmatched_t = greedy_assignment(detections, tracks, max_distance=50.0)
    
    # Cookie det1 -> track1
    # Jelly det2 -> track2
    assert len(matched) == 2
    assert (0, 0) in matched
    assert (1, 1) in matched
    assert unmatched_d == []
    assert unmatched_t == []


def test_greedy_assignment_max_distance() -> None:
    """Verify assignment respects max distance."""
    det = Detection(cast(FrameId, 1), cast(Timestamp, 0.0), DetectionClass.COOKIE, BBox(0, 0, 10, 10), cast(Confidence, 1.0))
    track = TrackedObject(cast(TrackId, 1), DetectionClass.COOKIE, BBox(100, 100, 110, 110), 0.0, 0.0, TrackStatus.ACTIVE)
    
    matched, unmatched_d, unmatched_t = greedy_assignment([det], [track], max_distance=10.0)
    assert len(matched) == 0
    assert unmatched_d == [0]
    assert unmatched_t == [0]


def test_lifecycle_manager() -> None:
    """Verify state transitions in lifecycle manager."""
    lm = LifecycleManager(max_occluded_frames=2)
    track = TrackedObject(cast(TrackId, 1), DetectionClass.COOKIE, BBox(0, 0, 10, 10), 0.0, 0.0, TrackStatus.ACTIVE)
    
    # Unmatched -> OCCLUDED
    lm.update_unmatched(track)
    assert track.status == TrackStatus.OCCLUDED
    assert lm.occluded_counts[1] == 1
    
    # Unmatched again -> count 2
    lm.update_unmatched(track)
    assert str(track.status) == str(TrackStatus.OCCLUDED)
    assert lm.occluded_counts[1] == 2
    
    # Unmatched again -> > max -> LOST
    lm.update_unmatched(track)
    assert str(track.status) == str(TrackStatus.LOST)
    assert 1 not in lm.occluded_counts
    
    # Matched -> ACTIVE
    track.status = TrackStatus.OCCLUDED
    lm.occluded_counts[1] = 1
    lm.update_matched(track)
    assert str(track.status) == str(TrackStatus.ACTIVE)
    assert 1 not in lm.occluded_counts


def test_tracker_protocol_conformance() -> None:
    """Verify ObjectTracker conforms to Tracker protocol."""
    tracker = ObjectTracker()
    assert isinstance(tracker, Tracker)


def test_object_tracker_logic() -> None:
    """Verify full tracking logic across frames."""
    tracker = ObjectTracker(max_distance=50.0, max_occluded_frames=2)
    
    # Frame 1: 1 Cookie, 1 Jelly
    det1 = Detection(cast(FrameId, 1), cast(Timestamp, 1.0), DetectionClass.COOKIE, BBox(0, 0, 10, 10), cast(Confidence, 1.0))
    det2 = Detection(cast(FrameId, 1), cast(Timestamp, 1.0), DetectionClass.JELLY, BBox(50, 50, 60, 60), cast(Confidence, 1.0))
    
    tracks_f1 = tracker.track([det1, det2])
    assert len(tracks_f1) == 2
    assert tracks_f1[0].object_id == 1
    assert tracks_f1[1].object_id == 2
    
    # Frame 2: Cookie moves, Jelly disappears
    # Time delta = 0.1s
    det3 = Detection(cast(FrameId, 2), cast(Timestamp, 1.1), DetectionClass.COOKIE, BBox(10, 0, 20, 10), cast(Confidence, 1.0))
    
    tracks_f2 = tracker.track([det3])
    # Cookie should be ACTIVE, Jelly should be OCCLUDED
    assert len(tracks_f2) == 2
    
    cookie_track = next(t for t in tracks_f2 if t.class_name == DetectionClass.COOKIE)
    jelly_track = next(t for t in tracks_f2 if t.class_name == DetectionClass.JELLY)
    
    assert cookie_track.status == TrackStatus.ACTIVE
    # Velocity x: dx = 10, dt = 0.1 -> vx = 100
    assert abs(cookie_track.velocity_x - 100.0) < 1e-5
    
    assert jelly_track.status == TrackStatus.OCCLUDED
    
    # Frame 3: Empty
    tracks_f3 = tracker.track([])
    assert len(tracks_f3) == 2
    assert tracks_f3[0].status == TrackStatus.OCCLUDED
    assert tracks_f3[1].status == TrackStatus.OCCLUDED
    
    # Frame 4: Empty (Jelly should be lost since it was occluded for F2, F3, F4? Wait: F2=count 1, F3=count 2, F4=count 3 > 2 => LOST)
    tracks_f4 = tracker.track([])
    assert len(tracks_f4) == 1
    assert tracks_f4[0].class_name == DetectionClass.COOKIE
    assert tracks_f4[0].status == TrackStatus.OCCLUDED
