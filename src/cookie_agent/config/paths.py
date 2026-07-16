"""Paths configuration for Cookie Agent."""

from pathlib import Path

from cookie_agent.config.config_name import ConfigName

CONFIG_ROOT = Path("configs")
DEFAULT_CONFIG_DIR = CONFIG_ROOT / "defaults"
LOCAL_CONFIG_DIR = CONFIG_ROOT / "local"


def get_config_file(
    config_name: ConfigName,
    local: bool = False,
    config_dir: Path | None = None,
) -> Path:
    """Get the path to a specific configuration file.

    Args:
        config_name: The ConfigName enum representing the target config.
        local: If True, return local overrides path, else defaults path.
        config_dir: Optional custom base directory override.

    Returns:
        Path: The Path to the target YAML file.
    """
    base = config_dir if config_dir is not None else CONFIG_ROOT
    sub = "local" if local else "defaults"
    return base / sub / f"{config_name.value}.yaml"


def config_exists(
    config_name: ConfigName,
    local: bool = False,
    config_dir: Path | None = None,
) -> bool:
    """Check if the configuration file exists on disk.

    Args:
        config_name: The ConfigName enum.
        local: True for local overrides, False for defaults.
        config_dir: Optional custom base directory override.

    Returns:
        bool: True if the file exists, else False.
    """
    return get_config_file(config_name, local=local, config_dir=config_dir).exists()
