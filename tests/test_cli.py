"""Unit tests for the Cookie Agent CLI."""

import argparse
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cookie_agent.cli.commands import (
    handle_evaluate,
    handle_play,
    handle_train,
)
from cookie_agent.cli.exceptions import CliCommandError
from cookie_agent.cli.main import main
from cookie_agent.cli.parser import parse_args
from cookie_agent.cli.protocols import AppBuilderProtocol


@pytest.fixture()
def mock_builder() -> MagicMock:
    """Provide a mock dependency injection builder."""
    builder = MagicMock(spec=AppBuilderProtocol)

    # Mock runners
    mock_runner = MagicMock()
    mock_runner.run_episode.return_value = None
    builder.build_training_runner.return_value = mock_runner
    builder.build_inference_runner.return_value = mock_runner

    mock_eval = MagicMock()
    mock_eval.evaluate.return_value = None
    builder.build_evaluator.return_value = mock_eval

    return builder


@pytest.fixture()
def temp_config_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary config file path."""
    config = tmp_path / "config.json"
    config.write_text("{}")
    return config


@pytest.fixture()
def temp_checkpoint_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary checkpoint file path."""
    ckpt = tmp_path / "model.pt"
    ckpt.write_text("dummy")
    return ckpt


def test_parser_train() -> None:
    """Test parser behavior for 'train' command."""
    args = parse_args(["train", "--config", "config.json"])
    assert args.command == "train"
    assert args.config == "config.json"


def test_parser_play() -> None:
    """Test parser behavior for 'play' command."""
    args = parse_args(["play", "--config", "config.json"])
    assert args.command == "play"
    assert args.config == "config.json"


def test_parser_evaluate() -> None:
    """Test parser behavior for 'evaluate' command."""
    args = parse_args(
        ["evaluate", "--config", "config.json", "--checkpoint", "latest.pt"]
    )
    assert args.command == "evaluate"
    assert args.config == "config.json"
    assert args.checkpoint == "latest.pt"


def test_parser_version() -> None:
    """Test parser behavior for 'version' command."""
    args = parse_args(["version"])
    assert args.command == "version"


def test_parser_missing_args() -> None:
    """Test parser behavior with missing required arguments."""
    with pytest.raises(SystemExit):
        parse_args(["train"])


def test_parser_invalid_command() -> None:
    """Test parser behavior with an invalid command."""
    with pytest.raises(SystemExit):
        parse_args(["invalid_command"])


def test_handle_train_success(mock_builder: MagicMock, temp_config_path: Path) -> None:
    """Test 'train' command handler."""
    args = argparse.Namespace(config=str(temp_config_path))
    handle_train(args, mock_builder)

    mock_builder.build_training_runner.assert_called_once_with(temp_config_path)
    mock_builder.build_training_runner.return_value.run_episode.assert_called_once()


def test_handle_train_missing_file(mock_builder: MagicMock) -> None:
    """Test 'train' command handler with missing config file."""
    args = argparse.Namespace(config="nonexistent.json")
    with pytest.raises(CliCommandError, match="Configuration file not found"):
        handle_train(args, mock_builder)


def test_handle_play_success(mock_builder: MagicMock, temp_config_path: Path) -> None:
    """Test 'play' command handler."""
    args = argparse.Namespace(config=str(temp_config_path))
    handle_play(args, mock_builder)

    mock_builder.build_inference_runner.assert_called_once_with(temp_config_path)
    mock_builder.build_inference_runner.return_value.run_episode.assert_called_once()


def test_handle_evaluate_success(
    mock_builder: MagicMock, temp_config_path: Path, temp_checkpoint_path: Path
) -> None:
    """Test 'evaluate' command handler."""
    args = argparse.Namespace(
        config=str(temp_config_path), checkpoint=str(temp_checkpoint_path)
    )
    handle_evaluate(args, mock_builder)

    mock_builder.build_evaluator.assert_called_once_with(
        temp_config_path, temp_checkpoint_path
    )
    mock_builder.build_evaluator.return_value.evaluate.assert_called_once()


def test_main_success_exit_code(
    mock_builder: MagicMock, temp_config_path: Path
) -> None:
    """Test main() returns 0 on success."""
    exit_code = main(["train", "--config", str(temp_config_path)], mock_builder)
    assert exit_code == 0


def test_main_failure_exit_code(mock_builder: MagicMock) -> None:
    """Test main() returns 1 on CliError."""
    # missing config file will trigger CliCommandError in handle_train
    exit_code = main(["train", "--config", "nonexistent.json"], mock_builder)
    assert exit_code == 1


@patch("cookie_agent.cli.main.handle_version")
def test_main_version(mock_handle_version: MagicMock, mock_builder: MagicMock) -> None:
    """Test main() invokes version handler correctly."""
    exit_code = main(["version"], mock_builder)
    assert exit_code == 0
    mock_handle_version.assert_called_once()


def test_main_invalid_args() -> None:
    """Test main() with invalid arguments returns non-zero."""
    # argparse raises SystemExit(2) for missing arguments
    exit_code = main(["train"])
    assert exit_code == 2


@patch("cookie_agent.cli.main.parse_args")
def test_main_keyboard_interrupt(
    mock_parse: MagicMock, mock_builder: MagicMock
) -> None:
    """Test main() handles KeyboardInterrupt correctly and returns exit code 130."""
    mock_parse.side_effect = KeyboardInterrupt

    exit_code = main(["train", "--config", "dummy.json"], mock_builder)

    assert exit_code == 130
    mock_builder.build_training_runner.assert_not_called()
