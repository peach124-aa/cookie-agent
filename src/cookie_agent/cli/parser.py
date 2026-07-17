"""Argument parsing for the Cookie Agent CLI."""

import argparse
from collections.abc import Sequence


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="cookie-agent",
        description="Cookie Agent Command Line Interface",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Train command
    train_parser = subparsers.add_parser(
        "train",
        help="Start the reinforcement learning training loop",
    )
    train_parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the training configuration file",
    )

    # Play command
    play_parser = subparsers.add_parser(
        "play",
        help="Start the inference runner (play mode)",
    )
    play_parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the inference configuration file",
    )

    # Evaluate command
    eval_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate a trained model checkpoint",
    )
    eval_parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the evaluation configuration file",
    )
    eval_parser.add_argument(
        "--checkpoint",
        type=str,
        required=True,
        help="Path to the model checkpoint file",
    )

    # Version command
    subparsers.add_parser(
        "version",
        help="Show the Cookie Agent version",
    )

    return parser


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser()
    return parser.parse_args(args)
