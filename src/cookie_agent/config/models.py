"""Frozen dataclasses for configuration tree representation."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AppConfig:
    """App configuration properties."""

    schema_version: int
    project_name: str
    version: str
    debug: bool
    log_level: str


@dataclass(frozen=True, slots=True)
class ResolutionConfig:
    """Screen resolution boundaries."""

    width: int
    height: int


@dataclass(frozen=True, slots=True)
class DeviceConfig:
    """Emulator connectivity settings."""

    schema_version: int
    adb_serial: str
    emulator_name: str
    resolution: ResolutionConfig
    orientation: str
    capture_backend: str


@dataclass(frozen=True, slots=True)
class RetryPolicyConfig:
    """Frame capture retry parameters."""

    max_retries: int
    backoff_ms: int


@dataclass(frozen=True, slots=True)
class CaptureConfig:
    """Graph buffer capture variables."""

    schema_version: int
    backend: str
    target_fps: int
    queue_size: int
    retry_policy: RetryPolicyConfig


@dataclass(frozen=True, slots=True)
class DetectorConfig:
    """Target classifier detector properties."""

    schema_version: int
    detector_type: str
    model_path: str
    confidence_threshold: float
    iou_threshold: float
    device: str
    half_precision: bool


@dataclass(frozen=True, slots=True)
class TapVarianceConfig:
    """Tap coordinates noise limits."""

    max_offset_x: int
    max_offset_y: int


@dataclass(frozen=True, slots=True)
class HoldVarianceConfig:
    """Touch duration noise bounds."""

    max_jitter_ms: int


@dataclass(frozen=True, slots=True)
class TimingVarianceConfig:
    """Touch delay noise bounds."""

    max_delay_jitter_ms: int


@dataclass(frozen=True, slots=True)
class CooldownRulesConfig:
    """Locomotion cooldown constraints."""

    jump_cooldown_ms: int
    slide_cooldown_ms: int


@dataclass(frozen=True, slots=True)
class PlannerConfig:
    """Motion action planners configurations."""

    schema_version: int
    tap_variance: TapVarianceConfig
    hold_variance: HoldVarianceConfig
    timing_variance: TimingVarianceConfig
    cooldown_rules: CooldownRulesConfig


@dataclass(frozen=True, slots=True)
class StrategyConfig:
    """Reward strategy weights."""

    points_per_distance_pixel: float
    points_per_jelly: float
    damage_penalty: float
    collision_penalty: float
    points_per_coin: float | None = None


@dataclass(frozen=True, slots=True)
class RewardConfig:
    """Scoring evaluation parameters."""

    schema_version: int
    strategy: str
    survival: StrategyConfig
    coin_farming: StrategyConfig
    score_farming: StrategyConfig


@dataclass(frozen=True, slots=True)
class MovementConfig:
    """Character movement settings."""

    base_speed: float
    jump_height_pixels: int


@dataclass(frozen=True, slots=True)
class CharacterItemConfig:
    """Details representing specific cookie capabilities."""

    name: str
    abilities: list[dict[str, Any]]
    cooldowns: dict[str, Any]
    movement: MovementConfig
    detectors: list[str]


@dataclass(frozen=True, slots=True)
class CharacterConfig:
    """Character runner attributes."""

    schema_version: int
    active_id: str
    roster: dict[str, CharacterItemConfig]


@dataclass(frozen=True, slots=True)
class ReplayBufferConfig:
    """Replay buffer variables."""

    capacity: int
    burn_in_steps: int


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    """RL parameters configuration."""

    schema_version: int
    algorithm: str
    seed: int
    batch_size: int
    learning_rate: float
    checkpoint_dir: str
    resume: bool
    device: str
    num_workers: int
    replay_buffer: ReplayBufferConfig


@dataclass(frozen=True, slots=True)
class LogRotationConfig:
    """Rotation guidelines for logs."""

    max_bytes: int
    backup_count: int


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Logging destination properties."""

    schema_version: int
    log_directory: str
    log_rotation: LogRotationConfig
    save_frames: bool
    save_replay: bool
    save_detector_output: bool
    save_tracker_output: bool
