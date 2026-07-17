"""Windows-specific screen capture source."""

import time
from typing import cast

from cookie_agent.capture.base import BaseCaptureSource
from cookie_agent.capture.exceptions import CaptureError, WindowNotFoundError
from cookie_agent.core.frame import Frame
from cookie_agent.core.types import FrameId, Timestamp

try:
    import win32con  # type: ignore[import-untyped]
    import win32gui  # type: ignore[import-untyped]
    import win32ui  # type: ignore[import-untyped]
except ImportError:
    win32gui = None
    win32ui = None
    win32con = None


class WindowsCapture(BaseCaptureSource):
    """GDI-based capture source targeting Windows emulator windows."""

    def __init__(self, emulator_name: str, width: int, height: int):
        """Initialize the windows capture source.

        Args:
            emulator_name: Name/Title of the emulator window.
            width: Expected width of the frame.
            height: Expected height of the frame.
        """
        self.emulator_name = emulator_name
        self.width = width
        self.height = height
        self._frame_count = 0

    def capture(self) -> Frame:
        """Capture a single frame from the target Windows application window.

        Returns:
            Frame: The captured Frame with raw RGB bytes.

        Raises:
            WindowNotFoundError: If the emulator window is not found.
            CaptureError: If frame capture fails.
        """
        if win32gui is None or win32ui is None or win32con is None:
            raise CaptureError("Windows GDI capture APIs are unavailable.")

        hwnd = win32gui.FindWindow(None, self.emulator_name)
        if not hwnd:
            raise WindowNotFoundError(
                f"Emulator window '{self.emulator_name}' not found."
            )

        hwnd_dc = None
        mfc_dc = None
        save_dc = None
        save_bitmap = None

        try:
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, self.width, self.height)
            save_dc.SelectObject(save_bitmap)

            # Perform GDI BitBlt transfer
            save_dc.BitBlt(
                (0, 0),
                (self.width, self.height),
                mfc_dc,
                (0, 0),
                win32con.SRCCOPY,
            )

            # Retrieve bitmap bits (BGRA format)
            bmp_str = save_bitmap.GetBitmapBits(True)

            self._frame_count += 1
            return Frame(
                frame_id=cast(FrameId, self._frame_count),
                timestamp=cast(Timestamp, time.time()),
                width=self.width,
                height=self.height,
                data=bmp_str,
            )

        except Exception as e:
            raise CaptureError(f"Windows frame capture failed: {e}") from e

        finally:
            if save_dc is not None:
                save_dc.DeleteDC()
            if mfc_dc is not None:
                mfc_dc.DeleteDC()
            if hwnd_dc is not None:
                win32gui.ReleaseDC(hwnd, hwnd_dc)

    def close(self) -> None:
        """Release GDI session references."""
        pass
