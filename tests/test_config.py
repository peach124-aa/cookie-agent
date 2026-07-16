"""Unit tests for independent configuration loaders and validators."""

import os
from pathlib import Path
from typing import Any

import pytest
from cookie_agent.config import (
    CONFIG_ROOT,
    DEFAULT_CONFIG_DIR,
    LOCAL_CONFIG_DIR,
    ConfigName,
    ConfigNotFoundError,
    ConfigSchemaError,
    ConfigValidationError,
    config_exists,
    get_config_file,
    load_app_config,
    load_capture_config,
    load_character_config,
    load_detector_config,
    load_device_config,
    load_logging_config,
    load_planner_config,
    load_reward_config,
    load_training_config,
)
from cookie_agent.config.env import override_from_env
from cookie_agent.config.merge import deep_merge
from cookie_agent.config.validator import validate_schema_version
from ruamel.yaml import YAML

# Baseline default templates for testing
DEFAULT_TEMPLATES = {
    "app": {
        "schema_version": 1,
        "app": {
            "project_name": "cookie_agent",
            "version": "1.0.0",
            "debug": False,
            "log_level": "INFO",
        },
    },
    "device": {
        "schema_version": 1,
        "device": {
            "adb_serial": "127.0.0.1:5555",
            "emulator_name": "MuMuPlayer",
            "resolution": {"width": 1280, "height": 720},
            "orientation": "landscape",
            "capture_backend": "DXGI",
        },
    },
    "capture": {
        "schema_version": 1,
        "capture": {
            "backend": "DXGI",
            "target_fps": 60,
            "queue_size": 3,
            "retry_policy": {"max_retries": 5, "backoff_ms": 100},
        },
    },
    "detector": {
        "schema_version": 1,
        "detector": {
            "detector_type": "yolov8n",
            "model_path": "models/detector.onnx",
            "confidence_threshold": 0.75,
            "iou_threshold": 0.45,
            "device": "auto",
            "half_precision": True,
        },
    },
    "planner": {
        "schema_version": 1,
        "planner": {
            "tap_variance": {"max_offset_x": 10, "max_offset_y": 10},
            "hold_variance": {"max_jitter_ms": 10},
            "timing_variance": {"max_delay_jitter_ms": 15},
            "cooldown_rules": {
                "jump_cooldown_ms": 200,
                "slide_cooldown_ms": 100,
            },
        },
    },
    "reward": {
        "schema_version": 1,
        "reward": {
            "strategy": "survival",
            "survival": {
                "points_per_distance_pixel": 1.0,
                "points_per_jelly": 0.1,
                "damage_penalty": -100.0,
                "collision_penalty": -500.0,
            },
            "coin_farming": {
                "points_per_distance_pixel": 0.1,
                "points_per_jelly": 0.05,
                "points_per_coin": 5.0,
                "damage_penalty": -50.0,
                "collision_penalty": -500.0,
            },
            "score_farming": {
                "points_per_distance_pixel": 0.5,
                "points_per_jelly": 2.0,
                "points_per_coin": 0.1,
                "damage_penalty": -200.0,
                "collision_penalty": -800.0,
            },
        },
    },
    "character": {
        "schema_version": 1,
        "character": {
            "active_id": "brave_cookie",
            "roster": {
                "brave_cookie": {
                    "name": "GingerBrave",
                    "abilities": ["jump", "slide"],
                    "cooldowns": {},
                    "movement": {"base_speed": 1.0, "jump_height_pixels": 240},
                    "detectors": [],
                }
            },
        },
    },
    "training": {
        "schema_version": 1,
        "training": {
            "algorithm": "PPO",
            "seed": 42,
            "batch_size": 64,
            "learning_rate": 0.0003,
            "checkpoint_dir": "models/",
            "resume": False,
            "device": "auto",
            "num_workers": 4,
            "replay_buffer": {"capacity": 100000, "burn_in_steps": 1000},
        },
    },
    "logging": {
        "schema_version": 1,
        "logging": {
            "log_directory": "logs/",
            "log_rotation": {"max_bytes": 10485760, "backup_count": 5},
            "save_frames": False,
            "save_replay": True,
            "save_detector_output": False,
            "save_tracker_output": False,
        },
    },
}


def _write_yaml_configs(target_dir: Path, data_map: dict[str, Any]) -> None:
    """Helper to write configuration structure to disk."""
    yaml_parser = YAML(typ="safe")
    for name, content in data_map.items():
        with (target_dir / f"{name}.yaml").open("w", encoding="utf-8") as f:
            yaml_parser.dump(content, f)


@pytest.fixture()
def temp_config_dir(tmp_path: Path) -> Path:
    """Fixture initializing temporary configs defaults structure."""
    defaults = tmp_path / "defaults"
    defaults.mkdir()
    (tmp_path / "local").mkdir()
    _write_yaml_configs(defaults, DEFAULT_TEMPLATES)
    return tmp_path


def test_paths_and_config_name() -> None:
    """Verify default paths variables exports and ConfigName values."""
    assert CONFIG_ROOT == Path("configs")
    assert DEFAULT_CONFIG_DIR == Path("configs/defaults")
    assert LOCAL_CONFIG_DIR == Path("configs/local")
    assert ConfigName.APP.value == "app"
    assert ConfigName.CAPTURE.value == "capture"


def test_get_config_file() -> None:
    """Verify that get_config_file resolves paths correctly."""
    p1 = get_config_file(ConfigName.APP, local=False)
    assert p1 == Path("configs/defaults/app.yaml")

    p2 = get_config_file(ConfigName.LOGGING, local=True)
    assert p2 == Path("configs/local/logging.yaml")

    custom_base = Path("custom_dir")
    p3 = get_config_file(ConfigName.DEVICE, local=False, config_dir=custom_base)
    assert p3 == Path("custom_dir/defaults/device.yaml")


def test_config_exists(temp_config_dir: Path) -> None:
    """Verify config_exists checks correct presence on disk."""
    assert (
        config_exists(ConfigName.APP, local=False, config_dir=temp_config_dir) is True
    )
    assert (
        config_exists(ConfigName.APP, local=True, config_dir=temp_config_dir) is False
    )


def test_deep_merge_immutability() -> None:
    """Verify that deep_merge creates a new dictionary and does not mutate inputs."""
    base = {"a": 1, "b": {"c": 2}}
    override = {"b": {"c": 3}, "d": 4}

    res = deep_merge(base, override)

    # Verify input dicts are unchanged
    assert base == {"a": 1, "b": {"c": 2}}
    assert override == {"b": {"c": 3}, "d": 4}

    # Verify return dict is a new instance matching merged keys
    assert res == {"a": 1, "b": {"c": 3}, "d": 4}
    assert res is not base
    assert res is not override
    assert res["b"] is not base["b"]
    assert res["b"] is not override["b"]


def test_deep_merge_list_override() -> None:
    """Verify that list deep merging behaves as atomic replacement."""
    base = {"abilities": ["jump", "slide"]}
    override = {"abilities": ["dash"]}
    res = deep_merge(base, override)

    assert res["abilities"] == ["dash"]


def test_load_defaults_only(temp_config_dir: Path) -> None:
    """Verify loading baseline defaults only compiles successfully."""
    app_cfg = load_app_config(temp_config_dir)
    assert app_cfg.project_name == "cookie_agent"
    assert app_cfg.schema_version == 1

    device_cfg = load_device_config(temp_config_dir)
    assert device_cfg.adb_serial == "127.0.0.1:5555"

    capture_cfg = load_capture_config(temp_config_dir)
    assert capture_cfg.target_fps == 60

    det_cfg = load_detector_config(temp_config_dir)
    assert det_cfg.confidence_threshold == 0.75

    planner_cfg = load_planner_config(temp_config_dir)
    assert planner_cfg.tap_variance.max_offset_x == 10

    reward_cfg = load_reward_config(temp_config_dir)
    assert reward_cfg.strategy == "survival"

    char_cfg = load_character_config(temp_config_dir)
    assert char_cfg.active_id == "brave_cookie"

    train_cfg = load_training_config(temp_config_dir)
    assert train_cfg.seed == 42

    log_cfg = load_logging_config(temp_config_dir)
    assert log_cfg.save_replay is True


def test_load_with_local_overrides(temp_config_dir: Path) -> None:
    """Verify local files correctly merge on top of defaults."""
    local_dir = temp_config_dir / "local"
    local_data = {
        "app": {
            "schema_version": 1,
            "app": {
                "debug": True,
                "log_level": "DEBUG",
            },
        },
        "device": {
            "schema_version": 1,
            "device": {
                "adb_serial": "192.168.1.100:5555",
            },
        },
    }
    _write_yaml_configs(local_dir, local_data)

    app_cfg = load_app_config(temp_config_dir)
    assert app_cfg.debug is True
    assert app_cfg.log_level == "DEBUG"
    assert app_cfg.project_name == "cookie_agent"

    device_cfg = load_device_config(temp_config_dir)
    assert device_cfg.adb_serial == "192.168.1.100:5555"


def test_load_with_env_overrides(temp_config_dir: Path) -> None:
    """Verify environment variables correctly take override priority."""
    os.environ["COOKIE_AGENT_DETECTOR__CONFIDENCE_THRESHOLD"] = "0.95"
    os.environ["COOKIE_AGENT_LOGGING__SAVE_FRAMES"] = "True"
    os.environ["COOKIE_AGENT_TRAINING__BATCH_SIZE"] = "128"

    try:
        det_cfg = load_detector_config(temp_config_dir)
        assert det_cfg.confidence_threshold == 0.95

        log_cfg = load_logging_config(temp_config_dir)
        assert log_cfg.save_frames is True

        train_cfg = load_training_config(temp_config_dir)
        assert train_cfg.batch_size == 128
    finally:
        del os.environ["COOKIE_AGENT_DETECTOR__CONFIDENCE_THRESHOLD"]
        del os.environ["COOKIE_AGENT_LOGGING__SAVE_FRAMES"]
        del os.environ["COOKIE_AGENT_TRAINING__BATCH_SIZE"]


def test_env_override_nested_creation() -> None:
    """Verify that env override correctly initializes missing intermediate dicts."""
    os.environ["COOKIE_AGENT_CAPTURE__THREAD__QUEUE_SIZE"] = "8"
    cfg = {"schema_version": 1, "backend": "DXGI"}
    try:
        override_from_env("capture", cfg)
        assert cfg["thread"] == {"queue_size": 8}
    finally:
        del os.environ["COOKIE_AGENT_CAPTURE__THREAD__QUEUE_SIZE"]


@pytest.mark.parametrize(
    ("env_val", "expected"),
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("YES", True),
        ("on", True),
        ("ON", True),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("NO", False),
        ("off", False),
        ("OFF", False),
    ],
)
def test_boolean_casting_success(
    temp_config_dir: Path, env_val: str, expected: bool
) -> None:
    """Verify case-insensitive parsing of common boolean representations."""
    os.environ["COOKIE_AGENT_APP__DEBUG"] = env_val
    try:
        app_cfg = load_app_config(temp_config_dir)
        assert app_cfg.debug is expected
    finally:
        del os.environ["COOKIE_AGENT_APP__DEBUG"]


def test_boolean_casting_failure(temp_config_dir: Path) -> None:
    """Verify ConfigValidationError raises on invalid boolean values."""
    os.environ["COOKIE_AGENT_APP__DEBUG"] = "maybe"
    try:
        with pytest.raises(ConfigValidationError):
            load_app_config(temp_config_dir)
    finally:
        del os.environ["COOKIE_AGENT_APP__DEBUG"]


def test_missing_default_config(temp_config_dir: Path) -> None:
    """Verify ConfigNotFoundError is raised when a default file is missing."""
    app_file = temp_config_dir / "defaults" / "app.yaml"
    app_file.unlink()

    with pytest.raises(ConfigNotFoundError):
        load_app_config(temp_config_dir)


def test_schema_version_validation() -> None:
    """Verify separate schema validation functions directly."""
    # Missing version
    with pytest.raises(ConfigSchemaError):
        validate_schema_version({}, "test")

    # Invalid type
    with pytest.raises(ConfigSchemaError):
        validate_schema_version({"schema_version": "1"}, "test")

    # Below 1
    with pytest.raises(ConfigSchemaError):
        validate_schema_version({"schema_version": 0}, "test")

    # Valid schema does not raise error
    validate_schema_version({"schema_version": 1}, "test")


def test_schema_version_mismatch(temp_config_dir: Path) -> None:
    """Verify ConfigSchemaError on version discrepancies."""
    local_dir = temp_config_dir / "local"
    local_data = {
        "app": {
            "schema_version": 2,  # mismatched version override
            "app": {
                "debug": True,
            },
        }
    }
    _write_yaml_configs(local_dir, local_data)

    with pytest.raises(ConfigSchemaError):
        load_app_config(temp_config_dir)


def test_unknown_key_validation(temp_config_dir: Path) -> None:
    """Verify validation triggers ConfigValidationError on unknown config keys."""
    local_dir = temp_config_dir / "local"
    local_data = {
        "app": {
            "schema_version": 1,
            "app": {
                "project_name": "cookie_agent",
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO",
                "extra_unknown_key": "some_value",
            },
        }
    }
    _write_yaml_configs(local_dir, local_data)

    with pytest.raises(ConfigValidationError):
        load_app_config(temp_config_dir)


@pytest.mark.parametrize(
    ("env_key", "env_val", "loader_func"),
    [
        ("COOKIE_AGENT_APP__LOG_LEVEL", "INVALID", load_app_config),
        ("COOKIE_AGENT_APP__PROJECT_NAME", "wrong_name", load_app_config),
        ("COOKIE_AGENT_DEVICE__RESOLUTION__WIDTH", "500", load_device_config),
        ("COOKIE_AGENT_DEVICE__RESOLUTION__HEIGHT", "3000", load_device_config),
        ("COOKIE_AGENT_DEVICE__ORIENTATION", "portrait_wrong", load_device_config),
        ("COOKIE_AGENT_DEVICE__CAPTURE_BACKEND", "UNKNOWN", load_device_config),
        ("COOKIE_AGENT_CAPTURE__TARGET_FPS", "200", load_capture_config),
        ("COOKIE_AGENT_CAPTURE__QUEUE_SIZE", "0", load_capture_config),
        ("COOKIE_AGENT_CAPTURE__RETRY_POLICY__MAX_RETRIES", "-1", load_capture_config),
        ("COOKIE_AGENT_CAPTURE__RETRY_POLICY__BACKOFF_MS", "5", load_capture_config),
        ("COOKIE_AGENT_DETECTOR__DETECTOR_TYPE", "yolo_wrong", load_detector_config),
        ("COOKIE_AGENT_DETECTOR__CONFIDENCE_THRESHOLD", "-0.1", load_detector_config),
        ("COOKIE_AGENT_DETECTOR__IOU_THRESHOLD", "1.1", load_detector_config),
        ("COOKIE_AGENT_DETECTOR__DEVICE", "tpu", load_detector_config),
        ("COOKIE_AGENT_PLANNER__TAP_VARIANCE__MAX_OFFSET_X", "60", load_planner_config),
        (
            "COOKIE_AGENT_PLANNER__HOLD_VARIANCE__MAX_JITTER_MS",
            "150",
            load_planner_config,
        ),
        (
            "COOKIE_AGENT_PLANNER__TIMING_VARIANCE__MAX_DELAY_JITTER_MS",
            "250",
            load_planner_config,
        ),
        (
            "COOKIE_AGENT_PLANNER__COOLDOWN_RULES__JUMP_COOLDOWN_MS",
            "40",
            load_planner_config,
        ),
        (
            "COOKIE_AGENT_PLANNER__COOLDOWN_RULES__SLIDE_COOLDOWN_MS",
            "2000",
            load_planner_config,
        ),
        ("COOKIE_AGENT_REWARD__STRATEGY", "farming", load_reward_config),
        (
            "COOKIE_AGENT_REWARD__SURVIVAL__POINTS_PER_DISTANCE_PIXEL",
            "-1.0",
            load_reward_config,
        ),
        ("COOKIE_AGENT_REWARD__SURVIVAL__DAMAGE_PENALTY", "1.0", load_reward_config),
        ("COOKIE_AGENT_CHARACTER__ACTIVE_ID", "unknown_cookie", load_character_config),
        ("COOKIE_AGENT_TRAINING__ALGORITHM", "A3C", load_training_config),
        ("COOKIE_AGENT_TRAINING__LEARNING_RATE", "0.5", load_training_config),
        ("COOKIE_AGENT_TRAINING__NUM_WORKERS", "100", load_training_config),
        ("COOKIE_AGENT_TRAINING__REPLAY_BUFFER__CAPACITY", "50", load_training_config),
        ("COOKIE_AGENT_LOGGING__LOG_ROTATION__MAX_BYTES", "500", load_logging_config),
        (
            "COOKIE_AGENT_LOGGING__LOG_ROTATION__BACKUP_COUNT",
            "150",
            load_logging_config,
        ),
    ],
)
def test_all_individual_validation_failures(
    temp_config_dir: Path, env_key: str, env_val: str, loader_func: Any
) -> None:
    """Verify various validation failures on invalid properties."""
    os.environ[env_key] = env_val
    try:
        with pytest.raises(ConfigValidationError):
            loader_func(temp_config_dir)
    finally:
        del os.environ[env_key]
