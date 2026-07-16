"""ADB CLI client wrapper via subprocess execution."""

import subprocess
from collections.abc import Sequence

from cookie_agent.device.exceptions import (
    ADBCommandError,
    DeviceTimeoutError,
)


class ADBClient:
    """Thin wrapper invoking subprocess commands against the adb executable."""

    def __init__(self, adb_path: str = "adb", serial: str | None = None):
        """Initialize ADBClient.

        Args:
            adb_path: Command path targeting the adb executable.
            serial: Targeted device serial configuration tag.
        """
        self.adb_path = adb_path
        self.serial = serial
        self.default_timeout = 10.0

    def _run_cmd(self, args: Sequence[str], timeout: float | None = None) -> str:
        """Run standard target adb subcommand.

        Args:
            args: Command arguments list.
            timeout: Subprocess timeout in seconds.

        Returns:
            str: Stdout output text.

        Raises:
            DeviceTimeoutError: On command timeouts.
            ADBCommandError: On command non-zero statuses or FileNotFoundError.
        """
        t = timeout if timeout is not None else self.default_timeout
        cmd = [self.adb_path]
        if self.serial:
            cmd.extend(["-s", self.serial])
        cmd.extend(args)

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=t,
            )
        except subprocess.TimeoutExpired as e:
            raise DeviceTimeoutError(f"ADB command timed out: {cmd}") from e
        except FileNotFoundError as e:
            raise ADBCommandError(
                f"ADB executable not found at path: {self.adb_path}"
            ) from e

        if res.returncode != 0:
            raise ADBCommandError(
                f"ADB command {cmd} failed with exit code {res.returncode}. "
                f"stderr: {res.stderr}"
            )
        return res.stdout

    def connect(self) -> None:
        """Establish connection with the target serial device."""
        if not self.serial:
            return
        cmd = [self.adb_path, "connect", self.serial]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.default_timeout,
            )
        except subprocess.TimeoutExpired as e:
            raise DeviceTimeoutError(f"ADB connect timed out: {cmd}") from e

        if res.returncode != 0:
            raise ADBCommandError(
                f"Failed to connect to device {self.serial}: {res.stderr}"
            )

    def disconnect(self) -> None:
        """Disconnect the target serial device connection."""
        if not self.serial:
            return
        cmd = [self.adb_path, "disconnect", self.serial]
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.default_timeout,
            )
        except subprocess.TimeoutExpired as e:
            raise DeviceTimeoutError(f"ADB disconnect timed out: {cmd}") from e

    def reconnect(self) -> None:
        """Attempt reconnection resets."""
        self._run_cmd(("reconnect",))

    def shell(self, args: Sequence[str]) -> str:
        """Run adb shell instructions.

        Args:
            args: Target arguments list.

        Returns:
            str: stdout string output.
        """
        if args and args[0] == "shell":
            return self._run_cmd(args)
        return self._run_cmd(["shell", *list(args)])

    def push(self, local_path: str, remote_path: str) -> None:
        """Push local file target to target remote path.

        Args:
            local_path: Local target filepath.
            remote_path: Remote path destination.
        """
        self._run_cmd(["push", local_path, remote_path])

    def pull(self, remote_path: str, local_path: str) -> None:
        """Pull remote files to local filesystems.

        Args:
            remote_path: Remote target filepath.
            local_path: Local destination.
        """
        self._run_cmd(["pull", remote_path, local_path])

    def health_check(self) -> bool:
        """Execute getprop sys.boot_completed to check active emulator statuses.

        Returns:
            bool: True if completed, else False.
        """
        try:
            out = self.shell(["getprop", "sys.boot_completed"])
            return out.strip() == "1"
        except Exception:
            return False
