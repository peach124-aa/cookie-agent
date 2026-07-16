"""Assignment logic for matching detections to tracked objects in pure Python."""

import math

from cookie_agent.core.detection import Detection
from cookie_agent.core.tracking import TrackedObject


def calculate_centroid_distance(det: Detection, track: TrackedObject) -> float:
    """Calculate Euclidean distance between centers of detection and tracked object.

    Args:
        det: New detection.
        track: Existing tracked object.

    Returns:
        float: Euclidean distance.
    """
    dx = det.bbox.center[0] - track.bbox.center[0]
    dy = det.bbox.center[1] - track.bbox.center[1]
    return math.sqrt(dx * dx + dy * dy)


def compute_iou(
    box1_coords: tuple[int, int, int, int], box2_coords: tuple[int, int, int, int]
) -> float:
    """Calculate Intersection-over-Union (IoU) of two bounding boxes.

    Args:
        box1_coords: (xmin, ymin, xmax, ymax)
        box2_coords: (xmin, ymin, xmax, ymax)

    Returns:
        float: Calculated IoU ratio.
    """
    x1 = max(box1_coords[0], box2_coords[0])
    y1 = max(box1_coords[1], box2_coords[1])
    x2 = min(box1_coords[2], box2_coords[2])
    y2 = min(box1_coords[3], box2_coords[3])

    intersection = max(0.0, float(x2 - x1)) * max(0.0, float(y2 - y1))
    area1 = float((box1_coords[2] - box1_coords[0]) * (box1_coords[3] - box1_coords[1]))
    area2 = float((box2_coords[2] - box2_coords[0]) * (box2_coords[3] - box2_coords[1]))
    union = area1 + area2 - intersection
    if union == 0.0:
        return 0.0
    return float(intersection / union)


def greedy_assignment(
    detections: list[Detection],
    tracks: list[TrackedObject],
    max_distance: float = 100.0,
) -> tuple[list[tuple[int, int]], list[int], list[int]]:
    """Assign detections to tracks using a greedy algorithm based on distance and class.

    Args:
        detections: List of current detections.
        tracks: List of active/occluded tracked objects.
        max_distance: Maximum allowable distance for an assignment.

    Returns:
        tuple containing:
            - matched_indices: list of (detection_idx, track_idx)
            - unmatched_detections: list of detection_idx
            - unmatched_tracks: list of track_idx
    """
    if not detections:
        return [], [], list(range(len(tracks)))

    if not tracks:
        return [], list(range(len(detections))), []

    # Build cost matrix (row: detection, col: track)
    # Store tuples of (cost, det_idx, track_idx) for sorting
    costs: list[tuple[float, int, int]] = []

    for d_idx, det in enumerate(detections):
        for t_idx, track in enumerate(tracks):
            # Must match class
            if det.class_name != track.class_name:
                continue

            dist = calculate_centroid_distance(det, track)
            if dist <= max_distance:
                costs.append((dist, d_idx, t_idx))

    # Sort by lowest distance first (greedy approach)
    costs.sort(key=lambda x: x[0])

    matched_indices: list[tuple[int, int]] = []
    assigned_detections: set[int] = set()
    assigned_tracks: set[int] = set()

    for cost, d_idx, t_idx in costs:
        if d_idx not in assigned_detections and t_idx not in assigned_tracks:
            matched_indices.append((d_idx, t_idx))
            assigned_detections.add(d_idx)
            assigned_tracks.add(t_idx)

    unmatched_detections = [
        i for i in range(len(detections)) if i not in assigned_detections
    ]
    unmatched_tracks = [i for i in range(len(tracks)) if i not in assigned_tracks]

    return matched_indices, unmatched_detections, unmatched_tracks
