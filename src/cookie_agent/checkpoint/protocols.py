"""Protocols for the checkpoint subsystem."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CheckpointSerializerProtocol(Protocol):
    """Contract for serializing and deserializing checkpoint data."""

    def serialize(self, state: dict[str, Any]) -> bytes:
        """Serialize the raw checkpoint state dictionary into bytes."""
        ...

    def deserialize(self, data: bytes) -> dict[str, Any]:
        """Deserialize bytes back into the checkpoint state dictionary."""
        ...


@runtime_checkable
class CheckpointStorageProtocol(Protocol):
    """Contract for persistent storage operations."""

    def write_atomic(self, filepath: str, data: bytes) -> None:
        """Atomically write data to the specified filepath."""
        ...

    def read(self, filepath: str) -> bytes:
        """Read data from the specified filepath."""
        ...

    def exists(self, filepath: str) -> bool:
        """Check if a file exists at the specified filepath."""
        ...
