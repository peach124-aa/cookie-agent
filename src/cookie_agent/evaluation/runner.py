"""Evaluation Runner Orchestrator."""

import time

from cookie_agent.evaluation.metrics import EvaluationMetrics
from cookie_agent.evaluation.protocols import EnvironmentProtocol, PolicyProtocol


class EvaluationRunner:
    """Orchestrates the environment and policy for model evaluation."""

    def __init__(
        self,
        environment: EnvironmentProtocol,
        policy: PolicyProtocol,
        num_episodes: int,
    ) -> None:
        """Initialize the Evaluation Runner.

        Args:
            environment: The game environment to evaluate on.
            policy: The policy to evaluate.
            num_episodes: Number of episodes to run during evaluation.
        """
        self._environment = environment
        self._policy = policy
        self._num_episodes = num_episodes

    def evaluate(self) -> EvaluationMetrics:
        """Run the evaluation over the specified number of episodes.

        Returns:
            EvaluationMetrics containing aggregated statistics.
        """
        rewards: list[float] = []
        lengths: list[int] = []

        start_time = time.perf_counter()

        for _ in range(self._num_episodes):
            state = self._environment.reset()
            terminated = False
            episode_reward = 0.0
            episode_length = 0

            while not terminated:
                action = self._policy.select_action(state)
                next_state, reward_event, terminated, _ = self._environment.step(action)

                episode_reward += reward_event.value
                episode_length += 1
                state = next_state

            rewards.append(episode_reward)
            lengths.append(episode_length)

        duration = time.perf_counter() - start_time

        return EvaluationMetrics.from_results(rewards, lengths, duration)
