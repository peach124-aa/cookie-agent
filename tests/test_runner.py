"""Tests for the Inference Runner module."""

from unittest.mock import MagicMock

import pytest
from cookie_agent.core.actions import ActionIntent, ADBCommand, InputKind, IntentType
from cookie_agent.core.frame import Frame
from cookie_agent.core.state import GameState, JumpPhase, PlayerState
from cookie_agent.core.types import FrameId, Timestamp
from cookie_agent.runner.exceptions import LoopStoppedError, PipelineError
from cookie_agent.runner.loop import InferenceLoop
from cookie_agent.runner.runner import InferenceRunner


@pytest.fixture()
def mock_capture() -> MagicMock:
    """Mock CaptureSource."""
    mock = MagicMock()
    mock.capture.return_value = Frame(
        frame_id=FrameId(1),
        timestamp=Timestamp(1000),
        width=1920,
        height=1080,
        data=b"",
    )
    return mock


@pytest.fixture()
def mock_detector() -> MagicMock:
    """Mock Detector."""
    mock = MagicMock()
    mock.detect.return_value = []
    return mock


@pytest.fixture()
def mock_tracker() -> MagicMock:
    """Mock Tracker."""
    mock = MagicMock()
    mock.track.return_value = []
    return mock


@pytest.fixture()
def mock_state_builder() -> MagicMock:
    """Mock StateBuilder."""
    mock = MagicMock()
    mock.build.return_value = GameState(
        schema_version=1,
        player=PlayerState(
            velocity_x=0.0,
            velocity_y=0.0,
            jump_phase=JumpPhase.GROUNDED,
            airborne=False,
            grounded=True,
            time_since_last_jump=0.0,
            time_since_last_damage=0.0,
            relay_available=False,
        ),
        objects=[],
        scroll_speed=10.0,
        scroll_distance=100.0,
    )
    return mock


@pytest.fixture()
def mock_policy() -> MagicMock:
    """Mock Policy."""
    mock = MagicMock()
    mock.select_action.return_value = ActionIntent(intent=IntentType.IDLE)
    return mock


@pytest.fixture()
def mock_planner() -> MagicMock:
    """Mock ActionPlanner."""
    mock = MagicMock()
    mock.plan.return_value = [
        ADBCommand(kind=InputKind.TOUCH_DOWN, x=0, y=0, hold_ms=0, delay_ms=0)
    ]
    return mock


@pytest.fixture()
def mock_device() -> MagicMock:
    """Mock DeviceController."""
    mock = MagicMock()
    mock.execute.return_value = True
    return mock


@pytest.fixture()
def runner(
    mock_capture: MagicMock,
    mock_detector: MagicMock,
    mock_tracker: MagicMock,
    mock_state_builder: MagicMock,
    mock_policy: MagicMock,
    mock_planner: MagicMock,
    mock_device: MagicMock,
) -> InferenceRunner:
    """Provide a configured InferenceRunner for testing."""
    return InferenceRunner(
        capture_source=mock_capture,
        detector=mock_detector,
        tracker=mock_tracker,
        state_builder=mock_state_builder,
        policy=mock_policy,
        planner=mock_planner,
        device_controller=mock_device,
    )


def test_runner_execution_order(runner: InferenceRunner) -> None:
    """Test that all dependencies are called in the correct order."""
    result = runner.run_step()

    runner._capture_source.capture.assert_called_once()  # type: ignore
    runner._detector.detect.assert_called_once()  # type: ignore
    runner._tracker.track.assert_called_once()  # type: ignore
    runner._state_builder.build.assert_called_once()  # type: ignore
    runner._policy.select_action.assert_called_once()  # type: ignore
    runner._planner.plan.assert_called_once()  # type: ignore
    runner._device_controller.execute.assert_called_once()  # type: ignore

    assert result.metrics.step_id == 1
    assert result.metrics.total_pipeline_time_ms >= 0


def test_runner_execution_failure(
    runner: InferenceRunner, mock_device: MagicMock
) -> None:
    """Test that PipelineError is raised if execution fails."""
    mock_device.execute.return_value = False
    with pytest.raises(PipelineError, match=r"Device controller failed"):
        runner.run_step()


def test_capture_failure(runner: InferenceRunner) -> None:
    """Test that capture failures propagate and halt the pipeline."""
    error = Exception("Capture failed")
    runner._capture_source.capture.side_effect = error  # type: ignore

    with pytest.raises(Exception, match="Capture failed"):
        runner.run_step()

    runner._capture_source.capture.assert_called_once()  # type: ignore
    runner._detector.detect.assert_not_called()  # type: ignore
    runner._tracker.track.assert_not_called()  # type: ignore
    runner._planner.plan.assert_not_called()  # type: ignore
    runner._device_controller.execute.assert_not_called()  # type: ignore


def test_loop_run_forever(runner: InferenceRunner) -> None:
    """Test that InferenceLoop runs correctly and stops on signal."""
    loop = InferenceLoop(runner)

    original_run_step = runner.run_step

    def mock_run_step() -> None:
        if runner._step_counter >= 3:
            raise LoopStoppedError()
        original_run_step()

    object.__setattr__(runner, "run_step", mock_run_step)

    metrics = loop.run_forever()
    assert metrics.step_count == 3
    assert metrics.frame_count == 3
    assert not loop._is_running


def test_loop_keyboard_interrupt(runner: InferenceRunner) -> None:
    """Test that InferenceLoop stops on KeyboardInterrupt."""
    loop = InferenceLoop(runner)

    def mock_run_step() -> None:
        raise KeyboardInterrupt

    object.__setattr__(runner, "run_step", mock_run_step)

    metrics = loop.run_forever()
    assert metrics.step_count == 0
    assert not loop._is_running
