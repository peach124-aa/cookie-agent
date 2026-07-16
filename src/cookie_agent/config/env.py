"""Environment variables overrides parsing helper."""

import os
from typing import Any

from cookie_agent.config.exceptions import ConfigValidationError


def _cast_unknown_val(val_str: str) -> Any:
    """Cast string values to basic types when target template is missing."""
    val_lower = val_str.lower().strip()
    if val_lower in {"true", "yes", "on"}:
        return True
    if val_lower in {"false", "no", "off"}:
        return False
    try:
        if "." in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str


def _cast_val(val_str: str, target_example: Any) -> Any:
    """Cast string value to match the type of target_example.

    Args:
        val_str: The environment variable string value.
        target_example: Example object of target type.

    Returns:
        Any: Casted value matching target type.

    Raises:
        ConfigValidationError: If casting fails or is invalid.
    """
    if isinstance(target_example, bool):
        val_lower = val_str.lower().strip()
        if val_lower in {"true", "1", "yes", "on"}:
            return True
        if val_lower in {"false", "0", "no", "off"}:
            return False
        raise ConfigValidationError(
            f"Invalid boolean value: '{val_str}'. "
            "Expected true/false, 1/0, yes/no, on/off."
        )
    if isinstance(target_example, int):
        try:
            return int(val_str)
        except ValueError as e:
            raise ConfigValidationError(f"Invalid integer value: '{val_str}'") from e
    if isinstance(target_example, float):
        try:
            return float(val_str)
        except ValueError as e:
            raise ConfigValidationError(f"Invalid float value: '{val_str}'") from e
    return val_str


def override_from_env(section_name: str, cfg: dict[str, Any]) -> None:
    """Override config section fields using COOKIE_AGENT_<SECTION>__ variables."""
    prefix = f"COOKIE_AGENT_{section_name.upper()}__"
    for env_key, env_val in os.environ.items():
        if env_key.startswith(prefix):
            path_str = env_key[len(prefix) :].lower()
            parts = path_str.split("__")

            curr = cfg
            for part in parts[:-1]:
                if part not in curr or not isinstance(curr[part], dict):
                    curr[part] = {}
                curr = curr[part]

            last_part = parts[-1]
            if last_part in curr:
                curr[last_part] = _cast_val(env_val, curr[last_part])
            else:
                curr[last_part] = _cast_unknown_val(env_val)
