"""Device-specific exceptions."""


class DeviceError(Exception):
    """Base exception for all device controller errors."""


class DeviceNotFoundError(DeviceError):
    """Raised when target ADB device serial cannot be resolved or connected."""


class DeviceTimeoutError(DeviceError):
    """Raised when ADB commands exceed specified execution time limits."""


class ADBCommandError(DeviceError):
    """Raised when an ADB command fails or returns a non-zero exit status."""
