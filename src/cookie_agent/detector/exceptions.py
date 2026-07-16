"""Detector-specific exceptions."""


class DetectorError(Exception):
    """Base exception for all detector module errors."""


class ModelLoadError(DetectorError):
    """Raised when loading model weights or configurations fails."""


class InferenceError(DetectorError):
    """Raised when running object detection inference fails."""
