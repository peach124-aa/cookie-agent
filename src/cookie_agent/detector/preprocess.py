"""Preprocessing functions for detector frames in pure Python."""

from cookie_agent.core.frame import Frame


def preprocess_frame(
    frame: Frame, target_size: tuple[int, int] | None = None
) -> list[list[list[float]]]:
    """Preprocess raw Frame bytes into normalized float32 image arrays.

    Args:
        frame: Immutable Frame object.
        target_size: Optional (width, height) resizing target.

    Returns:
        list[list[list[float]]]: Preprocessed normalized float image structure.
    """
    data = frame.data
    w = frame.width
    h = frame.height

    if not data:
        return []

    channels = len(data) // (w * h)
    if channels == 0:
        return []

    target_w, target_h = target_size if target_size is not None else (w, h)

    scale_x = w / target_w
    scale_y = h / target_h

    preprocessed = []
    for ty in range(target_h):
        row = []
        oy = int(ty * scale_y)
        if oy >= h:
            oy = h - 1
        oy_offset = oy * w * channels

        for tx in range(target_w):
            ox = int(tx * scale_x)
            if ox >= w:
                ox = w - 1
            pixel_start = oy_offset + ox * channels

            if channels >= 4:
                b = data[pixel_start]
                g = data[pixel_start + 1]
                r = data[pixel_start + 2]
            elif channels == 3:
                b = data[pixel_start]
                g = data[pixel_start + 1]
                r = data[pixel_start + 2]
            else:
                r = g = b = data[pixel_start]

            row.append([r / 255.0, g / 255.0, b / 255.0])
        preprocessed.append(row)

    return preprocessed
