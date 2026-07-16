"""Unit tests for the Configuration module."""

import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from cookie_agent.config import (
    BaseConfig,
    CaptureConfig,
    ConfigurationVersion,
    DetectorConfig,
    EnvironmentConfig,
    PlannerConfig,
    PolicyConfig,
    PPOConfig,
    RewardConfig,
    TrackerConfig,
    TrainingConfig,
    ValidationError,
    load_from_dict,
    load_from_file,
    load_from_json,
    merge_configs,
)


def test_version() -> None:
    """Verify ConfigurationVersion string formatting and defaults."""
    v = ConfigurationVersion(major=1, minor=2, patch=3)
    assert str(v) == "1.2.3"
    assert str(ConfigurationVersion.current()) == "1.0.0"


def test_capture_config() -> None:
    """Verify CaptureConfig validation."""
    c = CaptureConfig.default()
    assert c.backend == "windows"

    with pytest.raises(ValidationError, match="queue_size must be > 0"):
        CaptureConfig(backend="test", target_fps=60, queue_size=0)


def test_detector_config() -> None:
    """Verify DetectorConfig ranges."""
    c = DetectorConfig.default()
    assert c.confidence_threshold == 0.5

    with pytest.raises(
        ValidationError, match=r"iou_threshold must be between 0.0 and 1.0"
    ):
        DetectorConfig(
            detector_type="test",
            model_path="test",
            confidence_threshold=0.5,
            iou_threshold=1.5,
            device="cpu",
            half_precision=False,
        )


def test_tracker_config() -> None:
    """Verify TrackerConfig validation."""
    with pytest.raises(ValidationError, match="max_age must be > 0"):
        TrackerConfig(max_age=-1, min_hits=3, distance_threshold=10.0)


def test_environment_config() -> None:
    """Verify EnvironmentConfig validation."""
    c = EnvironmentConfig.default()
    assert c.fps_sync > 0


def test_reward_config() -> None:
    """Verify RewardConfig validation."""
    with pytest.raises(ValidationError, match="strategy cannot be empty"):
        RewardConfig(
            strategy="", survival_points_per_frame=1, jelly_points=1, obstacle_penalty=1
        )


def test_planner_config() -> None:
    """Verify PlannerConfig validation."""
    with pytest.raises(ValidationError, match="delay_between_commands_ms must be >= 0"):
        PlannerConfig(tap_hold_ms=50, delay_between_commands_ms=-5)


def test_policy_config() -> None:
    """Verify PolicyConfig validation."""
    c = PolicyConfig.default()
    assert c.active_policy == "rule"


def test_ppo_config() -> None:
    """Verify PPOConfig validation."""
    with pytest.raises(ValidationError, match=r"gamma must be between 0.0 and 1.0"):
        PPOConfig(
            gamma=2.0,
            lambda_gae=0.9,
            clip_ratio=0.2,
            value_coeff=0.5,
            entropy_coeff=0.01,
        )


def test_training_config() -> None:
    """Verify TrainingConfig validation."""
    with pytest.raises(ValidationError, match="learning_rate must be > 0"):
        TrainingConfig(
            batch_size=32, learning_rate=-0.1, num_epochs=1, checkpoint_dir="test"
        )


def test_base_config_serialization() -> None:
    """Verify BaseConfig to/from dict and json."""
    c1 = CaptureConfig.default()
    d = c1.to_dict()
    assert isinstance(d, dict)
    assert d["backend"] == "windows"

    c2 = CaptureConfig.from_dict(d)
    assert c1 == c2
    assert hash(c1) == hash(c2)

    j = c1.to_json()
    c3 = CaptureConfig.from_json(j)
    assert c1 == c3


def test_merge_configs() -> None:
    """Verify deterministic deep merge."""
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"a": 10, "b": {"d": 40}}

    merged = merge_configs(base, override)

    assert merged["a"] == 10
    assert isinstance(merged["b"], dict)
    assert merged["b"]["c"] == 2
    assert merged["b"]["d"] == 40

    # Original dicts must not be mutated
    assert base["a"] == 1
    assert isinstance(base["b"], dict)
    assert base["b"]["d"] == 3


@dataclass(frozen=True)
class NestedConfig(BaseConfig):
    """Mock nested config for testing."""

    capture: CaptureConfig

    @classmethod
    def default(cls) -> "NestedConfig":
        """Return default."""
        return cls(capture=CaptureConfig.default())


def test_nested_serialization() -> None:
    """Verify deserialization handles nested dataclass objects."""
    n1 = NestedConfig.default()
    j = n1.to_json()

    n2 = NestedConfig.from_json(j)
    assert isinstance(n2.capture, CaptureConfig)
    assert n2.capture.backend == "windows"


def test_loader(tmp_path: Path) -> None:
    """Verify configuration loader wrappers."""
    # From dict
    d = {"backend": "mac", "target_fps": 30, "queue_size": 2}
    c = load_from_dict(CaptureConfig, d)
    assert c.backend == "mac"

    # From json str
    j = json.dumps(d)
    c2 = load_from_json(CaptureConfig, j)
    assert c2.backend == "mac"

    # From file
    f = tmp_path / "config.json"
    f.write_text(j)
    c3 = load_from_file(CaptureConfig, f)
    assert c3.backend == "mac"
