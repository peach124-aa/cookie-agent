"""Unit tests for the ADB Device Controller module."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from cookie_agent.core.actions import ADBCommand, InputKind
from cookie_agent.core.protocols import DeviceController
from cookie_agent.device import (
    ADBClient,
    ADBCommandError,
    ADBDeviceController,
    DeviceTimeoutError,
    build_keyevent,
    build_shell,
    build_swipe,
    build_tap,
    parse_devices,
    parse_dumpsys_window_focus,
    parse_wm_size,
)


def test_command_builders() -> None:
    """Verify that command builders output correct string tuples."""
    assert build_tap(10, 20) == ("shell", "input", "tap", "10", "20")
    assert build_swipe(1, 2, 3, 4, 100) == (
        "shell",
        "input",
        "swipe",
        "1",
        "2",
        "3",
        "4",
        "100",
    )
    assert build_keyevent(4) == ("shell", "input", "keyevent", "4")
    assert build_shell("ls") == ("shell", "ls")


def test_parser_wm_size() -> None:
    """Verify wm size output parsing rules."""
    out = "Physical size: 1280x720\n"
    assert parse_wm_size(out) == (1280, 720)

    out_override = "Physical size: 1920x1080\nOverride size: 1280x720"
    assert parse_wm_size(out_override) == (1280, 720)

    with pytest.raises(ValueError, match="Failed to parse wm size"):
        parse_wm_size("invalid output")

    with pytest.raises(ValueError, match="Invalid integer values"):
        parse_wm_size("Physical size: 1280xabc")


def test_parser_devices() -> None:
    """Verify adb devices parsing."""
    out = "List of devices attached\n127.0.0.1:5555\tdevice\n"
    devices = parse_devices(out)
    assert len(devices) == 1
    assert devices[0]["serial"] == "127.0.0.1:5555"
    assert devices[0]["status"] == "device"


def test_parser_dumpsys_focus() -> None:
    """Verify focused window parsed value."""
    out = "mCurrentFocus=Window{5d1b32d u0 com.kakao.talk/MainActivity}\n"
    assert (
        parse_dumpsys_window_focus(out)
        == "Window{5d1b32d u0 com.kakao.talk/MainActivity}"
    )

    assert parse_dumpsys_window_focus("no focus info") == ""


@patch("subprocess.run")
def test_adb_client_connect_disconnect(mock_run: MagicMock) -> None:
    """Verify adb connect/disconnect parameter lists."""
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    client = ADBClient(serial="127.0.0.1:5555")
    client.connect()
    mock_run.assert_called_with(
        ["adb", "connect", "127.0.0.1:5555"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )

    client.disconnect()
    mock_run.assert_called_with(
        ["adb", "disconnect", "127.0.0.1:5555"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )


@patch("subprocess.run")
def test_adb_client_shell_and_push_pull(mock_run: MagicMock) -> None:
    """Verify adb shell/push/pull commands execute with serial prefixes."""
    mock_run.return_value = MagicMock(returncode=0, stdout="success\n", stderr="")

    client = ADBClient(serial="127.0.0.1:5555")
    res = client.shell(["getprop", "sys.boot_completed"])
    assert res == "success\n"
    mock_run.assert_called_with(
        ["adb", "-s", "127.0.0.1:5555", "shell", "getprop", "sys.boot_completed"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )

    client.push("local.txt", "remote.txt")
    mock_run.assert_called_with(
        ["adb", "-s", "127.0.0.1:5555", "push", "local.txt", "remote.txt"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )

    client.pull("remote.txt", "local.txt")
    mock_run.assert_called_with(
        ["adb", "-s", "127.0.0.1:5555", "pull", "remote.txt", "local.txt"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )


@patch("subprocess.run")
def test_adb_client_failures(mock_run: MagicMock) -> None:
    """Verify that failures raise customized exceptions."""
    # Test error exit status
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error message")
    client = ADBClient(serial="127.0.0.1:5555")
    with pytest.raises(ADBCommandError):
        client.shell(["invalid_cmd"])

    # Test connect fail
    with pytest.raises(ADBCommandError):
        client.connect()

    # Test timeout
    mock_run.side_effect = subprocess.TimeoutExpired(["adb"], timeout=10.0)
    with pytest.raises(DeviceTimeoutError):
        client.shell(["sleep", "20"])

    # Test connect timeout
    with pytest.raises(DeviceTimeoutError):
        client.connect()

    # Test disconnect timeout
    with pytest.raises(DeviceTimeoutError):
        client.disconnect()


@patch("subprocess.run")
def test_adb_client_health_check(mock_run: MagicMock) -> None:
    """Verify health check returns True on completed boot state."""
    client = ADBClient(serial="127.0.0.1:5555")

    mock_run.return_value = MagicMock(returncode=0, stdout="1\n", stderr="")
    assert client.health_check() is True

    mock_run.return_value = MagicMock(returncode=0, stdout="0\n", stderr="")
    assert client.health_check() is False

    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
    assert client.health_check() is False


def test_device_controller_protocol_conformance() -> None:
    """Verify that ADBDeviceController conforms to DeviceController protocol."""
    client = ADBClient()
    ctrl = ADBDeviceController(client)
    assert isinstance(ctrl, DeviceController)


@patch("subprocess.run")
def test_controller_helpers(mock_run: MagicMock) -> None:
    """Verify high-level actions map to adb subprocess command targets."""
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    client = ADBClient(serial="127.0.0.1:5555")
    ctrl = ADBDeviceController(client)

    ctrl.tap(10, 20)
    mock_run.assert_called_with(
        ["adb", "-s", "127.0.0.1:5555", "shell", "input", "tap", "10", "20"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )

    ctrl.swipe(1, 2, 3, 4, 100)
    mock_run.assert_called_with(
        [
            "adb",
            "-s",
            "127.0.0.1:5555",
            "shell",
            "input",
            "swipe",
            "1",
            "2",
            "3",
            "4",
            "100",
        ],
        capture_output=True,
        text=True,
        timeout=10.0,
    )

    ctrl.press_home()
    mock_run.assert_called_with(
        ["adb", "-s", "127.0.0.1:5555", "shell", "input", "keyevent", "3"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )

    ctrl.press_back()
    mock_run.assert_called_with(
        ["adb", "-s", "127.0.0.1:5555", "shell", "input", "keyevent", "4"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )


@patch("subprocess.run")
def test_controller_execute(mock_run: MagicMock) -> None:
    """Verify sequence command executions map to touch shell triggers."""
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    client = ADBClient(serial="127.0.0.1:5555")
    ctrl = ADBDeviceController(client)

    commands = [
        ADBCommand(kind=InputKind.TOUCH_DOWN, x=10, y=20, hold_ms=50, delay_ms=10),
        ADBCommand(kind=InputKind.TOUCH_UP, x=10, y=20, hold_ms=0, delay_ms=0),
    ]

    res = ctrl.execute(commands)
    assert res is True
    # Confirm last call was tap (TOUCH_UP)
    mock_run.assert_called_with(
        ["adb", "-s", "127.0.0.1:5555", "shell", "input", "tap", "10", "20"],
        capture_output=True,
        text=True,
        timeout=10.0,
    )
