"""Custom exceptions for the Training orchestration layer."""


class TrainingError(Exception):
    """Base exception for all errors occurring during the training loop."""

    pass


class TrainingStoppedError(TrainingError):
    """Raised when the training loop is intentionally interrupted or aborted."""

    pass
