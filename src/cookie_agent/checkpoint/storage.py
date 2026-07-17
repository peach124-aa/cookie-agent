"""File-based persistent storage for checkpoints."""

import os
import tempfile
from pathlib import Path

from cookie_agent.checkpoint.exceptions import CheckpointLoadError, CheckpointSaveError


class FileStorage:
    """Concrete implementation of CheckpointStorageProtocol using local filesystem."""

    def write_atomic(self, filepath: str, data: bytes) -> None:
        """Atomically write data to the specified filepath.

        Creates a temporary file, writes the data, flushes to disk,
        and atomically replaces the target file.
        """
        path = Path(filepath)
        directory = path.parent
        if str(directory) != ".":
            directory.mkdir(parents=True, exist_ok=True)

        fd, temp_path_str = tempfile.mkstemp(dir=str(directory), prefix=".tmp_ckpt_")
        temp_path = Path(temp_path_str)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            temp_path.replace(path)
        except OSError as e:
            if temp_path.exists():
                temp_path.unlink()
            raise CheckpointSaveError(
                f"Failed to atomically write {filepath}: {e}"
            ) from e

    def read(self, filepath: str) -> bytes:
        """Read data from the specified filepath."""
        try:
            with Path(filepath).open("rb") as f:
                return f.read()
        except OSError as e:
            raise CheckpointLoadError(f"Failed to read {filepath}: {e}") from e

    def exists(self, filepath: str) -> bool:
        """Check if a file exists at the specified filepath."""
        return Path(filepath).exists()
