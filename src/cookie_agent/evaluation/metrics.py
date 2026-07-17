"""Evaluation metrics definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvaluationMetrics:
    """Metrics collected during model evaluation."""

    num_episodes: int
    mean_reward: float
    std_reward: float
    mean_length: float
    total_duration_seconds: float

    @classmethod
    def from_results(
        cls, rewards: list[float], lengths: list[int], duration_seconds: float
    ) -> "EvaluationMetrics":
        """Calculate statistics from raw episode results."""
        import math

        num_episodes = len(rewards)
        if num_episodes == 0:
            return cls(
                num_episodes=0,
                mean_reward=0.0,
                std_reward=0.0,
                mean_length=0.0,
                total_duration_seconds=duration_seconds,
            )

        mean_reward = sum(rewards) / num_episodes
        mean_length = sum(lengths) / num_episodes

        if num_episodes > 1:
            variance = sum((r - mean_reward) ** 2 for r in rewards) / (num_episodes - 1)
            std_reward = math.sqrt(variance)
        else:
            std_reward = 0.0

        return cls(
            num_episodes=num_episodes,
            mean_reward=mean_reward,
            std_reward=std_reward,
            mean_length=mean_length,
            total_duration_seconds=duration_seconds,
        )
