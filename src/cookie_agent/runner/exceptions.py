"""Domain-specific exceptions for the Inference Runner."""


class RunnerError(Exception):
    """Base exception for all Runner related errors."""


class PipelineError(RunnerError):
    """Raised when a step in the pipeline fails."""


class LoopStoppedError(RunnerError):
    """Raised to cleanly stop the inference loop."""
