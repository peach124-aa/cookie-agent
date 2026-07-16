"""Public detector package exports."""

from cookie_agent.detector.exceptions import (
    DetectorError,
    InferenceError,
    ModelLoadError,
)
from cookie_agent.detector.model import InferenceModel
from cookie_agent.detector.postprocess import (
    non_max_suppression,
    postprocess_predictions,
    restore_coordinates,
)
from cookie_agent.detector.predictor import Predictor
from cookie_agent.detector.preprocess import preprocess_frame
from cookie_agent.detector.types import Detection

__all__: list[str] = [
    "Detection",
    "DetectorError",
    "InferenceError",
    "InferenceModel",
    "ModelLoadError",
    "Predictor",
    "non_max_suppression",
    "postprocess_predictions",
    "preprocess_frame",
    "restore_coordinates",
]
