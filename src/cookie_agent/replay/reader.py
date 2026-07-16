"""Binary stream reader for replay sessions."""

import json
import struct
from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO, cast

from cookie_agent.core.actions import ADBCommand, InputKind
from cookie_agent.core.frame import Frame
from cookie_agent.core.types import FrameId, Timestamp
from cookie_agent.replay.exceptions import ReplayFormatError, ReplayReadError
from cookie_agent.replay.metadata import ReplaySessionMetadata
from cookie_agent.replay.writer import MAGIC, VERSION


class ReplayReader:
    """Reads recorded replay sessions back into structured Frame and command objects."""

    def __init__(self, target: str | Path | BinaryIO):
        """Initialize ReplayReader.

        Args:
            target: Source filepath or open binary file-like object.
        """
        self._owned = False
        if isinstance(target, str | Path):
            try:
                self._file: BinaryIO = Path(target).open("rb")
                self._owned = True
            except OSError as e:
                raise ReplayReadError(f"Failed to open file: {target}") from e
        else:
            self._file = target
        self._header_read = False
        self._session_meta: ReplaySessionMetadata | None = None

    def read_header(self) -> ReplaySessionMetadata:
        """Parse and return session header properties.

        Returns:
            ReplaySessionMetadata: Parsed metadata options.

        Raises:
            ReplayFormatError: If file validation or version checks fail.
            ReplayReadError: If generic read exceptions occur.
        """
        if self._header_read and self._session_meta is not None:
            return self._session_meta

        try:
            magic = self._file.read(len(MAGIC))
            if magic != MAGIC:
                raise ReplayFormatError(f"Invalid magic header: {magic!r}")

            ver_bytes = self._file.read(2)
            if len(ver_bytes) < 2:
                raise ReplayReadError("Unexpected EOF reading version.")
            ver = struct.unpack(">H", ver_bytes)[0]
            if ver != VERSION:
                raise ReplayFormatError(f"Unsupported replay version: {ver}")

            len_bytes = self._file.read(4)
            if len(len_bytes) < 4:
                raise ReplayReadError("Unexpected EOF reading session ID length.")
            sid_len = struct.unpack(">I", len_bytes)[0]
            sid_bytes = self._file.read(sid_len)
            if len(sid_bytes) < sid_len:
                raise ReplayReadError("Unexpected EOF reading session ID.")
            session_id = sid_bytes.decode("utf-8")

            res_bytes = self._file.read(8)
            if len(res_bytes) < 8:
                raise ReplayReadError("Unexpected EOF reading resolution.")
            width, height = struct.unpack(">II", res_bytes)

            flen_bytes = self._file.read(4)
            if len(flen_bytes) < 4:
                raise ReplayReadError("Unexpected EOF reading format length.")
            fmt_len = struct.unpack(">I", flen_bytes)[0]
            fmt_bytes = self._file.read(fmt_len)
            if len(fmt_bytes) < fmt_len:
                raise ReplayReadError("Unexpected EOF reading format.")
            fmt = fmt_bytes.decode("utf-8")

            self._session_meta = ReplaySessionMetadata(
                session_id=session_id, width=width, height=height, format=fmt
            )
            self._header_read = True
            return self._session_meta

        except (OSError, struct.error) as e:
            raise ReplayReadError(f"Read failure parsing header: {e}") from e

    def read_frames(self) -> Iterator[tuple[Frame, list[ADBCommand]]]:
        """Iterate through all recorded frames in the replay stream.

        Yields:
            tuple[Frame, list[ADBCommand]]: Next record pair.

        Raises:
            ReplayReadError: If parsing a frame record block fails.
        """
        if not self._header_read:
            self.read_header()

        while True:
            try:
                hdr_bytes = self._file.read(24)
                if not hdr_bytes:
                    break
                if len(hdr_bytes) < 24:
                    raise ReplayReadError("Incomplete frame record header.")

                frame_id, timestamp, width, height = struct.unpack(">QdII", hdr_bytes)

                flen_bytes = self._file.read(4)
                if len(flen_bytes) < 4:
                    raise ReplayReadError("Unexpected EOF reading frame format length.")
                fmt_len = struct.unpack(">I", flen_bytes)[0]
                fmt_bytes = self._file.read(fmt_len)
                if len(fmt_bytes) < fmt_len:
                    raise ReplayReadError("Unexpected EOF reading frame format.")

                clen_bytes = self._file.read(4)
                if len(clen_bytes) < 4:
                    raise ReplayReadError("Unexpected EOF reading commands length.")
                cmd_len = struct.unpack(">I", clen_bytes)[0]
                cmd_bytes = self._file.read(cmd_len)
                if len(cmd_bytes) < cmd_len:
                    raise ReplayReadError("Unexpected EOF reading commands JSON.")
                cmd_data = json.loads(cmd_bytes.decode("utf-8"))

                commands = []
                for c in cmd_data:
                    commands.append(
                        ADBCommand(
                            kind=InputKind(c["kind"]),
                            x=c["x"],
                            y=c["y"],
                            hold_ms=c["hold_ms"],
                            delay_ms=c["delay_ms"],
                        )
                    )

                dlen_bytes = self._file.read(4)
                if len(dlen_bytes) < 4:
                    raise ReplayReadError("Unexpected EOF reading frame data length.")
                data_len = struct.unpack(">I", dlen_bytes)[0]
                data = self._file.read(data_len)
                if len(data) < data_len:
                    raise ReplayReadError("Unexpected EOF reading frame data buffer.")

                frame = Frame(
                    frame_id=cast(FrameId, frame_id),
                    timestamp=cast(Timestamp, timestamp),
                    width=width,
                    height=height,
                    data=data,
                )
                yield frame, commands

            except (
                OSError,
                struct.error,
                json.JSONDecodeError,
                ValueError,
            ) as e:
                raise ReplayReadError(f"Error parsing frame record block: {e}") from e

    def close(self) -> None:
        """Flush and release stream resources."""
        if self._owned and self._file:
            try:
                self._file.close()
            except OSError as e:
                raise ReplayReadError(f"Failed to close file: {e}") from e
