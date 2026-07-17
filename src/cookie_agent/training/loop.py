"""Training Loop Orchestrator."""

import time

from cookie_agent.training.exceptions import TrainingStoppedError
from cookie_agent.training.metrics import TrainingMetrics
from cookie_agent.training.runner import TrainingRunner


class TrainingLoop:
    """Orchestrates multiple episodes of training."""

    def __init__(self, runner: TrainingRunner) -> None:
        """Initialize the loop.

        Args:
            runner: The single-episode TrainingRunner.
        """
        self._runner = runner

    def run(self, total_episodes: int) -> TrainingMetrics:
        """Run the training loop for a fixed number of episodes.

        Args:
            total_episodes: Total number of episodes to train for.

        Returns:
            TrainingMetrics aggregating statistics over all episodes.
        """
        start_time = time.perf_counter()

        best_reward = float("-inf")
        total_reward = 0.0
        total_steps = 0

        for _ in range(total_episodes):
            try:
                metrics = self._runner.run_episode()
            except (KeyboardInterrupt, TrainingStoppedError):
                break

            total_steps += metrics.episode_length
            total_reward += metrics.episode_reward
            if metrics.episode_reward > best_reward:
                best_reward = metrics.episode_reward

        duration = time.perf_counter() - start_time
        avg_reward = total_reward / total_episodes if total_episodes > 0 else 0.0
        total_updates = self._runner._update_count

        return TrainingMetrics(
            total_episodes=total_episodes,
            total_updates=total_updates,
            total_steps=total_steps,
            best_reward=best_reward if best_reward != float("-inf") else 0.0,
            average_reward=avg_reward,
            total_training_time=duration,
        )
