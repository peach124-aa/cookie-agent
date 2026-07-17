from pathlib import Path
from typing import Any

from cookie_agent.checkpoint.exceptions import (
    CheckpointLoadError,
    CheckpointSaveError,
    CheckpointVersionError,
)
from cookie_agent.checkpoint.metadata import CheckpointMetadata
from cookie_agent.checkpoint.protocols import (
    CheckpointSerializerProtocol,
    CheckpointStorageProtocol,
)


class CheckpointManager:
    """Manages saving and loading of model checkpoints."""

    def __init__(
        self,
        directory: str,
        storage: CheckpointStorageProtocol,
        serializer: CheckpointSerializerProtocol,
        model_version: str,
    ) -> None:
        """Initialize the Checkpoint Manager.

        Args:
            directory: The base directory for saving checkpoints.
            storage: The persistent storage backend.
            serializer: The serialization backend.
            model_version: The expected version of the model.
        """
        self._directory = Path(directory)
        self._storage = storage
        self._serializer = serializer
        self._model_version = model_version

    def save(
        self,
        model_state: Any,
        optimizer_state: Any,
        metadata: CheckpointMetadata,
        is_best: bool = False,
    ) -> None:
        """Save a checkpoint.

        Args:
            model_state: The model's state.
            optimizer_state: The optimizer's state.
            metadata: Associated metadata.
            is_best: Whether this is the best checkpoint so far.
        """
        state_dict = {
            "model_state": model_state,
            "optimizer_state": optimizer_state,
            "metadata": metadata.to_dict(),
        }

        try:
            data = self._serializer.serialize(state_dict)
        except (ValueError, TypeError) as e:
            raise CheckpointSaveError(f"Serialization failed: {e}") from e

        latest_path = self._directory / "latest.pt"
        self._storage.write_atomic(str(latest_path), data)

        if is_best:
            best_path = self._directory / "best.pt"
            self._storage.write_atomic(str(best_path), data)

    def load(self, filepath: str) -> tuple[Any, Any, CheckpointMetadata]:
        """Load a checkpoint.

        Args:
            filepath: The path to the checkpoint file.

        Returns:
            A tuple of (model_state, optimizer_state, metadata).

        Raises:
            CheckpointLoadError: If loading fails or file does not exist.
            CheckpointVersionError: If the loaded model version does not match.
        """
        if not self._storage.exists(filepath):
            raise CheckpointLoadError(f"Checkpoint not found: {filepath}")

        data = self._storage.read(filepath)

        try:
            state_dict = self._serializer.deserialize(data)
        except (ValueError, TypeError) as e:
            raise CheckpointLoadError(f"Deserialization failed: {e}") from e

        if "metadata" not in state_dict:
            raise CheckpointLoadError("Checkpoint is missing metadata.")

        try:
            metadata = CheckpointMetadata.from_dict(state_dict["metadata"])
        except (KeyError, ValueError) as e:
            raise CheckpointLoadError(f"Invalid metadata format: {e}") from e

        if metadata.model_version != self._model_version:
            raise CheckpointVersionError(
                f"Version mismatch: Expected {self._model_version}, "
                f"got {metadata.model_version}"
            )

        model_state = state_dict.get("model_state")
        optimizer_state = state_dict.get("optimizer_state")

        return model_state, optimizer_state, metadata

    def latest_checkpoint(self) -> str | None:
        """Get the path to the latest checkpoint if it exists."""
        path = str(self._directory / "latest.pt")
        return path if self._storage.exists(path) else None

    def best_checkpoint(self) -> str | None:
        """Get the path to the best checkpoint if it exists."""
        path = str(self._directory / "best.pt")
        return path if self._storage.exists(path) else None

    def exists(self, filepath: str) -> bool:
        """Check if a checkpoint exists at the specified path."""
        return self._storage.exists(filepath)
