"""Atomic ADBCommand builders."""

from collections.abc import Sequence

from cookie_agent.core.actions import ADBCommand, InputKind


def tap(x: int, y: int, hold_ms: int = 50, delay_ms: int = 0) -> Sequence[ADBCommand]:
    """Build a tap sequence (touch down, delay, touch up).

    Args:
        x: Target X coordinate.
        y: Target Y coordinate.
        hold_ms: Time between down and up events.
        delay_ms: Pause before the next action.

    Returns:
        A sequence of ADB commands for tapping.
    """
    return [
        ADBCommand(kind=InputKind.TOUCH_DOWN, x=x, y=y, hold_ms=hold_ms, delay_ms=0),
        ADBCommand(kind=InputKind.TOUCH_UP, x=x, y=y, hold_ms=0, delay_ms=delay_ms),
    ]


def hold(x: int, y: int, hold_ms: int, delay_ms: int = 0) -> Sequence[ADBCommand]:
    """Build a hold sequence.

    Args:
        x: Target X coordinate.
        y: Target Y coordinate.
        hold_ms: Time to hold down the touch.
        delay_ms: Pause after release.

    Returns:
        A sequence of ADB commands for holding.
    """
    return [
        ADBCommand(kind=InputKind.TOUCH_DOWN, x=x, y=y, hold_ms=hold_ms, delay_ms=0),
        ADBCommand(kind=InputKind.TOUCH_UP, x=x, y=y, hold_ms=0, delay_ms=delay_ms),
    ]


def swipe(
    start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int
) -> Sequence[ADBCommand]:
    """Build a swipe sequence.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Total duration of the swipe in milliseconds.

    Returns:
        A sequence of ADB commands mimicking a swipe.
    """
    # A simple swipe involves a down, a move, and an up. 
    # For a deterministic baseline, we interpolate a few move points 
    # or just issue one move if the framework handles it.
    # Here we issue a start, move, and end.
    
    # We distribute duration_ms between down and move
    return [
        ADBCommand(
            kind=InputKind.TOUCH_DOWN, 
            x=start_x, y=start_y, hold_ms=0, delay_ms=0
        ),
        ADBCommand(
            kind=InputKind.TOUCH_MOVE, 
            x=end_x, y=end_y, hold_ms=duration_ms, delay_ms=0
        ),
        ADBCommand(
            kind=InputKind.TOUCH_UP, 
            x=end_x, y=end_y, hold_ms=0, delay_ms=0
        ),
    ]


def release(x: int, y: int, delay_ms: int = 0) -> ADBCommand:
    """Build a single release command.

    Args:
        x: X coordinate to release.
        y: Y coordinate to release.
        delay_ms: Pause after releasing.

    Returns:
        A single touch up command.
    """
    return ADBCommand(kind=InputKind.TOUCH_UP, x=x, y=y, hold_ms=0, delay_ms=delay_ms)
