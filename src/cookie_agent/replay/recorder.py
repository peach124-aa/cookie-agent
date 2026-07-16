"""Recorder implementing ReplayObserver protocol."""

from collections.abc import Sequence

from cookie_agent.core.actions import ADBCommand
from cookie_agent.core.frame import Frame
from cookie_agent.core.protocols import ReplayObserver
from cookie_agent.replay.writer import ReplayWriter


class ReplayRecorder(ReplayObserver):
    """Binds observer flows writing raw frames and commands to active file streams."""

    def __init__(self, writer: ReplayWriter):
        """Initialize ReplayRecorder.

        Args:
            writer: Active ReplayWriter reference.
        """
        self.writer = writer

    def observe(
        self,
        frame: Frame,
        commands: Sequence[ADBCommand],
        metadata: dict[str, bool | float | str],
    ) -> None:
        """Observe step: writes a frame and its corresponding commands to stream.

        Args:
            frame: Raw captured display graphics.
            commands: Emitted tap triggers.
            metadata: Setup parameters (ignored in raw frame writing).
        """
        _ = metadata
        self.writer.write_frame(frame, commands)
