"""Unit tests for the Capture Module."""

import time
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from cookie_agent.capture import (
    CaptureTimeoutError,
    FrameBuffer,
    WindowNotFoundError,
    WindowsCapture,
)
from cookie_agent.core.frame import Frame
from cookie_agent.core.protocols import CaptureSource
from cookie_agent.core.types import FrameId, Timestamp


def test_frame_buffer_push_pop() -> None:
    """Verify FrameBuffer basic push/pop functionality."""
    buf = FrameBuffer(max_size=3)
    assert buf.qsize() == 0

    f1 = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, time.time()),
        width=10,
        height=10,
        data=b"frame1",
    )
    f2 = Frame(
        frame_id=cast(FrameId, 2),
        timestamp=cast(Timestamp, time.time()),
        width=10,
        height=10,
        data=b"frame2",
    )

    buf.push(f1)
    buf.push(f2)
    assert buf.qsize() == 2

    # Pop oldest (FIFO)
    assert buf.pop() == f1
    assert buf.qsize() == 1
    assert buf.pop() == f2
    assert buf.qsize() == 0


def test_frame_buffer_overflow() -> None:
    """Verify that buffer drops oldest frame when limit is exceeded."""
    buf = FrameBuffer(max_size=2)
    f1 = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, time.time()),
        width=10,
        height=10,
        data=b"1",
    )
    f2 = Frame(
        frame_id=cast(FrameId, 2),
        timestamp=cast(Timestamp, time.time()),
        width=10,
        height=10,
        data=b"2",
    )
    f3 = Frame(
        frame_id=cast(FrameId, 3),
        timestamp=cast(Timestamp, time.time()),
        width=10,
        height=10,
        data=b"3",
    )

    buf.push(f1)
    buf.push(f2)
    # Exceed capacity: f1 (oldest) should be dropped
    buf.push(f3)

    assert buf.qsize() == 2
    assert buf.pop() == f2
    assert buf.pop() == f3


def test_frame_buffer_clear() -> None:
    """Verify clear method resets the queue."""
    buf = FrameBuffer(max_size=5)
    f1 = Frame(
        frame_id=cast(FrameId, 1),
        timestamp=cast(Timestamp, time.time()),
        width=10,
        height=10,
        data=b"1",
    )
    buf.push(f1)
    assert buf.qsize() == 1
    buf.clear()
    assert buf.qsize() == 0


def test_frame_buffer_pop_timeout() -> None:
    """Verify that pop times out on empty queue."""
    buf = FrameBuffer(max_size=5)
    with pytest.raises(CaptureTimeoutError):
        buf.pop(timeout=0.05)


def test_frame_buffer_invalid_size() -> None:
    """Verify FrameBuffer raises error on non-positive sizes."""
    with pytest.raises(ValueError, match="max_size must be positive"):
        FrameBuffer(max_size=0)
    with pytest.raises(ValueError, match="max_size must be positive"):
        FrameBuffer(max_size=-5)


def test_capture_source_protocol_conformance() -> None:
    """Verify that WindowsCapture conforms to the CaptureSource protocol."""
    # Ensure WindowsCapture is runtime checkable as CaptureSource
    assert isinstance(WindowsCapture("MuMu", 1280, 720), CaptureSource)


@patch("cookie_agent.capture.windows_capture.win32gui")
@patch("cookie_agent.capture.windows_capture.win32ui")
@patch("cookie_agent.capture.windows_capture.win32con")
def test_windows_capture_find_window_not_found(
    mock_win32con: MagicMock, mock_win32ui: MagicMock, mock_win32gui: MagicMock
) -> None:
    """Verify WindowNotFoundError triggers when target HWND is absent."""
    _ = (mock_win32con, mock_win32ui)
    # Setup mocks
    mock_win32gui.FindWindow.return_value = 0

    capture = WindowsCapture("NonExistentPlayer", 1280, 720)
    with pytest.raises(WindowNotFoundError):
        capture.capture()


@patch("cookie_agent.capture.windows_capture.win32gui")
@patch("cookie_agent.capture.windows_capture.win32ui")
@patch("cookie_agent.capture.windows_capture.win32con")
def test_windows_capture_successful(
    mock_win32con: MagicMock, mock_win32ui: MagicMock, mock_win32gui: MagicMock
) -> None:
    """Verify successful frame capture mock loop and conversion to RGB."""
    _ = mock_win32con
    # Setup mocks
    mock_win32gui.FindWindow.return_value = 123
    mock_win32gui.GetWindowDC.return_value = 456

    mock_mfc_dc = MagicMock()
    mock_win32ui.CreateDCFromHandle.return_value = mock_mfc_dc

    mock_save_dc = MagicMock()
    mock_mfc_dc.CreateCompatibleDC.return_value = mock_save_dc

    mock_save_bitmap = MagicMock()
    mock_win32ui.CreateBitmap.return_value = mock_save_bitmap

    # Generate dummy BGRA bytes for 2x2 resolution (16 bytes total)
    # B, G, R, A = 1, 2, 3, 255 for all pixels
    bgra_data = bytes([1, 2, 3, 255] * 4)
    mock_save_bitmap.GetBitmapBits.return_value = bgra_data

    capture = WindowsCapture("MuMuPlayer", width=2, height=2)
    frame = capture.capture()

    assert frame is not None
    assert frame.width == 2
    assert frame.height == 2
    assert frame.frame_id == 1
    assert isinstance(frame.timestamp, float)
    assert frame.resolution == (2, 2)

    # Verify raw BGRA data is returned directly without conversion
    assert frame.data == bgra_data

    # Clean up
    capture.close()
