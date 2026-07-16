"""Builders generating argument list parameters for ADB CLI commands."""


def build_tap(x: int, y: int) -> tuple[str, ...]:
    """Build adb shell arguments for a screen tap coordinate action.

    Args:
        x: Target horizontal coordinate.
        y: Target vertical coordinate.

    Returns:
        tuple[str, ...]: Argument options to execute.
    """
    return ("shell", "input", "tap", str(x), str(y))


def build_swipe(
    x1: int, y1: int, x2: int, y2: int, duration_ms: int
) -> tuple[str, ...]:
    """Build adb shell arguments representing a screen swipe gesture event.

    Args:
        x1: Horizontal start coordinate.
        y1: Vertical start coordinate.
        x2: Horizontal end coordinate.
        y2: Vertical end coordinate.
        duration_ms: Total duration of gesture swipe.

    Returns:
        tuple[str, ...]: Argument options to execute.
    """
    return (
        "shell",
        "input",
        "swipe",
        str(x1),
        str(y1),
        str(x2),
        str(y2),
        str(duration_ms),
    )


def build_keyevent(keycode: str | int) -> tuple[str, ...]:
    """Build adb shell arguments to execute a specific key event code step.

    Args:
        keycode: Android hardware key event identifier.

    Returns:
        tuple[str, ...]: Argument options to execute.
    """
    return ("shell", "input", "keyevent", str(keycode))


def build_shell(cmd: str) -> tuple[str, ...]:
    """Build custom shell script execution parameters.

    Args:
        cmd: Arbitrary shell command script.

    Returns:
        tuple[str, ...]: Argument options to execute.
    """
    return ("shell", cmd)
