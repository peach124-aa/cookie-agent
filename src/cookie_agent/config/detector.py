"""Detector configuration."""

from dataclasses import dataclass

from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_non_empty, validate_range


@dataclass(frozen=True, slots=True)
class DetectorConfig(BaseConfig):
    """Configuration for target classification."""

    detector_type: str
    model_path: str
    confidence_threshold: float
    iou_threshold: float
    device: str
    half_precision: bool

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_non_empty("detector_type", self.detector_type)
        validate_non_empty("model_path", self.model_path)
        validate_range("confidence_threshold", self.confidence_threshold, 0.0, 1.0)
        validate_range("iou_threshold", self.iou_threshold, 0.0, 1.0)
        validate_non_empty("device", self.device)

    @classmethod
    def default(cls) -> "DetectorConfig":
        """Return default configuration."""
        return cls(
            detector_type="yolov8",
            model_path="models/best.pt",
            confidence_threshold=0.5,
            iou_threshold=0.45,
            device="cuda",
            half_precision=True,
        )
