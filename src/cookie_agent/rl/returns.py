"""Cumulative reward returns calculation for PPO."""


def compute_discounted_returns(rewards: list[float], gamma: float) -> list[float]:
    """Compute the discounted cumulative returns.

    Args:
        rewards: Sequential list of raw scalar rewards.
        gamma: Discount factor (between 0.0 and 1.0).

    Returns:
        List of discounted returns, corresponding element-wise to the rewards.
    """
    returns: list[float] = [0.0] * len(rewards)
    discounted_return = 0.0

    for i in reversed(range(len(rewards))):
        discounted_return = rewards[i] + gamma * discounted_return
        returns[i] = discounted_return

    return returns
