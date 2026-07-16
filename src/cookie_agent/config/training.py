"""Training orchestration configuration."""

from dataclasses import dataclass
from cookie_agent.config.base import BaseConfig
from cookie_agent.config.validator import validate_positive, validate_non_empty

@dataclass(frozen=True, slots=True)
class TrainingConfig(BaseConfig):
    """High-level hyperparameters for training loops."""

    batch_size: int
    learning_rate: float
    num_epochs: int
    checkpoint_dir: str

    def __post_init__(self) -> None:
        """Validate properties."""
        validate_positive("batch_size", self.batch_size)
        validate_positive("learning_rate", self.learning_rate)
        validate_positive("num_epochs", self.num_epochs)
        validate_non_empty("checkpoint_dir", self.checkpoint_dir)

    @classmethod
    def default(cls) -> "TrainingConfig":
        return cls(
            batch_size=64,
            learning_rate=3e-4,
            num_epochs=10,
            checkpoint_dir="checkpoints/"
        )
