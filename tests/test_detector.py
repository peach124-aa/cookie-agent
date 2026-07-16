"""Unit tests for the Detector module in pure Python."""

from typing import cast

import pytest
from cookie_agent.core.detection import BBox, DetectionClass
from cookie_agent.core.frame import Frame
from cookie_agent.core.protocols import Detector
from cookie_agent.core.types import FrameId, Timestamp
from cookie_agent.detector import (
    DetectorError,
    InferenceError,
    ModelLoadError,
    Predictor,
    non_max_suppression,
    postprocess_predictions,
    preprocess_frame,
    restore_coordinates,
)


class MockInferenceModel:
    """Mock inference backend for testing Predictor flows."""

    def __init__(self, mock_outputs: list[list[float]]) -> None:
        """Initialise with pre-canned raw detection outputs."""
        self.mock_outputs = mock_outputs
        self.loaded: bool = False
        self.loaded_path = ""
        self.loaded_device = ""

    def load(self, model_path: str, device: str) -> None:
        """Simulate model loading; raise on 'invalid' path."""
        if model_path == "invalid":
            raise ModelLoadError("Failed to load model file.")
        self.loaded = True
        self.loaded_path = model_path
        self.loaded_device = device

    def predict(self, input_tensor: list[list[list[float]]]) -> list[list[float]]:
        """Return pre-canned outputs or raise on empty tensor."""
        if not input_tensor:
            raise InferenceError("Invalid input tensor.")
        return self.mock_outputs


def test_preprocess_frame() -> None:
    """Verify preprocessing correctly normalizes and resizes frames."""
    # 2x2 BGRA frame data (16 bytes)
    bgra_data = bytes([10, 20, 30, 255] * 4)
    frame = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, 0.0),
        width=2,
        height=2,
        data=bgra_data,
    )

    # Without resizing
    tensor = preprocess_frame(frame)
    assert len(tensor) == 2
    assert len(tensor[0]) == 2
    assert len(tensor[0][0]) == 3
    # Check BGRA to RGB: BGR=10,20,30 -> RGB=30,20,10 -> norm=30/255, 20/255, 10/255
    assert abs(tensor[0][0][0] - 30 / 255.0) < 1e-5
    assert abs(tensor[0][0][1] - 20 / 255.0) < 1e-5
    assert abs(tensor[0][0][2] - 10 / 255.0) < 1e-5

    # With resizing to 4x4 (nearest-neighbor interpolation)
    resized_tensor = preprocess_frame(frame, target_size=(4, 4))
    assert len(resized_tensor) == 4
    assert len(resized_tensor[0]) == 4
    assert abs(resized_tensor[0][0][0] - 30 / 255.0) < 1e-5


def test_coordinate_restoration() -> None:
    """Verify coordinate restoration scales bounding boxes back to original bounds."""
    # Original: 1280x720, Target: 640x360 (Scale factor = 2.0)
    bbox = BBox(xmin=10, ymin=20, xmax=100, ymax=200)
    restored = restore_coordinates(
        bbox, original_size=(1280, 720), target_size=(640, 360)
    )

    assert restored.xmin == 20
    assert restored.ymin == 40
    assert restored.xmax == 200
    assert restored.ymax == 400


def test_non_max_suppression() -> None:
    """Verify NMS filters overlapping boxes based on IoU threshold."""
    boxes = [
        [10.0, 10.0, 50.0, 50.0],  # Box A
        [12.0, 12.0, 48.0, 48.0],  # Box B (high overlap with A)
        [100.0, 100.0, 150.0, 150.0],  # Box C (no overlap)
    ]
    scores = [0.9, 0.85, 0.7]

    # Keep highest score overlapping box and non-overlapping box
    keep = non_max_suppression(boxes, scores, iou_threshold=0.5)
    assert keep == [0, 2]


def test_postprocess_predictions() -> None:
    """Verify postprocessing handles class and confidence filtering."""
    # Columns: xmin, ymin, xmax, ymax, confidence, class_id
    raw_outputs = [
        [10, 10, 50, 50, 0.9, 0],  # Class 0, Conf 0.9
        [12, 12, 48, 48, 0.8, 0],  # Class 0, Conf 0.8 (suppressed by NMS)
        [100, 100, 150, 150, 0.4, 1],  # Class 1, Conf 0.4 (below conf thresh)
        [200, 200, 250, 250, 0.85, 2],  # Class 2, Conf 0.85 (filtered by class_filters)
    ]

    class_names = {0: "cookie", 1: "jelly", 2: "obstacle"}
    class_filters = {0, 1}

    dets = postprocess_predictions(
        raw_outputs,
        conf_threshold=0.5,
        iou_threshold=0.5,
        original_size=(1000, 1000),
        class_filters=class_filters,
        class_names=class_names,
    )

    assert len(dets) == 1
    assert dets[0].class_id == 0
    assert dets[0].class_name == "cookie"
    assert dets[0].confidence == 0.9


def test_predictor_detect_lazy_loading() -> None:
    """Verify Predictor lazy loads the model on first detect call."""
    mock_outputs = [[10, 10, 50, 50, 0.9, 0]]
    model = MockInferenceModel(mock_outputs)

    class_map = {0: DetectionClass.COOKIE}
    predictor = Predictor(
        model_loader=model,
        model_path="weights.pt",
        device="cpu",
        class_map=class_map,
    )

    assert model.loaded is False

    frame = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, 1.0),
        width=10,
        height=10,
        data=bytes([0] * 300),
    )

    # Perform detection (triggers load)
    results = predictor.detect(frame)
    # Verify lazy-load side-effects
    assert model.loaded_path == "weights.pt"
    assert model.loaded_device == "cpu"
    assert model.loaded is True

    assert len(results) == 1  # type: ignore[unreachable]
    assert results[0].class_name == DetectionClass.COOKIE
    assert results[0].confidence == 0.9
    assert results[0].bbox.xmin == 10


def test_predictor_protocol_conformance() -> None:
    """Verify Predictor conforms to core Detector protocol."""
    model = MockInferenceModel([])
    predictor = Predictor(model, "weights.pt")
    assert isinstance(predictor, Detector)


def test_exceptions_inheritance() -> None:
    """Verify custom exception inheritance."""
    assert issubclass(ModelLoadError, DetectorError)
    assert issubclass(InferenceError, DetectorError)


def test_predictor_load_failure() -> None:
    """Verify that backend loading failure propagates correct exceptions."""
    model = MockInferenceModel([])
    predictor = Predictor(model, "invalid")
    frame = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, 1.0),
        width=10,
        height=10,
        data=bytes([0] * 300),
    )
    with pytest.raises(ModelLoadError):
        predictor.detect(frame)


def test_predictor_no_class_map() -> None:
    """Verify class mapping fallbacks when class_map is absent."""
    # Two items: class 0 (label "cookie") and class 1 (label "unknown")
    mock_outputs = [
        [10, 10, 50, 50, 0.9, 0],
        [20, 20, 60, 60, 0.85, 1],
    ]
    model = MockInferenceModel(mock_outputs)

    class_names = {0: "cookie", 1: "unknown"}
    predictor = Predictor(
        model_loader=model,
        model_path="weights.pt",
        device="cpu",
        class_names=class_names,
    )

    frame = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, 1.0),
        width=10,
        height=10,
        data=bytes([0] * 300),
    )

    results = predictor.detect(frame)
    assert len(results) == 2
    # "cookie" matches DetectionClass.COOKIE
    assert results[0].class_name == DetectionClass.COOKIE
    # "unknown" fails match and defaults to DetectionClass.JELLY
    assert results[1].class_name == DetectionClass.JELLY


def test_postprocess_edge_cases() -> None:
    """Verify postprocessing edge cases."""
    # compute_iou with zero union
    box1 = [0.0, 0.0, 0.0, 0.0]
    box2 = [0.0, 0.0, 0.0, 0.0]
    from cookie_agent.detector.postprocess import compute_iou

    assert compute_iou(box1, box2) == 0.0

    # NMS with empty boxes
    assert non_max_suppression([], [], 0.5) == []

    # postprocess_predictions with empty raw_outputs
    assert postprocess_predictions([], 0.5, 0.5, (10, 10)) == []

    # postprocess_predictions with empty filtered outputs
    raw_outputs = [[10.0, 10.0, 50.0, 50.0, 0.2, 0.0]]  # Below threshold
    assert postprocess_predictions(raw_outputs, 0.5, 0.5, (10, 10)) == []
