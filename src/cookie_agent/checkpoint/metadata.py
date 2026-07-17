"""Checkpoint metadata representation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CheckpointMetadata:
    """Metadata associated with a saved model checkpoint.

    Attributes:
        episode: The training episode number.
        global_step: The total number of environment steps across all episodes.
        total_reward: The total reward accumulated in the most recent
            episode or evaluation.
        timestamp: Unix timestamp when the checkpoint was saved.
        model_version: String identifier for the model architecture version.
    """

    episode: int
    global_step: int
    total_reward: float
    timestamp: float
    model_version: str

    def to_dict(self) -> dict[str, int | float | str]:
        """Serialize metadata to a primitive dictionary."""
        return {
            "episode": self.episode,
            "global_step": self.global_step,
            "total_reward": self.total_reward,
            "timestamp": self.timestamp,
            "model_version": self.model_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int | float | str]) -> "CheckpointMetadata":
        """Deserialize metadata from a dictionary."""
        return cls(
            episode=int(data["episode"]),
            global_step=int(data["global_step"]),
            total_reward=float(data["total_reward"]),
            timestamp=float(data["timestamp"]),
            model_version=str(data["model_version"]),
        )
