"""Exceptions for the checkpoint subsystem."""


class CheckpointError(Exception):
    """Base exception for all checkpoint-related errors."""


class CheckpointSaveError(CheckpointError):
    """Raised when a checkpoint fails to save properly."""


class CheckpointLoadError(CheckpointError):
    """Raised when a checkpoint fails to load properly."""


class CheckpointVersionError(CheckpointLoadError):
    """Raised when loading a checkpoint with an incompatible model version."""
