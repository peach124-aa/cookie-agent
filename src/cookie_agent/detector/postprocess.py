"""Postprocessing routines for object detection models in pure Python."""

from cookie_agent.core.detection import BBox
from cookie_agent.detector.types import Detection


def compute_iou(box1: list[float], box2: list[float]) -> float:
    """Calculate Intersection-over-Union (IoU) of two bounding boxes.

    Args:
        box1: list containing [xmin, ymin, xmax, ymax].
        box2: list containing [xmin, ymin, xmax, ymax].

    Returns:
        float: Calculated IoU ratio.
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    if union == 0.0:
        return 0.0
    return float(intersection / union)


def non_max_suppression(
    boxes: list[list[float]], scores: list[float], iou_threshold: float
) -> list[int]:
    """Perform Non-Maximum Suppression (NMS) to filter overlapping predictions.

    Args:
        boxes: list of shape [N, 4] containing [xmin, ymin, xmax, ymax].
        scores: list of shape [N] containing confidence scores.
        iou_threshold: Overlap limit threshold.

    Returns:
        list[int]: Selected prediction index lists.
    """
    if not boxes:
        return []

    indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    keep = []
    while indices:
        current = indices[0]
        keep.append(current)
        if len(indices) == 1:
            break
        remaining = []
        for idx in indices[1:]:
            iou = compute_iou(boxes[current], boxes[idx])
            if iou < iou_threshold:
                remaining.append(idx)
        indices = remaining
    return keep


def restore_coordinates(
    bbox: BBox,
    original_size: tuple[int, int],
    target_size: tuple[int, int] | None = None,
) -> BBox:
    """Scale bounding box coordinates back to original resolution.

    Args:
        bbox: BBox predicted on resized coordinates.
        original_size: Original (width, height) frame size.
        target_size: Resized (width, height) model input size.

    Returns:
        BBox: BBox mapped back to original coordinates.
    """
    if target_size is None or target_size == original_size:
        return bbox

    orig_w, orig_h = original_size
    targ_w, targ_h = target_size

    scale_x = orig_w / targ_w
    scale_y = orig_h / targ_h

    xmin = round(bbox.xmin * scale_x)
    ymin = round(bbox.ymin * scale_y)
    xmax = round(bbox.xmax * scale_x)
    ymax = round(bbox.ymax * scale_y)

    return BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)


def postprocess_predictions(
    raw_outputs: list[list[float]],
    conf_threshold: float,
    iou_threshold: float,
    original_size: tuple[int, int],
    target_size: tuple[int, int] | None = None,
    class_filters: set[int] | None = None,
    class_names: dict[int, str] | None = None,
) -> list[Detection]:
    """Filter, suppress, and scale raw model outputs to local Detection instances.

    Args:
        raw_outputs: nested list of shape [N, 6] containing
            [xmin, ymin, xmax, ymax, confidence, class_id].
        conf_threshold: Confidence filtering threshold.
        iou_threshold: NMS IoU threshold.
        original_size: Original frame size (width, height).
        target_size: Model input size (width, height).
        class_filters: Set of class IDs to keep. If None, all are kept.
        class_names: Mapping from class ID to label name.

    Returns:
        list[Detection]: List of postprocessed local Detection objects.
    """
    if not raw_outputs:
        return []

    filtered_rows = []
    for row in raw_outputs:
        conf = row[4]
        cid = int(row[5])
        if conf >= conf_threshold:
            if class_filters is None or cid in class_filters:
                filtered_rows.append(row)

    if not filtered_rows:
        return []

    boxes = [row[:4] for row in filtered_rows]
    scores = [row[4] for row in filtered_rows]

    keep_indices = non_max_suppression(boxes, scores, iou_threshold)

    detections = []
    for idx in keep_indices:
        row = filtered_rows[idx]
        xmin, ymin, xmax, ymax, conf, cid_float = row
        cid = int(cid_float)
        cname = class_names.get(cid, f"class_{cid}") if class_names else f"class_{cid}"

        raw_box = BBox(xmin=int(xmin), ymin=int(ymin), xmax=int(xmax), ymax=int(ymax))
        restored_box = restore_coordinates(raw_box, original_size, target_size)

        detections.append(
            Detection(
                class_id=cid,
                class_name=cname,
                confidence=float(conf),
                bbox=restored_box,
            )
        )
    return detections
