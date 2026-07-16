"""Metadata dataclasses for Replay sessions and records."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReplaySessionMetadata:
    """Consolidated metadata details for a replay recording session."""

    session_id: str
    width: int
    height: int
    format: str


@dataclass(frozen=True, slots=True)
class ReplayFrameMetadata:
    """Individual metadata record associated with each recorded frame."""

    frame_id: int
    timestamp: float
    width: int
    height: int
    format: str
