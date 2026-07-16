"""Dictionary deep merging helper."""

import copy
from typing import Any


def deep_merge(target: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge source dictionary into target without mutating inputs.

    Args:
        target: Base dictionary.
        source: Override dictionary.

    Returns:
        dict[str, Any]: A newly created merged dictionary.
    """
    res = copy.deepcopy(target)
    for key, val in source.items():
        if isinstance(val, dict) and isinstance(res.get(key), dict):
            res[key] = deep_merge(res[key], val)
        else:
            res[key] = copy.deepcopy(val)
    return res
