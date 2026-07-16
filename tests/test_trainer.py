"""Unit tests for the generic PPO Trainer."""

from typing import Any

from cookie_agent.rl.buffer import RolloutBuffer
from cookie_agent.rl.experience import Experience
from cookie_agent.rl.ppo import PPOAlgorithm, PPOLossResult
from cookie_agent.rl.trainer import PPOTrainer


class MockAgent:
    """Mock agent for testing trainer."""

    def __init__(self) -> None:
        """Initialize mock agent."""
        self.backward_calls: list[PPOLossResult] = []

    def evaluate_actions(
        self,
        batch: list[Experience[str, str, str]],
    ) -> tuple[list[float], list[float], list[float]]:
        """Mock evaluate actions."""
        b_len = len(batch)
        return ([0.5] * b_len, [-0.69] * b_len, [0.69] * b_len)

    def backward(self, loss_result: PPOLossResult) -> None:
        """Mock backward pass."""
        self.backward_calls.append(loss_result)


class MockOptimizer:
    """Mock optimizer for testing."""

    def __init__(self) -> None:
        """Initialize mock optimizer."""
        self.zero_grad_count = 0
        self.step_count = 0

    def zero_grad(self) -> None:
        """Mock zero grad."""
        self.zero_grad_count += 1

    def step(self) -> None:
        """Mock step."""
        self.step_count += 1


class MockScheduler:
    """Mock scheduler for testing."""

    def __init__(self) -> None:
        """Initialize mock scheduler."""
        self.step_count = 0

    def step(self) -> None:
        """Mock step."""
        self.step_count += 1

    def get_last_lr(self) -> list[float]:
        """Mock get_last_lr."""
        return [0.001]


class MockCallback:
    """Mock callback for testing."""

    def __init__(self) -> None:
        """Initialize mock callback."""
        self.events: list[str] = []

    def on_train_start(self, _trainer: Any) -> None:
        """Mock on_train_start."""
        self.events.append("train_start")

    def on_epoch_start(self, epoch: int) -> None:
        """Mock on_epoch_start."""
        self.events.append(f"epoch_start_{epoch}")

    def on_batch_start(self, batch_idx: int) -> None:
        """Mock on_batch_start."""
        self.events.append(f"batch_start_{batch_idx}")

    def on_batch_end(self, batch_idx: int, _metrics: PPOLossResult) -> None:
        """Mock on_batch_end."""
        self.events.append(f"batch_end_{batch_idx}")

    def on_epoch_end(self, epoch: int, _metrics: Any) -> None:
        """Mock on_epoch_end."""
        self.events.append(f"epoch_end_{epoch}")

    def on_train_end(self) -> None:
        """Mock on_train_end."""
        self.events.append("train_end")


def create_mock_buffer(size: int = 5) -> RolloutBuffer[str, str, str]:
    """Helper to create mock buffer."""
    buffer = RolloutBuffer[str, str, str]()
    for i in range(size):
        exp = Experience(
            state=f"S{i}",
            action="A",
            reward=1.0,
            next_state=f"S{i + 1}",
            terminated=False,
            info="I",
        )
        buffer.append(exp)
    return buffer


def test_trainer_orchestration() -> None:
    """Verify trainer correctly wires Agent, Optimizer, Scheduler, and Callbacks."""
    agent = MockAgent()
    optimizer = MockOptimizer()
    ppo = PPOAlgorithm()
    scheduler = MockScheduler()
    callback = MockCallback()

    trainer = PPOTrainer[str, str, str](
        agent=agent,
        optimizer=optimizer,
        ppo_algorithm=ppo,
        scheduler=scheduler,
        callbacks=[callback],
    )

    buffer = create_mock_buffer(size=4)
    # 4 items, batch_size=2 -> 2 batches per epoch
    metrics = trainer.train(epochs=2, buffer=buffer, batch_size=2)

    assert metrics.epochs_completed == 2
    assert len(metrics.epoch_history) == 2

    # Verify callback event sequence
    expected_events = [
        "train_start",
        "epoch_start_1",
        "batch_start_0",
        "batch_end_0",
        "batch_start_1",
        "batch_end_1",
        "epoch_end_1",
        "epoch_start_2",
        "batch_start_0",
        "batch_end_0",
        "batch_start_1",
        "batch_end_1",
        "epoch_end_2",
        "train_end",
    ]
    assert callback.events == expected_events

    # Verify optimizer step counts (2 epochs * 2 batches = 4 steps)
    assert optimizer.zero_grad_count == 4
    assert optimizer.step_count == 4

    # Verify backward passes
    assert len(agent.backward_calls) == 4

    # Verify scheduler steps (2 epochs = 2 steps)
    assert scheduler.step_count == 2

    # Verify epoch metrics structure
    epoch1_metrics = metrics.epoch_history[0]
    assert epoch1_metrics.epoch == 1
    assert epoch1_metrics.learning_rate == 0.001
    assert isinstance(epoch1_metrics.mean_policy_loss, float)
