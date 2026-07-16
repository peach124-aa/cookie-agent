"""Common type aliases for the Cookie Agent core package."""

from typing import NewType

FrameId = NewType("FrameId", int)
TrackId = NewType("TrackId", int)
StepId = NewType("StepId", int)
Timestamp = NewType("Timestamp", float)
LaneIndex = NewType("LaneIndex", int)
Confidence = NewType("Confidence", float)
