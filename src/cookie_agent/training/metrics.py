"""Metrics containers for training outcomes."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EpisodeMetrics:
    """Metrics recorded for a single training episode."""

    episode: int
    episode_reward: float
    episode_length: int
    update_count: int
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class TrainingMetrics:
    """Aggregate metrics recorded across all training episodes."""

    total_episodes: int
    total_updates: int
    total_steps: int
    best_reward: float
    average_reward: float
    total_training_time: float
