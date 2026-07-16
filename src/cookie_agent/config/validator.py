"""Schema validation rules for individual configurations."""

from typing import Any

from cookie_agent.config.exceptions import ConfigSchemaError, ConfigValidationError
from cookie_agent.config.version import CONFIG_SCHEMA_VERSION


def validate_schema_version(cfg: dict[str, Any], name: str) -> None:
    """Validate schema_version presence and value in config dict.

    Args:
        cfg: Raw configuration dictionary.
        name: Name of the configuration block.

    Raises:
        ConfigSchemaError: If schema version validation fails.
    """
    if "schema_version" not in cfg:
        raise ConfigSchemaError(f"Missing 'schema_version' in {name} configuration.")
    version = cfg["schema_version"]
    if not isinstance(version, int) or version != CONFIG_SCHEMA_VERSION:
        raise ConfigSchemaError(
            f"Invalid 'schema_version' in {name}: {version}. "
            f"Expected {CONFIG_SCHEMA_VERSION}."
        )


def validate_unknown_keys(
    cfg: dict[str, Any], allowed_keys: set[str], name: str
) -> None:
    """Validate that there are no unknown keys in the configuration.

    Args:
        cfg: Configuration dictionary to check.
        allowed_keys: Set of allowed key names.
        name: Context namespace name for error reports.

    Raises:
        ConfigValidationError: If unknown keys are found.
    """
    actual_keys = set(cfg.keys())
    unknown = actual_keys - allowed_keys
    if unknown:
        raise ConfigValidationError(
            f"Unknown configuration keys in '{name}': {unknown}. "
            f"Allowed: {allowed_keys}"
        )


def validate_app_config(app: dict[str, Any]) -> None:
    """Validate app configuration parameters.

    Args:
        app: App configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        app,
        {"schema_version", "project_name", "version", "debug", "log_level"},
        "app",
    )
    if app.get("project_name") != "cookie_agent":
        raise ConfigValidationError("app.project_name must equal 'cookie_agent'.")
    if not app.get("version"):
        raise ConfigValidationError("app.version must be a non-empty string.")
    if not isinstance(app.get("debug"), bool):
        raise ConfigValidationError("app.debug must be a boolean.")
    log_level = app.get("log_level")
    allowed_logs = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level not in allowed_logs:
        raise ConfigValidationError(
            f"app.log_level '{log_level}' not in {allowed_logs}."
        )


def validate_device_config(device: dict[str, Any]) -> None:
    """Validate device configuration parameters.

    Args:
        device: Device configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        device,
        {
            "schema_version",
            "adb_serial",
            "emulator_name",
            "resolution",
            "orientation",
            "capture_backend",
        },
        "device",
    )
    if not device.get("adb_serial"):
        raise ConfigValidationError("device.adb_serial must be non-empty.")
    if not device.get("emulator_name"):
        raise ConfigValidationError("device.emulator_name must be non-empty.")

    res = device.get("resolution", {})
    validate_unknown_keys(res, {"width", "height"}, "device.resolution")
    width = res.get("width")
    height = res.get("height")
    if not isinstance(width, int) or not (640 <= width <= 3840):
        raise ConfigValidationError(
            f"device.resolution.width {width} must be in [640, 3840]."
        )
    if not isinstance(height, int) or not (360 <= height <= 2160):
        raise ConfigValidationError(
            f"device.resolution.height {height} must be in [360, 2160]."
        )
    if device.get("orientation") not in {"landscape", "portrait"}:
        raise ConfigValidationError("device.orientation must be landscape/portrait.")
    if device.get("capture_backend") not in {"GDI", "DXGI", "ADB"}:
        raise ConfigValidationError("device.capture_backend must be GDI/DXGI/ADB.")


def validate_capture_config(capture: dict[str, Any]) -> None:
    """Validate capture configuration parameters.

    Args:
        capture: Capture configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        capture,
        {"schema_version", "backend", "target_fps", "queue_size", "retry_policy"},
        "capture",
    )
    if capture.get("backend") not in {"GDI", "DXGI", "ADB"}:
        raise ConfigValidationError("capture.backend must be GDI/DXGI/ADB.")
    fps = capture.get("target_fps")
    if not isinstance(fps, int) or not (1 <= fps <= 120):
        raise ConfigValidationError(f"capture.target_fps {fps} must be in [1, 120].")
    q_size = capture.get("queue_size")
    if not isinstance(q_size, int) or not (1 <= q_size <= 10):
        raise ConfigValidationError(f"capture.queue_size {q_size} must be in [1, 10].")

    retry = capture.get("retry_policy", {})
    validate_unknown_keys(retry, {"max_retries", "backoff_ms"}, "capture.retry_policy")
    max_r = retry.get("max_retries")
    back_ms = retry.get("backoff_ms")
    if not isinstance(max_r, int) or max_r < 0:
        raise ConfigValidationError("capture.retry_policy.max_retries must be >= 0.")
    if not isinstance(back_ms, int) or back_ms < 10:
        raise ConfigValidationError("capture.retry_policy.backoff_ms must be >= 10.")


def validate_detector_config(det: dict[str, Any]) -> None:
    """Validate detector configuration parameters.

    Args:
        det: Detector configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        det,
        {
            "schema_version",
            "detector_type",
            "model_path",
            "confidence_threshold",
            "iou_threshold",
            "device",
            "half_precision",
        },
        "detector",
    )
    if det.get("detector_type") not in {"yolov8n", "yolonas", "custom_cnn"}:
        raise ConfigValidationError(
            "detector.detector_type must be yolov8n/yolonas/custom_cnn."
        )
    if not det.get("model_path"):
        raise ConfigValidationError("detector.model_path must be non-empty.")
    conf = det.get("confidence_threshold")
    iou = det.get("iou_threshold")
    if not isinstance(conf, int | float) or not (0.0 <= conf <= 1.0):
        raise ConfigValidationError(
            f"detector.confidence_threshold {conf} must be in [0.0, 1.0]."
        )
    if not isinstance(iou, int | float) or not (0.0 <= iou <= 1.0):
        raise ConfigValidationError(
            f"detector.iou_threshold {iou} must be in [0.0, 1.0]."
        )
    if det.get("device") not in {"auto", "cpu", "cuda"}:
        raise ConfigValidationError("detector.device must be auto/cpu/cuda.")
    if not isinstance(det.get("half_precision"), bool):
        raise ConfigValidationError("detector.half_precision must be a boolean.")


def validate_planner_config(planner: dict[str, Any]) -> None:
    """Validate planner configuration parameters.

    Args:
        planner: Planner configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        planner,
        {
            "schema_version",
            "tap_variance",
            "hold_variance",
            "timing_variance",
            "cooldown_rules",
        },
        "planner",
    )
    tv = planner.get("tap_variance", {})
    validate_unknown_keys(tv, {"max_offset_x", "max_offset_y"}, "planner.tap_variance")
    offset_x = tv.get("max_offset_x")
    offset_y = tv.get("max_offset_y")
    if not isinstance(offset_x, int) or not (0 <= offset_x <= 50):
        raise ConfigValidationError(
            "planner.tap_variance.max_offset_x must be [0, 50]."
        )
    if not isinstance(offset_y, int) or not (0 <= offset_y <= 50):
        raise ConfigValidationError(
            "planner.tap_variance.max_offset_y must be [0, 50]."
        )

    hv = planner.get("hold_variance", {})
    validate_unknown_keys(hv, {"max_jitter_ms"}, "planner.hold_variance")
    h_jitter = hv.get("max_jitter_ms")
    if not isinstance(h_jitter, int) or not (0 <= h_jitter <= 100):
        raise ConfigValidationError(
            "planner.hold_variance.max_jitter_ms must be [0, 100]."
        )

    t_var = planner.get("timing_variance", {})
    validate_unknown_keys(t_var, {"max_delay_jitter_ms"}, "planner.timing_variance")
    t_jitter = t_var.get("max_delay_jitter_ms")
    if not isinstance(t_jitter, int) or not (0 <= t_jitter <= 200):
        raise ConfigValidationError(
            "planner.timing_variance.max_delay_jitter_ms must be [0, 200]."
        )

    cd = planner.get("cooldown_rules", {})
    validate_unknown_keys(
        cd, {"jump_cooldown_ms", "slide_cooldown_ms"}, "planner.cooldown_rules"
    )
    j_cd = cd.get("jump_cooldown_ms")
    s_cd = cd.get("slide_cooldown_ms")
    if not isinstance(j_cd, int) or not (50 <= j_cd <= 1000):
        raise ConfigValidationError(
            "planner.cooldown_rules.jump_cooldown_ms must be [50, 1000]."
        )
    if not isinstance(s_cd, int) or not (50 <= s_cd <= 1000):
        raise ConfigValidationError(
            "planner.cooldown_rules.slide_cooldown_ms must be [50, 1000]."
        )


def validate_reward_config(reward: dict[str, Any]) -> None:
    """Validate reward configuration parameters.

    Args:
        reward: Reward configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        reward,
        {"schema_version", "strategy", "survival", "coin_farming", "score_farming"},
        "reward",
    )
    strat = reward.get("strategy")
    allowed_strats = {"survival", "coin_farming", "score_farming"}
    if strat not in allowed_strats:
        raise ConfigValidationError(
            f"reward.strategy {strat} must be in {allowed_strats}."
        )
    for s_name in allowed_strats:
        s_block = reward.get(s_name, {})
        if not s_block:
            raise ConfigValidationError(f"Missing reward strategy block: {s_name}")
        validate_unknown_keys(
            s_block,
            {
                "points_per_distance_pixel",
                "points_per_jelly",
                "damage_penalty",
                "collision_penalty",
                "points_per_coin",
            },
            f"reward.{s_name}",
        )
        dist = s_block.get("points_per_distance_pixel")
        jelly = s_block.get("points_per_jelly")
        dmg = s_block.get("damage_penalty")
        coll = s_block.get("collision_penalty")
        if not isinstance(dist, int | float) or dist < 0:
            raise ConfigValidationError(
                f"reward.{s_name}.points_per_distance_pixel must be >= 0."
            )
        if not isinstance(jelly, int | float) or jelly < 0:
            raise ConfigValidationError(
                f"reward.{s_name}.points_per_jelly must be >= 0."
            )
        if not isinstance(dmg, int | float) or dmg > 0:
            raise ConfigValidationError(f"reward.{s_name}.damage_penalty must be <= 0.")
        if not isinstance(coll, int | float) or coll > 0:
            raise ConfigValidationError(
                f"reward.{s_name}.collision_penalty must be <= 0."
            )


def validate_character_config(char: dict[str, Any]) -> None:
    """Validate character configuration parameters.

    Args:
        char: Character configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(char, {"schema_version", "active_id", "roster"}, "character")
    active_id = char.get("active_id")
    roster = char.get("roster", {})
    if not active_id or active_id not in roster:
        raise ConfigValidationError(
            f"character.active_id '{active_id}' must match key in roster."
        )
    for char_id, info in roster.items():
        validate_unknown_keys(
            info,
            {"name", "abilities", "cooldowns", "movement", "detectors"},
            f"character.roster.{char_id}",
        )
        if not info.get("name"):
            raise ConfigValidationError(f"character.roster.{char_id}.name is required.")
        m = info.get("movement", {})
        validate_unknown_keys(
            m,
            {"base_speed", "jump_height_pixels"},
            f"character.roster.{char_id}.movement",
        )
        speed = m.get("base_speed")
        jh = m.get("jump_height_pixels")
        if not isinstance(speed, int | float) or not (0.5 <= speed <= 3.0):
            raise ConfigValidationError(
                f"character.roster.{char_id}.movement.base_speed must be [0.5, 3.0]."
            )
        if not isinstance(jh, int) or jh <= 0:
            raise ConfigValidationError(
                f"character.roster.{char_id}.movement.jump_height_pixels must be > 0."
            )


def validate_training_config(tr: dict[str, Any]) -> None:
    """Validate training configuration parameters.

    Args:
        tr: Training configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        tr,
        {
            "schema_version",
            "algorithm",
            "seed",
            "batch_size",
            "learning_rate",
            "checkpoint_dir",
            "resume",
            "device",
            "num_workers",
            "replay_buffer",
        },
        "training",
    )
    if tr.get("algorithm") not in {"PPO", "DQN", "SAC"}:
        raise ConfigValidationError("training.algorithm must be PPO/DQN/SAC.")
    bs = tr.get("batch_size")
    if not isinstance(bs, int) or bs <= 0 or (bs & (bs - 1) != 0):
        raise ConfigValidationError("training.batch_size must be positive power of 2.")
    lr = tr.get("learning_rate")
    if not isinstance(lr, int | float) or not (1e-6 <= lr <= 1e-1):
        raise ConfigValidationError(
            f"training.learning_rate {lr} must be in [1e-6, 1e-1]."
        )
    if not tr.get("checkpoint_dir"):
        raise ConfigValidationError("training.checkpoint_dir is required.")
    if tr.get("device") not in {"cpu", "cuda", "auto"}:
        raise ConfigValidationError("training.device must be cpu/cuda/auto.")
    workers = tr.get("num_workers")
    if not isinstance(workers, int) or not (0 <= workers <= 64):
        raise ConfigValidationError("training.num_workers must be [0, 64].")

    rb = tr.get("replay_buffer", {})
    validate_unknown_keys(rb, {"capacity", "burn_in_steps"}, "training.replay_buffer")
    cap = rb.get("capacity")
    burn = rb.get("burn_in_steps")
    if not isinstance(cap, int) or cap < 100:
        raise ConfigValidationError("training.replay_buffer.capacity must be >= 100.")
    if not isinstance(burn, int) or burn < 0:
        raise ConfigValidationError(
            "training.replay_buffer.burn_in_steps must be >= 0."
        )


def validate_logging_config(log: dict[str, Any]) -> None:
    """Validate logging configuration parameters.

    Args:
        log: Logging configuration dictionary.

    Raises:
        ConfigValidationError: If values violate constraints.
    """
    validate_unknown_keys(
        log,
        {
            "schema_version",
            "log_directory",
            "log_rotation",
            "save_frames",
            "save_replay",
            "save_detector_output",
            "save_tracker_output",
        },
        "logging",
    )
    if not log.get("log_directory"):
        raise ConfigValidationError("logging.log_directory is required.")

    rot = log.get("log_rotation", {})
    validate_unknown_keys(rot, {"max_bytes", "backup_count"}, "logging.log_rotation")
    max_b = rot.get("max_bytes")
    backup = rot.get("backup_count")
    if not isinstance(max_b, int) or not (1024 <= max_b <= 1073741824):
        raise ConfigValidationError(
            "logging.log_rotation.max_bytes must be [1KB, 1GB]."
        )
    if not isinstance(backup, int) or not (0 <= backup <= 100):
        raise ConfigValidationError(
            "logging.log_rotation.backup_count must be [0, 100]."
        )
