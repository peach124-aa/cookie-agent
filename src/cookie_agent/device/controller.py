"""High-level Device Controller implementing target protocols."""

import time
from collections.abc import Sequence

from cookie_agent.core.actions import ADBCommand, InputKind
from cookie_agent.core.protocols import DeviceController
from cookie_agent.device.adb_client import ADBClient
from cookie_agent.device.commands import (
    build_keyevent,
    build_swipe,
    build_tap,
)


class ADBDeviceController(DeviceController):
    """Execution wrapper translating tap command logs to shell CLI inputs."""

    def __init__(self, adb_client: ADBClient):
        """Initialize ADBDeviceController.

        Args:
            adb_client: Target ADB connection wrapper.
        """
        self.adb_client = adb_client

    def execute(self, commands: Sequence[ADBCommand]) -> bool:
        """Sequential execution loop translating touch events into shell triggers.

        Args:
            commands: Sequence of ADBCommands.

        Returns:
            bool: True if execution succeeded, else False.
        """
        for cmd in commands:
            if cmd.kind == InputKind.TOUCH_DOWN:
                # Emulate touch down and hold using a swipe at same coordinates
                args = build_swipe(cmd.x, cmd.y, cmd.x, cmd.y, cmd.hold_ms)
            elif cmd.kind == InputKind.TOUCH_UP:
                # Emulate release / click action
                args = build_tap(cmd.x, cmd.y)
            else:  # TOUCH_MOVE
                # Emulate path drag / hold
                args = build_swipe(cmd.x, cmd.y, cmd.x, cmd.y, cmd.hold_ms)

            self.adb_client.shell(args)

            if cmd.delay_ms > 0:
                time.sleep(cmd.delay_ms / 1000.0)
        return True

    def tap(self, x: int, y: int) -> None:
        """Inject tap command event.

        Args:
            x: Target horizontal coordinate.
            y: Target vertical coordinate.
        """
        self.adb_client.shell(build_tap(x, y))

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int) -> None:
        """Inject drag swipe event.

        Args:
            x1: Horizontal start coordinate.
            y1: Vertical start coordinate.
            x2: Horizontal end coordinate.
            y2: Vertical end coordinate.
            duration_ms: Total duration of gesture swipe.
        """
        self.adb_client.shell(build_swipe(x1, y1, x2, y2, duration_ms))

    def key_event(self, keycode: str | int) -> None:
        """Inject generic key event code.

        Args:
            keycode: Key code identifier.
        """
        self.adb_client.shell(build_keyevent(keycode))

    def press_home(self) -> None:
        """Inject key code event mapping KEYCODE_HOME."""
        self.key_event(3)

    def press_back(self) -> None:
        """Inject key code event mapping KEYCODE_BACK."""
        self.key_event(4)
