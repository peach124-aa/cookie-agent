"""PPO Training Loop Orchestrator."""

from collections.abc import Sequence

from cookie_agent.rl.buffer import RolloutBuffer
from cookie_agent.rl.ppo import PPOAlgorithm
from cookie_agent.rl.protocols import (
    AgentProtocol,
    CallbackProtocol,
    CheckpointProtocol,
    OptimizerProtocol,
    SchedulerProtocol,
)
from cookie_agent.rl.sampler import MiniBatchSampler
from cookie_agent.rl.trainer_metrics import EpochMetrics, TrainMetrics


class PPOTrainer[StateType, ActionType, InfoType]:
    """Pure Python orchestrator for Proximal Policy Optimization loops.

    Coordinates the generic mathematical RL routines with strict abstract
    protocols, avoiding any coupling to external Deep Learning frameworks.
    """

    def __init__(
        self,
        agent: AgentProtocol[StateType, ActionType, InfoType],
        optimizer: OptimizerProtocol,
        ppo_algorithm: PPOAlgorithm,
        scheduler: SchedulerProtocol | None = None,
        checkpoint: CheckpointProtocol | None = None,
        callbacks: Sequence[CallbackProtocol] | None = None,
    ) -> None:
        """Initialize the trainer.

        Args:
            agent: Evaluator for policy and value distributions.
            optimizer: Protocol for backprop stepping.
            ppo_algorithm: Computes advantages and surrogate objectives.
            scheduler: Optional learning rate decay manager.
            checkpoint: Optional serializer.
            callbacks: Lifecycle hook handlers.
        """
        self._agent = agent
        self._optimizer = optimizer
        self._ppo = ppo_algorithm
        self._scheduler = scheduler
        self._checkpoint = checkpoint
        self._callbacks = callbacks or []

    def train(
        self,
        epochs: int,
        buffer: RolloutBuffer[StateType, ActionType, InfoType],
        batch_size: int,
    ) -> TrainMetrics:
        """Execute the training loop over the rollout buffer.

        Args:
            epochs: Number of times to iterate over the buffer.
            buffer: The collected experiences.
            batch_size: The chunk size for backpropagation.

        Returns:
            The complete history of training metrics.
        """
        train_metrics = TrainMetrics()

        for callback in self._callbacks:
            callback.on_train_start(self)

        for epoch in range(1, epochs + 1):
            for callback in self._callbacks:
                callback.on_epoch_start(epoch)

            epoch_metrics = self.train_epoch(epoch, buffer, batch_size)
            train_metrics.add_epoch(epoch_metrics)

            if self._scheduler:
                self._scheduler.step()

            for callback in self._callbacks:
                callback.on_epoch_end(epoch, epoch_metrics)

        for callback in self._callbacks:
            callback.on_train_end()

        return train_metrics

    def train_epoch(
        self,
        epoch: int,
        buffer: RolloutBuffer[StateType, ActionType, InfoType],
        batch_size: int,
    ) -> EpochMetrics:
        """Run a single optimization pass over the entire buffer.

        Args:
            epoch: The current epoch index.
            buffer: The collected experiences.
            batch_size: Number of records per optimization step.

        Returns:
            Aggregated metric averages for the epoch.
        """
        # Unroll raw fields for GAE
        rewards = [exp.reward for exp in buffer]
        dones = [exp.terminated for exp in buffer]

        # Fetch baseline values for the entire buffer
        # This allows computing accurate temporal differences
        values, old_log_probs, _ = self._agent.evaluate_actions(list(buffer))

        # Compute advantages exactly once per epoch
        advantages, returns = self._ppo.compute_advantages(
            rewards=rewards,
            values=values,
            dones=dones,
        )

        sampler = MiniBatchSampler(buffer, batch_size)

        metrics_sum = {
            "policy_loss": 0.0,
            "value_loss": 0.0,
            "entropy_loss": 0.0,
            "total_loss": 0.0,
            "approx_kl": 0.0,
            "clip_fraction": 0.0,
        }
        batches_processed = 0

        # We must align the pre-computed advantages/returns to the sampled batches.
        # Since MiniBatchSampler currently yields chunks sequentially and
        # deterministically without shuffling, we can safely slice the advantages
        # array based on batch indexing.
        cursor = 0

        for batch_idx, batch in enumerate(sampler):
            for callback in self._callbacks:
                callback.on_batch_start(batch_idx)

            b_len = len(batch)
            b_adv = advantages[cursor : cursor + b_len]
            b_ret = returns[cursor : cursor + b_len]
            b_old_lp = old_log_probs[cursor : cursor + b_len]
            cursor += b_len

            # Evaluate new policy
            b_val, b_lp, b_ent = self._agent.evaluate_actions(batch)

            # Compute surrogate objectives
            loss_result = self._ppo.compute_losses(
                advantages=b_adv,
                returns=b_ret,
                values=b_val,
                log_probs=b_lp,
                old_log_probs=b_old_lp,
                entropies=b_ent,
            )

            # Optimization Step
            self._optimizer.zero_grad()
            self._agent.backward(loss_result)
            self._optimizer.step()

            # Aggregate Metrics
            metrics_sum["policy_loss"] += loss_result.policy_loss
            metrics_sum["value_loss"] += loss_result.value_loss
            metrics_sum["entropy_loss"] += loss_result.entropy_loss
            metrics_sum["total_loss"] += loss_result.total_loss
            metrics_sum["approx_kl"] += loss_result.approx_kl
            metrics_sum["clip_fraction"] += loss_result.clip_fraction
            batches_processed += 1

            for callback in self._callbacks:
                callback.on_batch_end(batch_idx, loss_result)

        if batches_processed == 0:
            batches_processed = 1  # prevent division by zero for empty buffers

        lr = 0.0
        if self._scheduler:
            lr_list = self._scheduler.get_last_lr()
            if lr_list:
                lr = lr_list[0]

        return EpochMetrics(
            epoch=epoch,
            mean_policy_loss=metrics_sum["policy_loss"] / batches_processed,
            mean_value_loss=metrics_sum["value_loss"] / batches_processed,
            mean_entropy_loss=metrics_sum["entropy_loss"] / batches_processed,
            mean_total_loss=metrics_sum["total_loss"] / batches_processed,
            mean_approx_kl=metrics_sum["approx_kl"] / batches_processed,
            mean_clip_fraction=metrics_sum["clip_fraction"] / batches_processed,
            learning_rate=lr,
        )
