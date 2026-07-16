"""Output parser helpers for ADB CLI outputs."""


def parse_wm_size(output: str) -> tuple[int, int]:
    """Parse Android wm size output returning (width, height) integers.

    Args:
        output: Raw wm size shell output text.

    Returns:
        tuple[int, int]: Screen resolution width and height bounds.

    Raises:
        ValueError: If parsing fails.
    """
    lines = output.strip().split("\n")
    physical_res = None
    override_res = None
    for line in lines:
        if "physical size:" in line.lower():
            parts = line.split(":")[-1].strip().split("x")
            if len(parts) == 2:
                try:
                    physical_res = (int(parts[0].strip()), int(parts[1].strip()))
                except ValueError as e:
                    raise ValueError(
                        f"Invalid integer values in physical size: {line}"
                    ) from e
        elif "override size:" in line.lower():
            parts = line.split(":")[-1].strip().split("x")
            if len(parts) == 2:
                try:
                    override_res = (int(parts[0].strip()), int(parts[1].strip()))
                except ValueError as e:
                    raise ValueError(
                        f"Invalid integer values in override size: {line}"
                    ) from e

    if override_res is not None:
        return override_res
    if physical_res is not None:
        return physical_res

    # Fallback to general scan if neither keyword is explicitly matched
    for line in lines:
        if "size:" in line.lower():
            parts = line.split(":")[-1].strip().split("x")
            if len(parts) == 2:
                try:
                    return int(parts[0].strip()), int(parts[1].strip())
                except ValueError as e:
                    raise ValueError(f"Invalid integer values in: {line}") from e
    raise ValueError(f"Failed to parse wm size from output: {output}")


def parse_devices(output: str) -> list[dict[str, str]]:
    """Parse adb devices outputs into structured serial and status dictionaries.

    Args:
        output: Raw output string of the adb devices command.

    Returns:
        list[dict[str, str]]: List of attached device records.
    """
    devices = []
    lines = output.strip().split("\n")
    # Skip header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append({"serial": parts[0], "status": parts[1]})
    return devices


def parse_dumpsys_window_focus(output: str) -> str:
    """Parse dumpsys window output extracting focus activity/window.

    Args:
        output: Raw dumpsys window output buffer.

    Returns:
        str: Window target title details or empty.
    """
    for line in output.strip().split("\n"):
        if "mcurrentfocus" in line.lower():
            # Handles "mCurrentFocus=Window{...}" or similar variants
            parts = line.split("mCurrentFocus")[-1].strip()
            if parts.startswith("="):
                parts = parts[1:].strip()
            return parts
    return ""
