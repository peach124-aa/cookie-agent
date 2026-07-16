"""Generalized Advantage Estimation for PPO."""


def compute_gae(
    rewards: list[float],
    values: list[float],
    dones: list[bool],
    gamma: float,
    lambda_: float,
) -> tuple[list[float], list[float]]:
    """Compute Generalized Advantage Estimation (GAE).

    Args:
        rewards: Sequential list of raw scalar rewards.
        values: Sequential list of state value estimates from the critic.
        dones: Sequential list of boolean episode termination flags.
        gamma: Discount factor for rewards.
        lambda_: GAE smoothing parameter.

    Returns:
        A tuple of (advantages, returns), both corresponding element-wise to the inputs.
    """
    length = len(rewards)
    advantages: list[float] = [0.0] * length
    returns: list[float] = [0.0] * length
    
    gae = 0.0
    for i in reversed(range(length)):
        if i == length - 1:
            next_value = 0.0
        else:
            next_value = values[i + 1]

        # If the current state was terminal, the next state value is 0.
        # Wait, typically 'done' applies to the transition resulting in next_value.
        # We will use dones[i] to mask out next_value.
        mask = 0.0 if dones[i] else 1.0
        
        delta = rewards[i] + gamma * next_value * mask - values[i]
        gae = delta + gamma * lambda_ * mask * gae
        
        advantages[i] = gae
        returns[i] = gae + values[i]

    return advantages, returns
