"""Training Runner Orchestrator."""

import time

from cookie_agent.core.protocols import Policy
from cookie_agent.rl.experience import Experience
from cookie_agent.training.metrics import EpisodeMetrics
from cookie_agent.training.protocols import (
    BufferProtocol,
    EnvironmentProtocol,
    TrainerProtocol,
)


class TrainingRunner:
    """Orchestrates the environment, policy, buffer, and trainer."""

    def __init__(
        self,
        environment: EnvironmentProtocol,
        policy: Policy,
        buffer: BufferProtocol,
        trainer: TrainerProtocol,
        target_buffer_size: int,
        ppo_epochs: int,
        ppo_batch_size: int,
    ) -> None:
        """Initialize the Training Runner.

        Args:
            environment: The game environment.
            policy: The action selection policy.
            buffer: The experience collection buffer.
            trainer: The PPO update orchestrator.
            target_buffer_size: Number of experiences to collect before updating.
            ppo_epochs: Number of epochs to train the PPO algorithm per update.
            ppo_batch_size: Minibatch size for the PPO update.
        """
        self._environment = environment
        self._policy = policy
        self._buffer = buffer
        self._trainer = trainer
        self._target_buffer_size = target_buffer_size
        self._ppo_epochs = ppo_epochs
        self._ppo_batch_size = ppo_batch_size
        self._update_count = 0
        self._episode_count = 0

    def run_episode(self) -> EpisodeMetrics:
        """Run a single training episode.

        Returns:
            EpisodeMetrics containing the episode statistics.
        """
        state = self._environment.reset()

        terminated = False
        episode_reward = 0.0
        episode_length = 0
        start_time = time.perf_counter()

        self._episode_count += 1

        while not terminated:
            action = self._policy.select_action(state)
            next_state, reward_event, terminated, info = self._environment.step(action)

            # Create experience and add to buffer
            experience = Experience(
                state=state,
                action=action,
                reward=reward_event.value,
                next_state=next_state,
                terminated=terminated,
                info=info,
            )
            self._buffer.append(experience)

            episode_reward += reward_event.value
            episode_length += 1
            state = next_state

            # If buffer is ready, update the model
            if len(self._buffer) >= self._target_buffer_size:
                self._trainer.train(
                    epochs=self._ppo_epochs,
                    buffer=self._buffer,
                    batch_size=self._ppo_batch_size,
                )
                self._buffer.clear()
                self._update_count += 1

        duration = time.perf_counter() - start_time

        return EpisodeMetrics(
            episode=self._episode_count,
            episode_reward=episode_reward,
            episode_length=episode_length,
            update_count=self._update_count,
            duration_seconds=duration,
        )
