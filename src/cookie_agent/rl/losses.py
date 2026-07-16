"""Loss functions for the PPO Algorithm."""

import math


def clip_ratio(log_probs: list[float], old_log_probs: list[float]) -> list[float]:
    """Calculate the probability ratio r_t(theta).

    Args:
        log_probs: Log probabilities of actions under current policy.
        old_log_probs: Log probabilities of actions under old policy.

    Returns:
        List of ratio scalars: exp(log_prob - old_log_prob).
    """
    return [
        math.exp(lp - olp) for lp, olp in zip(log_probs, old_log_probs, strict=False)
    ]


def compute_policy_loss(
    advantages: list[float],
    log_probs: list[float],
    old_log_probs: list[float],
    epsilon: float,
) -> float:
    """Compute the clipped surrogate objective for the policy.

    Args:
        advantages: List of GAE advantages.
        log_probs: Log probabilities of actions under current policy.
        old_log_probs: Log probabilities of actions under old policy.
        epsilon: PPO clipping parameter.

    Returns:
        The scalar policy loss (negative of the objective since we minimize loss).
    """
    if not advantages:
        return 0.0

    ratios = clip_ratio(log_probs, old_log_probs)

    loss_sum = 0.0
    for ratio, adv in zip(ratios, advantages, strict=False):
        surr1 = ratio * adv
        # Clip the ratio
        clipped_ratio = max(1.0 - epsilon, min(ratio, 1.0 + epsilon))
        surr2 = clipped_ratio * adv

        # We want to maximize min(surr1, surr2), so loss is negative of this
        loss_sum += -min(surr1, surr2)

    return loss_sum / len(advantages)


def compute_value_loss(values: list[float], returns: list[float]) -> float:
    """Compute Mean Squared Error (MSE) value loss.

    Args:
        values: State value estimates.
        returns: Target returns.

    Returns:
        The MSE loss scalar.
    """
    if not values:
        return 0.0

    sq_errors = [(v - r) ** 2 for v, r in zip(values, returns, strict=False)]
    return sum(sq_errors) / len(values)


def compute_entropy_bonus(entropies: list[float], c: float) -> float:
    """Compute the scaled entropy bonus to encourage exploration.

    Args:
        entropies: List of entropy scalars per step.
        c: Entropy coefficient.

    Returns:
        The scalar entropy bonus (subtracted from total loss).
    """
    if not entropies:
        return 0.0

    mean_entropy = sum(entropies) / len(entropies)
    return -(
        c * mean_entropy
    )  # Negative because we want to maximize entropy via minimization
