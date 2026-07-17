"""Command handlers for the Cookie Agent CLI."""

import argparse
from pathlib import Path

from cookie_agent.cli.exceptions import CliCommandError
from cookie_agent.cli.protocols import AppBuilderProtocol
from cookie_agent.version import __version__


def handle_train(args: argparse.Namespace, builder: AppBuilderProtocol) -> None:
    """Handle the 'train' command."""
    config_path = Path(args.config)
    if not config_path.is_file():
        raise CliCommandError(f"Configuration file not found: {config_path}")

    try:
        runner = builder.build_training_runner(config_path)
    except (ValueError, TypeError) as e:
        raise CliCommandError(f"Failed to build TrainingRunner: {e}") from e

    # Assume a single episode or run loop is executed by run_episode
    # In a real app this might loop, but the CLI's job is just to invoke it.
    runner.run_episode()


def handle_play(args: argparse.Namespace, builder: AppBuilderProtocol) -> None:
    """Handle the 'play' command."""
    config_path = Path(args.config)
    if not config_path.is_file():
        raise CliCommandError(f"Configuration file not found: {config_path}")

    try:
        runner = builder.build_inference_runner(config_path)
    except (ValueError, TypeError) as e:
        raise CliCommandError(f"Failed to build InferenceRunner: {e}") from e

    runner.run_episode()


def handle_evaluate(args: argparse.Namespace, builder: AppBuilderProtocol) -> None:
    """Handle the 'evaluate' command."""
    config_path = Path(args.config)
    checkpoint_path = Path(args.checkpoint)

    if not config_path.is_file():
        raise CliCommandError(f"Configuration file not found: {config_path}")
    if not checkpoint_path.is_file():
        raise CliCommandError(f"Checkpoint file not found: {checkpoint_path}")

    try:
        evaluator = builder.build_evaluator(config_path, checkpoint_path)
    except (ValueError, TypeError) as e:
        raise CliCommandError(f"Failed to build Evaluator: {e}") from e

    evaluator.evaluate()


def handle_version(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Handle the 'version' command."""
    print(f"Cookie Agent v{__version__}")
