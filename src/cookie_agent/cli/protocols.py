"""Protocols for CLI dependency injection."""

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class RunnableProtocol(Protocol):
    """Contract for any runner that can be executed by the CLI."""

    def run_episode(self) -> None:
        """Execute a single episode or run loop."""
        ...


@runtime_checkable
class EvaluatorProtocol(Protocol):
    """Contract for the evaluation runner."""

    def evaluate(self) -> None:
        """Run the evaluation and print metrics."""
        ...


@runtime_checkable
class AppBuilderProtocol(Protocol):
    """Contract for building application dependencies."""

    def build_training_runner(self, config_path: Path) -> RunnableProtocol:
        """Build the TrainingRunner."""
        ...

    def build_inference_runner(self, config_path: Path) -> RunnableProtocol:
        """Build the InferenceRunner."""
        ...

    def build_evaluator(
        self, config_path: Path, checkpoint_path: Path
    ) -> EvaluatorProtocol:
        """Build the Evaluator."""
        ...
