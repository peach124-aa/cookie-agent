"""Metrics tracking for the inference pipeline."""

from dataclasses import dataclass


@dataclass(slots=True)
class StepMetrics:
    """Performance timing metrics for a single inference step.

    All timings are in milliseconds.
    """

    step_id: int
    capture_time_ms: float
    detection_time_ms: float
    tracking_time_ms: float
    state_builder_time_ms: float
    policy_time_ms: float
    planner_time_ms: float
    device_execution_time_ms: float
    total_pipeline_time_ms: float


@dataclass(slots=True)
class LoopMetrics:
    """Accumulated performance metrics for the entire loop run."""

    frame_count: int
    step_count: int
    loop_duration_ms: float
