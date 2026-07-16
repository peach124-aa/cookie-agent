"""Public Device Controller namespace."""

from cookie_agent.device.adb_client import ADBClient
from cookie_agent.device.commands import (
    build_keyevent,
    build_shell,
    build_swipe,
    build_tap,
)
from cookie_agent.device.controller import ADBDeviceController
from cookie_agent.device.exceptions import (
    ADBCommandError,
    DeviceError,
    DeviceNotFoundError,
    DeviceTimeoutError,
)
from cookie_agent.device.parser import (
    parse_devices,
    parse_dumpsys_window_focus,
    parse_wm_size,
)

__all__: list[str] = [
    "ADBClient",
    "ADBCommandError",
    "ADBDeviceController",
    "DeviceError",
    "DeviceNotFoundError",
    "DeviceTimeoutError",
    "build_keyevent",
    "build_shell",
    "build_swipe",
    "build_tap",
    "parse_devices",
    "parse_dumpsys_window_focus",
    "parse_wm_size",
]
