"""Inference model protocol definition."""

from typing import Any, Protocol


class InferenceModel(Protocol):
    """Protocol for model inference engines, enabling dependency injection."""

    def load(self, model_path: str, device: str) -> None:
        """Load model weights and configurations.

        Args:
            model_path: Configured path to model files.
            device: target execution backend device (e.g. cpu, cuda).
        """
        ...

    def predict(self, input_tensor: Any) -> list[list[float]]:
        """Run prediction inference forward pass.

        Args:
            input_tensor: Preprocessed normalized image matrix.

        Returns:
            list[list[float]]: Raw predictions matrix of shape [N, 6], where each row
                is structured as [xmin, ymin, xmax, ymax, confidence, class_id].
        """
        ...
