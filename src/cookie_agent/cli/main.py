"""Main entry point for the Cookie Agent CLI."""

import sys
from collections.abc import Sequence
from pathlib import Path

from cookie_agent.cli.commands import (
    handle_evaluate,
    handle_play,
    handle_train,
    handle_version,
)
from cookie_agent.cli.exceptions import CliError
from cookie_agent.cli.parser import parse_args
from cookie_agent.cli.protocols import (
    AppBuilderProtocol,
    EvaluatorProtocol,
    RunnableProtocol,
)


class DefaultAppBuilder:
    """Default concrete implementation for building app dependencies.

    This will be fully implemented in a future DI container commit.
    For now it raises NotImplementedError to satisfy the protocol shape.
    """

    def build_training_runner(self, config_path: Path) -> RunnableProtocol:
        """Build the TrainingRunner."""
        raise NotImplementedError("Dependency injection not fully wired yet.")

    def build_inference_runner(self, config_path: Path) -> RunnableProtocol:
        """Build the InferenceRunner."""
        raise NotImplementedError("Dependency injection not fully wired yet.")

    def build_evaluator(
        self, config_path: Path, checkpoint_path: Path
    ) -> EvaluatorProtocol:
        """Build the Evaluator."""
        raise NotImplementedError("Dependency injection not fully wired yet.")


def main(
    args: Sequence[str] | None = None,
    builder: AppBuilderProtocol | None = None,
) -> int:
    """Run the CLI application.

    Args:
        args: Optional list of command line arguments.
        builder: Optional dependency injection builder (used for testing).

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    if builder is None:
        builder = DefaultAppBuilder()

    try:
        parsed_args = parse_args(args)

        if parsed_args.command == "train":
            handle_train(parsed_args, builder)
        elif parsed_args.command == "play":
            handle_play(parsed_args, builder)
        elif parsed_args.command == "evaluate":
            handle_evaluate(parsed_args, builder)
        elif parsed_args.command == "version":
            handle_version(parsed_args)
        else:
            print(f"Error: Unknown command '{parsed_args.command}'", file=sys.stderr)
            return 1

        return 0

    except CliError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except SystemExit as e:
        # argparse raises SystemExit on --help or invalid args
        return e.code if isinstance(e.code, int) else 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
