"""Unit tests for the Checkpoint subsystem."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cookie_agent.checkpoint.exceptions import (
    CheckpointLoadError,
    CheckpointVersionError,
)
from cookie_agent.checkpoint.manager import CheckpointManager
from cookie_agent.checkpoint.metadata import CheckpointMetadata
from cookie_agent.checkpoint.protocols import (
    CheckpointSerializerProtocol,
    CheckpointStorageProtocol,
)
from cookie_agent.checkpoint.storage import FileStorage


@pytest.fixture()
def mock_storage() -> MagicMock:
    """Mock storage backend."""
    storage = MagicMock(spec=CheckpointStorageProtocol)
    storage.exists.return_value = True
    storage.read.return_value = b"mock_data"
    return storage


@pytest.fixture()
def mock_serializer() -> MagicMock:
    """Mock serializer backend."""
    serializer = MagicMock(spec=CheckpointSerializerProtocol)
    serializer.serialize.return_value = b"mock_data"

    # By default, deserialize returns a valid state
    serializer.deserialize.return_value = {
        "model_state": "mock_model",
        "optimizer_state": "mock_opt",
        "metadata": {
            "episode": 10,
            "global_step": 1000,
            "total_reward": 500.5,
            "timestamp": 1234567890.0,
            "model_version": "1.0",
        },
    }
    return serializer


@pytest.fixture()
def metadata() -> CheckpointMetadata:
    """Dummy metadata."""
    return CheckpointMetadata(
        episode=10,
        global_step=1000,
        total_reward=500.5,
        timestamp=1234567890.0,
        model_version="1.0",
    )


@pytest.fixture()
def manager(mock_storage: MagicMock, mock_serializer: MagicMock) -> CheckpointManager:
    """Manager with mocked dependencies."""
    return CheckpointManager(
        directory="/fake/dir",
        storage=mock_storage,
        serializer=mock_serializer,
        model_version="1.0",
    )


def test_metadata_serialization(metadata: CheckpointMetadata) -> None:
    """Test Metadata Serialization."""
    data = metadata.to_dict()
    assert data["episode"] == 10
    assert data["global_step"] == 1000
    assert data["total_reward"] == 500.5
    assert data["timestamp"] == 1234567890.0
    assert data["model_version"] == "1.0"

    restored = CheckpointMetadata.from_dict(data)
    assert restored == metadata


def test_save_success(
    manager: CheckpointManager, mock_storage: MagicMock, metadata: CheckpointMetadata
) -> None:
    """Test Save Success."""
    manager.save(
        model_state="mock_model",
        optimizer_state="mock_opt",
        metadata=metadata,
        is_best=False,
    )

    # Should only write latest.pt
    mock_storage.write_atomic.assert_called_once()
    args, _kwargs = mock_storage.write_atomic.call_args
    assert args[0].endswith("latest.pt")
    assert args[1] == b"mock_data"


def test_best_checkpoint_save(
    manager: CheckpointManager, mock_storage: MagicMock, metadata: CheckpointMetadata
) -> None:
    """Test Save Success with Best Checkpoint."""
    manager.save(
        model_state="mock_model",
        optimizer_state="mock_opt",
        metadata=metadata,
        is_best=True,
    )

    # Should write latest.pt and best.pt
    assert mock_storage.write_atomic.call_count == 2
    calls = mock_storage.write_atomic.call_args_list
    assert calls[0][0][0].endswith("latest.pt")
    assert calls[1][0][0].endswith("best.pt")


def test_load_success(manager: CheckpointManager, metadata: CheckpointMetadata) -> None:
    """Test Load Success (Resume Success)."""
    model, opt, meta = manager.load("/fake/dir/latest.pt")
    assert model == "mock_model"
    assert opt == "mock_opt"
    assert meta == metadata


def test_file_not_found(manager: CheckpointManager, mock_storage: MagicMock) -> None:
    """Test File Not Found."""
    mock_storage.exists.return_value = False
    with pytest.raises(CheckpointLoadError, match="Checkpoint not found"):
        manager.load("/fake/dir/latest.pt")


def test_version_mismatch(
    manager: CheckpointManager, mock_serializer: MagicMock
) -> None:
    """Test Version Mismatch."""
    mock_serializer.deserialize.return_value = {
        "model_state": "mock_model",
        "optimizer_state": "mock_opt",
        "metadata": {
            "episode": 10,
            "global_step": 1000,
            "total_reward": 500.5,
            "timestamp": 1234567890.0,
            "model_version": "2.0",  # Mismatch
        },
    }
    with pytest.raises(CheckpointVersionError, match="Version mismatch"):
        manager.load("/fake/dir/latest.pt")


def test_latest_and_best_checkpoint(
    manager: CheckpointManager, mock_storage: MagicMock
) -> None:
    """Test Latest Checkpoint and Best Checkpoint paths."""
    mock_storage.exists.return_value = True
    assert manager.latest_checkpoint() == str(Path("/fake/dir") / "latest.pt")
    assert manager.best_checkpoint() == str(Path("/fake/dir") / "best.pt")

    mock_storage.exists.return_value = False
    assert manager.latest_checkpoint() is None
    assert manager.best_checkpoint() is None


@pytest.fixture()
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for FileStorage tests."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def test_atomic_save(temp_dir: Path) -> None:
    """Test Atomic Save flow in FileStorage."""
    storage = FileStorage()
    target_file = temp_dir / "target.pt"

    # We patch Path.replace to simulate atomicity verification
    replace_called = False
    temp_file_used = ""

    def mock_replace(self: Path, dst: str | Path) -> None:
        nonlocal replace_called, temp_file_used
        replace_called = True
        temp_file_used = str(self)
        assert self.exists()
        assert str(dst) == str(target_file)
        shutil.move(self, dst)

    with patch.object(Path, "replace", autospec=True, side_effect=mock_replace):
        storage.write_atomic(str(target_file), b"test_data")

    assert replace_called
    assert not Path(temp_file_used).exists()
    assert storage.exists(str(target_file))
    assert storage.read(str(target_file)) == b"test_data"
