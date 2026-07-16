"""Binary stream writer for replay sessions."""

import json
import struct
from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO

from cookie_agent.core.actions import ADBCommand
from cookie_agent.core.frame import Frame
from cookie_agent.replay.exceptions import ReplayWriteError
from cookie_agent.replay.metadata import ReplaySessionMetadata

MAGIC = b"CAREPLAY"
VERSION = 1


class ReplayWriter:
    """Writes replay sessions containing lossless display buffers and commands."""

    def __init__(self, target: str | Path | BinaryIO):
        """Initialize ReplayWriter.

        Args:
            target: Destination file path or open binary file-like object.
        """
        self._owned = False
        if isinstance(target, str | Path):
            try:
                self._file: BinaryIO = Path(target).open("wb")
                self._owned = True
            except OSError as e:
                raise ReplayWriteError(f"Failed to open file: {target}") from e
        else:
            self._file = target
        self._header_written = False

    def write_header(self, meta: ReplaySessionMetadata) -> None:
        """Serialize the file header.

        Args:
            meta: Session configuration parameters.
        """
        if self._header_written:
            raise ReplayWriteError("Header has already been written.")

        try:
            self._file.write(MAGIC)
            self._file.write(struct.pack(">H", VERSION))

            sid_bytes = meta.session_id.encode("utf-8")
            self._file.write(struct.pack(">I", len(sid_bytes)))
            self._file.write(sid_bytes)

            self._file.write(struct.pack(">II", meta.width, meta.height))

            fmt_bytes = meta.format.encode("utf-8")
            self._file.write(struct.pack(">I", len(fmt_bytes)))
            self._file.write(fmt_bytes)

            self._header_written = True
        except OSError as e:
            raise ReplayWriteError(f"OS error writing header: {e}") from e

    def write_frame(self, frame: Frame, commands: Sequence[ADBCommand] = ()) -> None:
        """Write a single frame record block.

        Args:
            frame: Immutable Frame object.
            commands: Optional sequence of associated ADBCommands.
        """
        if not self._header_written:
            raise ReplayWriteError("Header must be written before recording frames.")

        try:
            self._file.write(
                struct.pack(
                    ">QdII",
                    frame.frame_id,
                    frame.timestamp,
                    frame.width,
                    frame.height,
                )
            )

            fmt_bytes = b"BGRA"
            self._file.write(struct.pack(">I", len(fmt_bytes)))
            self._file.write(fmt_bytes)

            cmd_list = []
            for cmd in commands:
                cmd_list.append(
                    {
                        "kind": cmd.kind.value,
                        "x": cmd.x,
                        "y": cmd.y,
                        "hold_ms": cmd.hold_ms,
                        "delay_ms": cmd.delay_ms,
                    }
                )
            cmd_json = json.dumps(cmd_list).encode("utf-8")
            self._file.write(struct.pack(">I", len(cmd_json)))
            self._file.write(cmd_json)

            self._file.write(struct.pack(">I", len(frame.data)))
            self._file.write(frame.data)

        except OSError as e:
            raise ReplayWriteError(f"OS error writing frame record: {e}") from e

    def close(self) -> None:
        """Flush and release stream resources."""
        if self._owned and self._file:
            try:
                self._file.close()
            except OSError as e:
                raise ReplayWriteError(f"Failed to close file: {e}") from e
