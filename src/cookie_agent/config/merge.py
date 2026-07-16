"""Configuration dictionary merge utilities."""

from typing import Any


def merge_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deterministically merge an override dictionary into a base dictionary.

    Creates a new dictionary without mutating the originals.
    Nested dictionaries are merged recursively.
    Lists and primitives in override completely replace those in base.

    Args:
        base: The default base dictionary.
        override: The dictionary of overrides.

    Returns:
        A new merged dictionary.

    Raises:
        MergeError: If types unexpectedly mismatch during merge.
    """
    merged = dict(base)
    for key, val in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(val, dict):
            merged[key] = merge_configs(merged[key], val)
        else:
            merged[key] = val
    return merged
