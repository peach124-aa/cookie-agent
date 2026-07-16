"""Configuration loader functions for independent configuration modules."""

from pathlib import Path
from typing import Any, cast

from ruamel.yaml import YAML

from cookie_agent.config.config_name import ConfigName
from cookie_agent.config.env import override_from_env
from cookie_agent.config.exceptions import (
    ConfigNotFoundError,
    ConfigSchemaError,
    ConfigValidationError,
)
from cookie_agent.config.merge import deep_merge
from cookie_agent.config.models import (
    AppConfig,
    CaptureConfig,
    CharacterConfig,
    CharacterItemConfig,
    CooldownRulesConfig,
    DetectorConfig,
    DeviceConfig,
    HoldVarianceConfig,
    LoggingConfig,
    LogRotationConfig,
    MovementConfig,
    PlannerConfig,
    ReplayBufferConfig,
    ResolutionConfig,
    RetryPolicyConfig,
    RewardConfig,
    StrategyConfig,
    TapVarianceConfig,
    TimingVarianceConfig,
    TrainingConfig,
)
from cookie_agent.config.paths import get_config_file
from cookie_agent.config.validator import (
    validate_app_config,
    validate_capture_config,
    validate_character_config,
    validate_detector_config,
    validate_device_config,
    validate_logging_config,
    validate_planner_config,
    validate_reward_config,
    validate_schema_version,
    validate_training_config,
)


def _load_yaml_file(file_path: Path) -> dict[str, Any]:
    """Helper to parse a YAML file into a dictionary.

    Args:
        file_path: Path to the target YAML file.

    Returns:
        dict[str, Any]: Parsed configuration data.

    Raises:
        ConfigValidationError: If YAML parsing fails.
    """
    yaml = YAML(typ="safe")
    with file_path.open("r", encoding="utf-8") as f:
        try:
            return cast(dict[str, Any], yaml.load(f) or {})
        except Exception as e:
            raise ConfigValidationError(
                f"Failed to parse config file {file_path}: {e}"
            ) from e


def _load_raw_section(
    config_name: ConfigName, config_dir: Path | None = None
) -> dict[str, Any]:
    """Helper load, merge, and override raw section configs.

    Args:
        config_name: Enum value representing the config section.
        config_dir: Optional config directory overrides.

    Returns:
        The merged config dictionary.
    """
    default_file = get_config_file(config_name, local=False, config_dir=config_dir)
    if not default_file.exists():
        raise ConfigNotFoundError(f"Missing default config file: {default_file}")

    default_data = _load_yaml_file(default_file)

    # 1. Validate default schema version first
    validate_schema_version(default_data, config_name.value)
    schema_ver = default_data["schema_version"]

    section_dict = default_data.get(config_name.value, {})
    section_dict["schema_version"] = schema_ver

    # Merge local overrides
    local_file = get_config_file(config_name, local=True, config_dir=config_dir)
    if local_file.exists():
        local_data = _load_yaml_file(local_file)

        # Validate local override schema version first
        validate_schema_version(local_data, f"local_{config_name.value}")
        local_ver = local_data["schema_version"]
        if local_ver != schema_ver:
            raise ConfigSchemaError(
                "Schema version mismatch in local overrides for "
                f"{config_name.value}.yaml. "
                f"Expected {schema_ver}, got {local_ver}"
            )

        local_section = cast(dict[str, Any], local_data.get(config_name.value, {}))
        section_dict = deep_merge(section_dict, local_section)

    # Apply environment overrides
    override_from_env(config_name.value, section_dict)

    return cast(dict[str, Any], section_dict)


def load_app_config(config_dir: Path | None = None) -> AppConfig:
    """Load and validate app config."""
    raw = _load_raw_section(ConfigName.APP, config_dir)
    validate_app_config(raw)
    return AppConfig(**raw)


def load_device_config(config_dir: Path | None = None) -> DeviceConfig:
    """Load and validate device config."""
    raw = _load_raw_section(ConfigName.DEVICE, config_dir)
    validate_device_config(raw)
    res_cfg = ResolutionConfig(**raw["resolution"])
    return DeviceConfig(
        schema_version=raw["schema_version"],
        adb_serial=raw["adb_serial"],
        emulator_name=raw["emulator_name"],
        resolution=res_cfg,
        orientation=raw["orientation"],
        capture_backend=raw["capture_backend"],
    )


def load_capture_config(config_dir: Path | None = None) -> CaptureConfig:
    """Load and validate capture config."""
    raw = _load_raw_section(ConfigName.CAPTURE, config_dir)
    validate_capture_config(raw)
    retry_cfg = RetryPolicyConfig(**raw["retry_policy"])
    return CaptureConfig(
        schema_version=raw["schema_version"],
        backend=raw["backend"],
        target_fps=raw["target_fps"],
        queue_size=raw["queue_size"],
        retry_policy=retry_cfg,
    )


def load_detector_config(config_dir: Path | None = None) -> DetectorConfig:
    """Load and validate detector config."""
    raw = _load_raw_section(ConfigName.DETECTOR, config_dir)
    validate_detector_config(raw)
    return DetectorConfig(**raw)


def load_planner_config(config_dir: Path | None = None) -> PlannerConfig:
    """Load and validate planner config."""
    raw = _load_raw_section(ConfigName.PLANNER, config_dir)
    validate_planner_config(raw)
    tv_cfg = TapVarianceConfig(**raw["tap_variance"])
    hv_cfg = HoldVarianceConfig(**raw["hold_variance"])
    tim_cfg = TimingVarianceConfig(**raw["timing_variance"])
    cd_cfg = CooldownRulesConfig(**raw["cooldown_rules"])
    return PlannerConfig(
        schema_version=raw["schema_version"],
        tap_variance=tv_cfg,
        hold_variance=hv_cfg,
        timing_variance=tim_cfg,
        cooldown_rules=cd_cfg,
    )


def load_reward_config(config_dir: Path | None = None) -> RewardConfig:
    """Load and validate reward config."""
    raw = _load_raw_section(ConfigName.REWARD, config_dir)
    validate_reward_config(raw)
    return RewardConfig(
        schema_version=raw["schema_version"],
        strategy=raw["strategy"],
        survival=StrategyConfig(**raw["survival"]),
        coin_farming=StrategyConfig(**raw["coin_farming"]),
        score_farming=StrategyConfig(**raw["score_farming"]),
    )


def load_character_config(config_dir: Path | None = None) -> CharacterConfig:
    """Load and validate character config."""
    raw = _load_raw_section(ConfigName.CHARACTER, config_dir)
    validate_character_config(raw)
    roster_dict = {}
    for char_id, info in raw["roster"].items():
        mv_cfg = MovementConfig(**info["movement"])
        roster_dict[char_id] = CharacterItemConfig(
            name=info["name"],
            abilities=info["abilities"],
            cooldowns=info["cooldowns"],
            movement=mv_cfg,
            detectors=info["detectors"],
        )
    return CharacterConfig(
        schema_version=raw["schema_version"],
        active_id=raw["active_id"],
        roster=roster_dict,
    )


def load_training_config(config_dir: Path | None = None) -> TrainingConfig:
    """Load and validate training config."""
    raw = _load_raw_section(ConfigName.TRAINING, config_dir)
    validate_training_config(raw)
    rb_cfg = ReplayBufferConfig(**raw["replay_buffer"])
    return TrainingConfig(
        schema_version=raw["schema_version"],
        algorithm=raw["algorithm"],
        seed=raw["seed"],
        batch_size=raw["batch_size"],
        learning_rate=raw["learning_rate"],
        checkpoint_dir=raw["checkpoint_dir"],
        resume=raw["resume"],
        device=raw["device"],
        num_workers=raw["num_workers"],
        replay_buffer=rb_cfg,
    )


def load_logging_config(config_dir: Path | None = None) -> LoggingConfig:
    """Load and validate logging config."""
    raw = _load_raw_section(ConfigName.LOGGING, config_dir)
    validate_logging_config(raw)
    rot_cfg = LogRotationConfig(**raw["log_rotation"])
    return LoggingConfig(
        schema_version=raw["schema_version"],
        log_directory=raw["log_directory"],
        log_rotation=rot_cfg,
        save_frames=raw["save_frames"],
        save_replay=raw["save_replay"],
        save_detector_output=raw["save_detector_output"],
        save_tracker_output=raw["save_tracker_output"],
    )
