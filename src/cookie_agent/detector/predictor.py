"""Predictor implementing core Detector protocol."""

from collections.abc import Sequence
from typing import cast

from cookie_agent.core.detection import Detection as CoreDetection
from cookie_agent.core.detection import DetectionClass
from cookie_agent.core.frame import Frame
from cookie_agent.core.protocols import Detector
from cookie_agent.core.types import Confidence
from cookie_agent.detector.model import InferenceModel
from cookie_agent.detector.postprocess import postprocess_predictions
from cookie_agent.detector.preprocess import preprocess_frame


class Predictor(Detector):
    """Integrate pre/postprocessing with an InferenceModel backend.

    Implements the Detector protocol contract.
    """

    def __init__(
        self,
        model_loader: InferenceModel,
        model_path: str,
        device: str = "cpu",
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        target_size: tuple[int, int] | None = None,
        class_filters: set[int] | None = None,
        class_names: dict[int, str] | None = None,
        class_map: dict[int, DetectionClass] | None = None,
        detector_name: str = "default_yolo",
    ):
        """Initialize the Predictor.

        Args:
            model_loader: Inference backend model instance.
            model_path: Path to target model files.
            device: Connection target device.
            confidence_threshold: Minimum confidence score.
            iou_threshold: NMS overlap threshold.
            target_size: Target image dimensions.
            class_filters: Optional subset of class IDs to filter.
            class_names: Mapping from class ID to label name.
            class_map: Mapping from class ID to core DetectionClass enums.
            detector_name: Name of this detector configuration.
        """
        self.model_loader = model_loader
        self.model_path = model_path
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.target_size = target_size
        self.class_filters = class_filters
        self.class_names = class_names
        self.class_map = class_map
        self.detector_name = detector_name
        self._model_loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy load model parameters."""
        if not self._model_loaded:
            self.model_loader.load(self.model_path, self.device)
            self._model_loaded = True

    def detect(self, frame: Frame) -> Sequence[CoreDetection]:
        """Perform object detection on the Frame.

        Args:
            frame: Immutable Frame object.

        Returns:
            Sequence[CoreDetection]: List of core Detection objects.
        """
        self._ensure_loaded()

        # Run preprocessing
        input_tensor = preprocess_frame(frame, self.target_size)

        # Forward prediction
        raw_outputs = self.model_loader.predict(input_tensor)

        # Run postprocessing NMS and coordinate restoration
        local_detections = postprocess_predictions(
            raw_outputs,
            conf_threshold=self.confidence_threshold,
            iou_threshold=self.iou_threshold,
            original_size=frame.resolution,
            target_size=self.target_size,
            class_filters=self.class_filters,
            class_names=self.class_names,
        )

        # Map to core representations
        core_detections = []
        for det in local_detections:
            c_name = DetectionClass.JELLY
            if self.class_map and det.class_id in self.class_map:
                c_name = self.class_map[det.class_id]
            else:
                try:
                    c_name = DetectionClass(det.class_name)
                except ValueError:
                    pass

            core_detections.append(
                CoreDetection(
                    frame_id=frame.frame_id,
                    timestamp=frame.timestamp,
                    class_name=c_name,
                    bbox=det.bbox,
                    confidence=cast(Confidence, det.confidence),
                    detector_name=self.detector_name,
                )
            )

        return core_detections
