"""Unit tests for the Replay Recorder module."""

import io
import struct
from pathlib import Path
from typing import cast

import pytest
from cookie_agent.core.actions import ADBCommand, InputKind
from cookie_agent.core.frame import Frame
from cookie_agent.core.protocols import ReplayObserver
from cookie_agent.core.types import FrameId, Timestamp
from cookie_agent.replay import (
    ReplayFormatError,
    ReplayFrameMetadata,
    ReplayReader,
    ReplayRecorder,
    ReplaySessionMetadata,
    ReplayWriteError,
    ReplayWriter,
)


def test_metadata_instantiation() -> None:
    """Verify metadata objects preserve passed attributes."""
    sess = ReplaySessionMetadata("sess_123", 1280, 720, "BGRA")
    assert sess.session_id == "sess_123"
    assert sess.width == 1280
    assert sess.height == 720
    assert sess.format == "BGRA"

    frm = ReplayFrameMetadata(5, 100.5, 640, 480, "RGB")
    assert frm.frame_id == 5
    assert frm.timestamp == 100.5
    assert frm.width == 640
    assert frm.height == 480
    assert frm.format == "RGB"


def test_writer_and_reader_cycle() -> None:
    """Verify that writer and reader serialize/deserialize correctly."""
    stream = io.BytesIO()

    # Create writer
    writer = ReplayWriter(stream)
    session_meta = ReplaySessionMetadata("test_session", 1280, 720, "BGRA")
    writer.write_header(session_meta)

    # Frame 1
    f1 = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, 1000.1),
        width=1280,
        height=720,
        data=b"pixel_data_1",
    )
    cmds1 = [
        ADBCommand(kind=InputKind.TOUCH_DOWN, x=100, y=200, hold_ms=50, delay_ms=10)
    ]
    writer.write_frame(f1, cmds1)

    # Frame 2 (no commands)
    f2 = Frame(
        frame_id=cast(FrameId, 2),
        timestamp=cast(Timestamp, 1000.2),
        width=1280,
        height=720,
        data=b"pixel_data_2",
    )
    writer.write_frame(f2)

    # Re-read
    stream.seek(0)
    reader = ReplayReader(stream)

    read_session = reader.read_header()
    assert read_session.session_id == "test_session"
    assert read_session.width == 1280
    assert read_session.height == 720
    assert read_session.format == "BGRA"

    # read frames
    records = list(reader.read_frames())
    assert len(records) == 2

    # Verify frame 1
    rf1, rcmds1 = records[0]
    assert rf1.frame_id == 1
    assert rf1.timestamp == 1000.1
    assert rf1.width == 1280
    assert rf1.height == 720
    assert rf1.data == b"pixel_data_1"
    assert len(rcmds1) == 1
    assert rcmds1[0].kind == InputKind.TOUCH_DOWN
    assert rcmds1[0].x == 100
    assert rcmds1[0].y == 200

    # Verify frame 2
    rf2, rcmds2 = records[1]
    assert rf2.frame_id == 2
    assert rf2.timestamp == 1000.2
    assert rf2.data == b"pixel_data_2"
    assert len(rcmds2) == 0


def test_unwritten_header_errors() -> None:
    """Verify writing frame before header raises error."""
    stream = io.BytesIO()
    writer = ReplayWriter(stream)
    f = Frame(cast(FrameId, 1), cast(Timestamp, 0.0), 10, 10, b"data")
    with pytest.raises(ReplayWriteError, match="Header must be written"):
        writer.write_frame(f)


def test_write_header_twice_error() -> None:
    """Verify writing header twice raises error."""
    stream = io.BytesIO()
    writer = ReplayWriter(stream)
    meta = ReplaySessionMetadata("sess", 10, 10, "BGRA")
    writer.write_header(meta)
    with pytest.raises(ReplayWriteError, match="Header has already been written"):
        writer.write_header(meta)


def test_corrupted_header_format_error() -> None:
    """Verify that corrupted headers raise format errors."""
    stream = io.BytesIO(b"INVALID_MAGIC_BYTES_SHORT")
    reader = ReplayReader(stream)
    with pytest.raises(ReplayFormatError, match="Invalid magic header"):
        reader.read_header()


def test_unsupported_version_format_error() -> None:
    """Verify incompatible file format version triggers format errors."""
    stream = io.BytesIO()
    writer = ReplayWriter(stream)
    meta = ReplaySessionMetadata("sess", 10, 10, "BGRA")
    writer.write_header(meta)

    # Mutate version bytes in stream manually to version 99
    data = bytearray(stream.getvalue())
    # magic is 8 bytes, next 2 bytes is version
    data[8:10] = struct.pack(">H", 99)

    reader = ReplayReader(io.BytesIO(data))
    with pytest.raises(ReplayFormatError, match="Unsupported replay version"):
        reader.read_header()


def test_recorder_protocol_conformance() -> None:
    """Verify ReplayRecorder conforms to ReplayObserver protocol."""
    writer = ReplayWriter(io.BytesIO())
    recorder = ReplayRecorder(writer)
    assert isinstance(recorder, ReplayObserver)


def test_recorder_observe() -> None:
    """Verify observer method routes parameters correctly."""
    stream = io.BytesIO()
    writer = ReplayWriter(stream)
    meta = ReplaySessionMetadata("sess", 10, 10, "BGRA")
    writer.write_header(meta)

    recorder = ReplayRecorder(writer)
    f = Frame(cast(FrameId, 1), cast(Timestamp, 100.0), 10, 10, b"pixels")
    recorder.observe(f, [], {})

    # Check reader extracts it
    stream.seek(0)
    reader = ReplayReader(stream)
    frames = list(reader.read_frames())
    assert len(frames) == 1
    assert frames[0][0].data == b"pixels"


def test_writer_reader_file_path(tmp_path: Path) -> None:
    """Verify writer/reader connection via temporary file paths and close calls."""
    filepath = tmp_path / "replay.bin"

    # Write using filepath string
    writer = ReplayWriter(str(filepath))
    meta = ReplaySessionMetadata("file_sess", 10, 10, "BGRA")
    writer.write_header(meta)
    f = Frame(cast(FrameId, 1), cast(Timestamp, 123.4), 10, 10, b"some_bytes")
    writer.write_frame(f)
    writer.close()

    # Read using Path object
    reader = ReplayReader(filepath)
    meta_read = reader.read_header()
    assert meta_read.session_id == "file_sess"
    frames = list(reader.read_frames())
    assert len(frames) == 1
    assert frames[0][0].data == b"some_bytes"
    reader.close()
