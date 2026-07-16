"""Metrics dataclasses for the PPO Trainer."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EpochMetrics:
    """Metrics aggregated over a single training epoch."""

    epoch: int
    mean_policy_loss: float
    mean_value_loss: float
    mean_entropy_loss: float
    mean_total_loss: float
    mean_approx_kl: float
    mean_clip_fraction: float
    learning_rate: float


@dataclass(slots=True)
class TrainMetrics:
    """Cumulative metrics tracking an entire training run."""

    epochs_completed: int = 0
    epoch_history: list[EpochMetrics] = field(default_factory=list)

    def add_epoch(self, metrics: EpochMetrics) -> None:
        """Append epoch results to the training history.

        Args:
            metrics: The finalized metrics for the latest epoch.
        """
        self.epoch_history.append(metrics)
        self.epochs_completed += 1
